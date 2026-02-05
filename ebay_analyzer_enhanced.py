import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import csv
import os
import threading
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import statistics
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sqlite3
import json
import logging
import time
from typing import List, Dict, Tuple, Optional

# Setup logging
logging.basicConfig(
    filename='ebay_analyzer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global variables
last_results = []
config = {}


def load_config():
    """Load configuration from config.json or create default"""
    global config
    default_config = {
        "default_exclude_keywords": ["lot of", "broken", "for parts", "as-is", "not working"],
        "default_max_pages": 3,
        "alert_threshold": 0.85,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "favorite_searches": [],
        "max_retries": 3,
        "min_price": 5,
        "max_price": 10000,
        "dark_mode": False,
        "last_export_dir": "",
        "window_geometry": "1200x700"
    }
    
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                # Add any missing keys from default
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        else:
            config = default_config
            save_config()
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        config = default_config
    
    return config


def save_config():
    """Save configuration to config.json"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, indent=2, fp=f)
    except Exception as e:
        logging.error(f"Error saving config: {e}")


def init_database():
    """Initialize SQLite database for storing results"""
    conn = sqlite3.connect('ebay_data.db')
    cursor = conn.cursor()
    
    # Table for individual items
    cursor.execute('''CREATE TABLE IF NOT EXISTS items
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      price REAL NOT NULL,
                      shipping REAL DEFAULT 0,
                      total_cost REAL,
                      condition TEXT,
                      sale_date TEXT,
                      query TEXT NOT NULL,
                      scrape_date TEXT NOT NULL,
                      url TEXT)''')
    
    # Table for search summaries
    cursor.execute('''CREATE TABLE IF NOT EXISTS searches
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT NOT NULL,
                      query TEXT NOT NULL,
                      item_count INTEGER,
                      average_price REAL,
                      median_price REAL,
                      min_price REAL,
                      max_price REAL)''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized")


def validate_query(query: str) -> bool:
    """Validate search query"""
    if not query or len(query.strip()) < 3:
        raise ValueError("Query must be at least 3 characters long")
    if re.search(r'[<>]', query):
        raise ValueError("Query contains invalid characters")
    return True


def scrape_ebay_sold_items(query: str, max_pages: int = None) -> List[Dict]:
    """
    Scrape eBay sold items with pagination and enhanced data extraction
    
    Returns list of dicts with: title, price, shipping, total_cost, condition, sale_date, url
    """
    if max_pages is None:
        max_pages = config.get('default_max_pages', 3)
    
    all_results = []
    headers = {"User-Agent": config.get('user_agent', 'Mozilla/5.0')}
    
    for page in range(1, max_pages + 1):
        try:
            url = "https://www.ebay.com/sch/i.html"
            params = {
                "_nkw": query,
                "_sop": "13",  # Sort by newest
                "_ipg": "50",  # Items per page
                "_pgn": page,  # Page number
                "LH_Complete": "1",
                "LH_Sold": "1"
            }
            
            logging.info(f"Scraping page {page} for query: {query}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select(".s-item")
            
            if not items or len(items) <= 1:  # eBay returns 1 item as header
                logging.info(f"No more items found on page {page}")
                break
            
            for item in items:
                try:
                    title_elem = item.select_one(".s-item__title")
                    price_elem = item.select_one(".s-item__price")
                    
                    if not title_elem or not price_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Skip header items
                    if "Shop on eBay" in title or title == "":
                        continue
                    
                    # Extract price
                    price_text = price_elem.text.strip()
                    price_match = re.search(r"\$([\d,.]+)", price_text)
                    if not price_match:
                        continue
                    
                    price = float(price_match.group(1).replace(",", ""))
                    
                    # Extract shipping cost
                    shipping = 0.0
                    shipping_elem = item.select_one(".s-item__shipping")
                    if shipping_elem:
                        shipping_text = shipping_elem.text.strip()
                        if "Free" not in shipping_text:
                            shipping_match = re.search(r"\$([\d,.]+)", shipping_text)
                            if shipping_match:
                                shipping = float(shipping_match.group(1).replace(",", ""))
                    
                    total_cost = price + shipping
                    
                    # Extract sale date
                    sale_date = None
                    date_elem = item.select_one(".s-item__title--tagblock .POSITIVE")
                    if date_elem:
                        date_text = date_elem.text.strip()
                        # Try to parse date (eBay format: "Sold  Feb 3, 2026")
                        date_match = re.search(r'Sold\s+(\w+\s+\d+,\s+\d{4})', date_text)
                        if date_match:
                            try:
                                sale_date = datetime.strptime(date_match.group(1), "%b %d, %Y").strftime("%Y-%m-%d")
                            except:
                                pass
                    
                    # Extract condition
                    condition = "Unknown"
                    condition_elem = item.select_one(".SECONDARY_INFO")
                    if condition_elem:
                        condition = condition_elem.text.strip()
                    
                    # Extract URL
                    url_elem = item.select_one(".s-item__link")
                    item_url = url_elem.get('href', '') if url_elem else ''
                    
                    all_results.append({
                        'title': title,
                        'price': price,
                        'shipping': shipping,
                        'total_cost': total_cost,
                        'condition': condition,
                        'sale_date': sale_date,
                        'url': item_url
                    })
                    
                except Exception as e:
                    logging.warning(f"Error parsing item: {e}")
                    continue
            
            # Be nice to eBay's servers
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {page}: {e}")
            break
        except Exception as e:
            logging.error(f"Unexpected error on page {page}: {e}")
            break
    
    logging.info(f"Scraped {len(all_results)} items for query: {query}")
    return all_results


def scrape_with_retry(query: str, max_pages: int = None, max_retries: int = None) -> List[Dict]:
    """Scrape with retry logic and exponential backoff"""
    if max_retries is None:
        max_retries = config.get('max_retries', 3)
    
    for attempt in range(max_retries):
        try:
            return scrape_ebay_sold_items(query, max_pages)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed after {max_retries} attempts: {e}")
                raise
            wait_time = 2 ** attempt
            logging.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    return []


def clean_results(results: List[Dict], exclude_keywords: List[str] = None, 
                  min_price: float = None, max_price: float = None) -> List[Dict]:
    """Filter results based on keywords and price range"""
    if exclude_keywords is None:
        exclude_keywords = config.get('default_exclude_keywords', [])
    if min_price is None:
        min_price = config.get('min_price', 5)
    if max_price is None:
        max_price = config.get('max_price', 10000)
    
    filtered = []
    for item in results:
        title = item['title'].lower()
        price = item['total_cost']
        
        # Check exclude keywords
        if any(kw.lower() in title for kw in exclude_keywords):
            continue
        
        # Check price range
        if price < min_price or price > max_price:
            continue
        
        filtered.append(item)
    
    logging.info(f"Filtered {len(results)} items to {len(filtered)} items")
    return filtered


def save_to_database(query: str, results: List[Dict]):
    """Save search results to database"""
    if not results:
        return
    
    conn = sqlite3.connect('ebay_data.db')
    cursor = conn.cursor()
    scrape_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save individual items
    for item in results:
        cursor.execute('''INSERT INTO items 
                         (title, price, shipping, total_cost, condition, sale_date, query, scrape_date, url)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (item['title'], item['price'], item['shipping'], item['total_cost'],
                       item['condition'], item['sale_date'], query, scrape_date, item['url']))
    
    # Save search summary
    prices = [item['total_cost'] for item in results]
    cursor.execute('''INSERT INTO searches 
                     (timestamp, query, item_count, average_price, median_price, min_price, max_price)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (scrape_date, query, len(results), 
                   statistics.mean(prices), statistics.median(prices),
                   min(prices), max(prices)))
    
    conn.commit()
    conn.close()
    logging.info(f"Saved {len(results)} items to database")


def export_results_to_csv(results: List[Dict]):
    """Export results to CSV with enhanced data"""
    if not results:
        messagebox.showwarning("No Results", "Nothing to export.")
        return
    
    initial_dir = config.get('last_export_dir', '')
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        initialdir=initial_dir
    )
    
    if not file_path:
        return
    
    # Save export directory
    config['last_export_dir'] = os.path.dirname(file_path)
    save_config()
    
    try:
        with open(file_path, "w", newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Price', 'Shipping', 'Total Cost', 'Condition', 'Sale Date', 'URL']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in results:
                writer.writerow({
                    'Title': item['title'],
                    'Price': f"${item['price']:.2f}",
                    'Shipping': f"${item['shipping']:.2f}",
                    'Total Cost': f"${item['total_cost']:.2f}",
                    'Condition': item['condition'],
                    'Sale Date': item['sale_date'] or 'Unknown',
                    'URL': item['url']
                })
        
        messagebox.showinfo("Export Complete", f"Results exported to:\n{file_path}")
        logging.info(f"Exported results to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export: {e}")
        logging.error(f"Export error: {e}")


def plot_comprehensive_analysis(results: List[Dict]):
    """Create comprehensive visualization with multiple charts"""
    if not results:
        messagebox.showwarning("No Data", "No data to plot.")
        return
    
    prices = [item['total_cost'] for item in results]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Box plot showing quartiles and outliers
    ax1.boxplot(prices, vert=True)
    ax1.set_ylabel("Price (USD)")
    ax1.set_title("Price Distribution (Box Plot)")
    ax1.grid(True, alpha=0.3)
    
    # Add statistics text
    q1, median, q3 = np.percentile(prices, [25, 50, 75])
    ax1.text(1.15, median, f'Median: ${median:.2f}', fontsize=9)
    ax1.text(1.15, q1, f'Q1: ${q1:.2f}', fontsize=9)
    ax1.text(1.15, q3, f'Q3: ${q3:.2f}', fontsize=9)
    
    # 2. Histogram with median line
    ax2.hist(prices, bins=20, edgecolor='black', alpha=0.7, color='skyblue')
    ax2.axvline(median, color='red', linestyle='--', linewidth=2, label=f'Median: ${median:.2f}')
    ax2.set_xlabel("Price (USD)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Price Frequency Distribution")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Condition breakdown (if available)
    conditions = {}
    for item in results:
        cond = item['condition']
        conditions[cond] = conditions.get(cond, 0) + 1
    
    if len(conditions) > 1:
        ax3.pie(conditions.values(), labels=conditions.keys(), autopct='%1.1f%%', startangle=90)
        ax3.set_title("Items by Condition")
    else:
        ax3.text(0.5, 0.5, 'Condition data\nnot available', 
                ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title("Items by Condition")
    
    # 4. Price vs Shipping scatter
    item_prices = [item['price'] for item in results]
    shipping_costs = [item['shipping'] for item in results]
    ax4.scatter(item_prices, shipping_costs, alpha=0.6, color='green')
    ax4.set_xlabel("Item Price (USD)")
    ax4.set_ylabel("Shipping Cost (USD)")
    ax4.set_title("Item Price vs Shipping Cost")
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Display in window
    win = tk.Toplevel()
    win.title("Comprehensive Analysis")
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def suggest_buy_sell_price(results: List[Dict]) -> Dict:
    """Provide intelligent buy/sell price recommendations"""
    if not results:
        messagebox.showwarning("No Data", "No data available.")
        return {}
    
    prices = sorted([item['total_cost'] for item in results])
    
    # Remove outliers (top and bottom 10%)
    trim_count = max(1, len(prices) // 10)
    trimmed = prices[trim_count:-trim_count] if len(prices) > 20 else prices
    
    q1 = np.percentile(trimmed, 25)
    median = np.median(trimmed)
    q3 = np.percentile(trimmed, 75)
    mean = statistics.mean(trimmed)
    
    try:
        mode = statistics.mode(prices)
    except:
        mode = "Multiple modes"
    
    recommendation = {
        "buy_below": q1,
        "market_price": median,
        "sell_above": q3,
        "mean": mean,
        "mode": mode,
        "sample_size": len(results)
    }
    
    message = f"""Price Recommendations (based on {len(results)} items):

📉 BUY BELOW: ${q1:.2f} (25th percentile - good deal)
💰 MARKET PRICE: ${median:.2f} (median - fair price)
📈 SELL ABOVE: ${q3:.2f} (75th percentile - premium)

Statistics:
• Mean: ${mean:.2f}
• Mode: {mode if isinstance(mode, str) else f'${mode:.2f}'}
• Sample Size: {len(results)} items
• Price Range: ${min(prices):.2f} - ${max(prices):.2f}
"""
    
    messagebox.showinfo("Smart Price Recommendation", message)
    return recommendation


def compare_historical_searches(query: str):
    """Show price trends over time for a specific query"""
    conn = sqlite3.connect('ebay_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT timestamp, average_price, median_price, item_count
                     FROM searches
                     WHERE query = ?
                     ORDER BY timestamp''', (query,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) < 2:
        messagebox.showinfo("Insufficient Data", 
                          f"Need at least 2 searches for '{query}' to show trends.\nCurrent searches: {len(rows)}")
        return
    
    timestamps = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in rows]
    avg_prices = [row[1] for row in rows]
    median_prices = [row[2] for row in rows]
    item_counts = [row[3] for row in rows]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Price trends
    ax1.plot(timestamps, avg_prices, 'b-o', label='Average Price', linewidth=2)
    ax1.plot(timestamps, median_prices, 'r--s', label='Median Price', linewidth=2)
    ax1.set_ylabel("Price (USD)")
    ax1.set_title(f"Price Trends for '{query}' Over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Item count trends
    ax2.bar(timestamps, item_counts, color='green', alpha=0.7)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Items Found")
    ax2.set_title("Number of Items Found Over Time")
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    win = tk.Toplevel()
    win.title(f"Historical Trends: {query}")
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def forecast_price_trend(results: List[Dict]):
    """Forecast future prices using polynomial regression with actual dates"""
    if not results or len(results) < 3:
        messagebox.showwarning("Insufficient Data", "Need at least 3 data points to forecast.")
        return
    
    # Try to use actual sale dates if available
    dated_items = [item for item in results if item.get('sale_date')]
    
    if len(dated_items) >= 3:
        # Sort by date
        dated_items.sort(key=lambda x: x['sale_date'])
        
        # Convert dates to numeric (days since first date)
        first_date = datetime.strptime(dated_items[0]['sale_date'], "%Y-%m-%d")
        x_vals = []
        y_vals = []
        
        for item in dated_items:
            item_date = datetime.strptime(item['sale_date'], "%Y-%m-%d")
            days_diff = (item_date - first_date).days
            x_vals.append(days_diff)
            y_vals.append(item['total_cost'])
        
        x = np.array(x_vals).reshape(-1, 1)
        y = np.array(y_vals)
        
        xlabel = "Days Since First Sale"
        title = "Price Forecast (Based on Sale Dates)"
    else:
        # Fallback to index-based
        y = np.array([item['total_cost'] for item in results])
        x = np.arange(len(y)).reshape(-1, 1)
        xlabel = "Item Index"
        title = "Price Forecast (Index-based)"
    
    # Polynomial regression
    poly = PolynomialFeatures(degree=2)
    x_poly = poly.fit_transform(x)
    model = LinearRegression()
    model.fit(x_poly, y)
    
    # Predict future
    forecast_points = 10
    x_future = np.arange(len(x) + forecast_points).reshape(-1, 1)
    x_future_poly = poly.transform(x_future)
    y_pred = model.predict(x_future_poly)
    
    # Calculate trend
    trend = "stable"
    if y_pred[-1] > y_pred[len(x)-1] * 1.05:
        trend = "rising"
    elif y_pred[-1] < y_pred[len(x)-1] * 0.95:
        trend = "falling"
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y, color='blue', s=50, alpha=0.6, label='Actual Data')
    ax.plot(x_future, y_pred, 'r--', linewidth=2, label='Forecast')
    ax.axvline(x=len(x)-1, color='gray', linestyle=':', label='Forecast Start')
    ax.set_title(f"{title}\nTrend: {trend.upper()}")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Price (USD)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    win = tk.Toplevel()
    win.title("Price Forecast")
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def alert_below_avg(results: List[Dict]):
    """Find items priced below threshold"""
    if not results:
        messagebox.showinfo("No Results", "No results to evaluate for deals.")
        return
    
    prices = [item['total_cost'] for item in results]
    avg_price = sum(prices) / len(prices)
    threshold = avg_price * config.get('alert_threshold', 0.85)
    
    deals = [item for item in results if item['total_cost'] < threshold]
    
    if not deals:
        messagebox.showinfo("No Alerts", 
                          f"No items found below {config.get('alert_threshold', 0.85)*100:.0f}% of average price (${avg_price:.2f}).")
        return
    
    alert_text = f"🔔 DEALS FOUND! 🔔\n\n"
    alert_text += f"Items below {config.get('alert_threshold', 0.85)*100:.0f}% of average (${avg_price:.2f}):\n"
    alert_text += f"Found {len(deals)} deals out of {len(results)} items\n\n"
    
    # Sort by price
    deals.sort(key=lambda x: x['total_cost'])
    
    for item in deals[:10]:  # Show top 10 deals
        savings = avg_price - item['total_cost']
        savings_pct = (savings / avg_price) * 100
        alert_text += f"💰 ${item['total_cost']:.2f} (Save ${savings:.2f} / {savings_pct:.0f}%)\n"
        alert_text += f"   {item['title'][:80]}\n"
        alert_text += f"   Condition: {item['condition']}\n\n"
    
    if len(deals) > 10:
        alert_text += f"\n... and {len(deals) - 10} more deals!"
    
    # Create scrollable window for deals
    win = tk.Toplevel()
    win.title("Price Alerts - Best Deals")
    win.geometry("700x500")
    
    text = scrolledtext.ScrolledText(win, wrap=tk.WORD, width=80, height=25)
    text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    text.insert(tk.END, alert_text)
    text.config(state=tk.DISABLED)


def compare_models(queries: List[str], text_widget, progress_var):
    """Compare multiple models side-by-side"""
    comparison_data = {}
    total = len(queries)
    
    for idx, query in enumerate(queries):
        try:
            progress_var.set((idx / total) * 100)
            results = scrape_with_retry(query, max_pages=2)
            results = clean_results(results)
            
            if results:
                prices = [item['total_cost'] for item in results]
                comparison_data[query] = {
                    'count': len(results),
                    'avg': statistics.mean(prices),
                    'median': statistics.median(prices),
                    'min': min(prices),
                    'max': max(prices)
                }
        except Exception as e:
            logging.error(f"Error comparing {query}: {e}")
            comparison_data[query] = None
    
    progress_var.set(100)
    
    # Display comparison
    output = "="*80 + "\n"
    output += "MODEL COMPARISON\n"
    output += "="*80 + "\n\n"
    output += f"{'Model':<40} {'Avg Price':<12} {'Median':<12} {'Count':<8}\n"
    output += "-"*80 + "\n"
    
    for query, data in comparison_data.items():
        if data:
            output += f"{query[:40]:<40} ${data['avg']:<11.2f} ${data['median']:<11.2f} {data['count']:<8}\n"
        else:
            output += f"{query[:40]:<40} {'ERROR':<12} {'ERROR':<12} {'0':<8}\n"
    
    output += "="*80 + "\n"
    
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, output)
    
    # Create visualization
    if any(comparison_data.values()):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        models = list(comparison_data.keys())
        avgs = [comparison_data[m]['avg'] if comparison_data[m] else 0 for m in models]
        counts = [comparison_data[m]['count'] if comparison_data[m] else 0 for m in models]
        
        # Average price comparison
        ax1.barh(models, avgs, color='skyblue')
        ax1.set_xlabel("Average Price (USD)")
        ax1.set_title("Average Price Comparison")
        ax1.grid(True, alpha=0.3)
        
        # Sample size comparison
        ax2.barh(models, counts, color='lightgreen')
        ax2.set_xlabel("Number of Items Found")
        ax2.set_title("Sample Size Comparison")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        win = tk.Toplevel()
        win.title("Model Comparison")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def run_search(query: str, text_widget, progress_var=None):
    """Main search function with enhanced features"""
    global last_results
    
    try:
        # Validate query
        validate_query(query)
        
        if progress_var:
            progress_var.set(10)
        
        # Scrape with retry
        results = scrape_with_retry(query)
        
        if progress_var:
            progress_var.set(50)
        
        # Clean results
        results = clean_results(results)
        last_results = results
        
        if progress_var:
            progress_var.set(75)
        
        # Save to database
        save_to_database(query, results)
        
        if progress_var:
            progress_var.set(90)
        
        # Display results
        if not results:
            output = "No results found after filtering."
        else:
            prices = [item['total_cost'] for item in results]
            avg_price = statistics.mean(prices)
            median_price = statistics.median(prices)
            
            output = "="*80 + "\n"
            output += f"SEARCH RESULTS FOR: {query}\n"
            output += "="*80 + "\n"
            output += f"Found {len(results)} items\n"
            output += f"Average Total Cost: ${avg_price:.2f}\n"
            output += f"Median Total Cost: ${median_price:.2f}\n"
            output += f"Price Range: ${min(prices):.2f} - ${max(prices):.2f}\n"
            output += "="*80 + "\n\n"
            
            for item in results[:50]:  # Show first 50
                output += f"💰 ${item['total_cost']:.2f} (${item['price']:.2f} + ${item['shipping']:.2f} ship)\n"
                output += f"   {item['title']}\n"
                output += f"   Condition: {item['condition']} | "
                output += f"Sold: {item['sale_date'] or 'Unknown'}\n\n"
            
            if len(results) > 50:
                output += f"\n... and {len(results) - 50} more items (use Export to see all)"
        
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, output)
        
        if progress_var:
            progress_var.set(100)
        
        logging.info(f"Search completed for: {query}")
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        messagebox.showerror("Search Error", error_msg)
        logging.error(f"Search error for '{query}': {e}")
        if progress_var:
            progress_var.set(0)


def on_search(entry, text_widget, progress_var):
    """Handle search button click"""
    query = entry.get().strip()
    if not query:
        messagebox.showwarning("Missing Input", "Please enter a search term.")
        return
    
    # Run in thread to keep UI responsive
    thread = threading.Thread(target=run_search, args=(query, text_widget, progress_var))
    thread.daemon = True
    thread.start()


def on_batch_import(text_widget, progress_var):
    """Import and search multiple queries from file"""
    file_path = filedialog.askopenfilename(filetypes=[("Text/CSV Files", "*.txt *.csv")])
    if not file_path:
        return
    
    queries = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(".csv"):
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():
                        queries.append(row[0].strip())
            else:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        queries.append(line)
    except Exception as e:
        messagebox.showerror("File Error", f"Error reading file: {e}")
        return
    
    if not queries:
        messagebox.showwarning("No Queries", "No valid queries found in file.")
        return
    
    # Ask if they want comparison or individual searches
    response = messagebox.askyesno("Batch Mode", 
                                   f"Found {len(queries)} queries.\n\n"
                                   "YES = Compare models side-by-side\n"
                                   "NO = Search individually")
    
    if response:
        # Compare mode
        thread = threading.Thread(target=compare_models, args=(queries, text_widget, progress_var))
        thread.daemon = True
        thread.start()
    else:
        # Individual search mode
        def search_all():
            for idx, query in enumerate(queries):
                progress_var.set((idx / len(queries)) * 100)
                run_search(query, text_widget)
                time.sleep(2)  # Delay between searches
            progress_var.set(100)
            messagebox.showinfo("Batch Complete", f"Completed {len(queries)} searches.")
        
        thread = threading.Thread(target=search_all)
        thread.daemon = True
        thread.start()


def copy_to_clipboard(text_widget):
    """Copy results to clipboard"""
    try:
        text = text_widget.get("1.0", tk.END)
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("Copied", "Results copied to clipboard!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy: {e}")


def toggle_dark_mode(root):
    """Toggle between light and dark mode"""
    config['dark_mode'] = not config.get('dark_mode', False)
    save_config()
    
    if config['dark_mode']:
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        messagebox.showinfo("Dark Mode", "Dark mode enabled! Restart app to apply.")
    else:
        bg_color = '#ffffff'
        fg_color = '#000000'
        messagebox.showinfo("Light Mode", "Light mode enabled! Restart app to apply.")


def open_settings():
    """Open settings window"""
    settings_win = tk.Toplevel()
    settings_win.title("Settings")
    settings_win.geometry("500x600")
    
    # Create notebook for tabs
    notebook = ttk.Notebook(settings_win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Scraping Settings Tab
    scraping_frame = ttk.Frame(notebook)
    notebook.add(scraping_frame, text="Scraping")
    
    ttk.Label(scraping_frame, text="Max Pages to Scrape:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
    max_pages_var = tk.IntVar(value=config.get('default_max_pages', 3))
    ttk.Spinbox(scraping_frame, from_=1, to=10, textvariable=max_pages_var, width=10).grid(row=0, column=1, padx=10, pady=5)
    
    ttk.Label(scraping_frame, text="Max Retries:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
    max_retries_var = tk.IntVar(value=config.get('max_retries', 3))
    ttk.Spinbox(scraping_frame, from_=1, to=5, textvariable=max_retries_var, width=10).grid(row=1, column=1, padx=10, pady=5)
    
    # Filter Settings Tab
    filter_frame = ttk.Frame(notebook)
    notebook.add(filter_frame, text="Filters")
    
    ttk.Label(filter_frame, text="Minimum Price ($):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
    min_price_var = tk.DoubleVar(value=config.get('min_price', 5))
    ttk.Entry(filter_frame, textvariable=min_price_var, width=15).grid(row=0, column=1, padx=10, pady=5)
    
    ttk.Label(filter_frame, text="Maximum Price ($):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
    max_price_var = tk.DoubleVar(value=config.get('max_price', 10000))
    ttk.Entry(filter_frame, textvariable=max_price_var, width=15).grid(row=1, column=1, padx=10, pady=5)
    
    ttk.Label(filter_frame, text="Exclude Keywords (comma-separated):").grid(row=2, column=0, sticky='nw', padx=10, pady=5)
    exclude_text = tk.Text(filter_frame, width=30, height=5)
    exclude_text.grid(row=2, column=1, padx=10, pady=5)
    exclude_text.insert('1.0', ', '.join(config.get('default_exclude_keywords', [])))
    
    ttk.Label(filter_frame, text="Alert Threshold (0.0-1.0):").grid(row=3, column=0, sticky='w', padx=10, pady=5)
    alert_var = tk.DoubleVar(value=config.get('alert_threshold', 0.85))
    ttk.Entry(filter_frame, textvariable=alert_var, width=15).grid(row=3, column=1, padx=10, pady=5)
    
    # Appearance Tab
    appearance_frame = ttk.Frame(notebook)
    notebook.add(appearance_frame, text="Appearance")
    
    dark_mode_var = tk.BooleanVar(value=config.get('dark_mode', False))
    ttk.Checkbutton(appearance_frame, text="Dark Mode (requires restart)", 
                   variable=dark_mode_var).grid(row=0, column=0, sticky='w', padx=10, pady=5)
    
    # Save button
    def save_settings():
        config['default_max_pages'] = max_pages_var.get()
        config['max_retries'] = max_retries_var.get()
        config['min_price'] = min_price_var.get()
        config['max_price'] = max_price_var.get()
        config['alert_threshold'] = alert_var.get()
        config['dark_mode'] = dark_mode_var.get()
        
        # Parse exclude keywords
        exclude_text_content = exclude_text.get('1.0', tk.END).strip()
        config['default_exclude_keywords'] = [kw.strip() for kw in exclude_text_content.split(',') if kw.strip()]
        
        save_config()
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        settings_win.destroy()
    
    ttk.Button(settings_win, text="Save Settings", command=save_settings).pack(pady=10)


def build_gui():
    """Build the main GUI"""
    global root
    root = tk.Tk()
    root.title("eBay Sold Price Analyzer - Enhanced Edition")
    
    # Load config and set geometry
    geometry = config.get('window_geometry', '1200x700')
    root.geometry(geometry)
    
    # Apply dark mode if enabled
    if config.get('dark_mode', False):
        style = ttk.Style()
        style.theme_use('clam')
        # Note: Full dark mode styling would require more extensive theming
    
    # Menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Settings", command=open_settings)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    
    tools_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Tools", menu=tools_menu)
    tools_menu.add_command(label="View Database", command=lambda: messagebox.showinfo("Info", "Database viewer coming soon!"))
    tools_menu.add_command(label="Clear History", command=lambda: messagebox.showinfo("Info", "Clear history coming soon!"))
    
    # Main container
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Top section - Search
    search_frame = ttk.LabelFrame(main_frame, text="Search", padding=10)
    search_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(search_frame, text="Enter Product Name:").grid(row=0, column=0, sticky='w', padx=5)
    entry = ttk.Entry(search_frame, width=60)
    entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    
    # Favorite searches
    favorites = config.get('favorite_searches', [])
    if favorites:
        ttk.Label(search_frame, text="Quick Searches:").grid(row=1, column=0, sticky='w', padx=5)
        fav_frame = ttk.Frame(search_frame)
        fav_frame.grid(row=1, column=1, sticky='w', padx=5)
        for fav in favorites[:5]:  # Show first 5
            btn = ttk.Button(fav_frame, text=fav, 
                           command=lambda f=fav: (entry.delete(0, tk.END), entry.insert(0, f)))
            btn.pack(side=tk.LEFT, padx=2)
    
    search_frame.columnconfigure(1, weight=1)
    
    # Progress bar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, pady=(0, 10))
    
    # Results area
    results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
    results_frame.pack(fill=tk.BOTH, expand=True)
    
    result_box = scrolledtext.ScrolledText(results_frame, width=100, height=20, wrap=tk.WORD)
    result_box.pack(fill=tk.BOTH, expand=True)
    
    # Button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Row 1 buttons
    btn_row1 = ttk.Frame(button_frame)
    btn_row1.pack(fill=tk.X, pady=2)
    
    ttk.Button(btn_row1, text="🔍 Search", 
              command=lambda: on_search(entry, result_box, progress_var)).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_row1, text="📁 Batch Import", 
              command=lambda: on_batch_import(result_box, progress_var)).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_row1, text="💾 Export CSV", 
              command=lambda: export_results_to_csv(last_results)).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_row1, text="📊 Plot Analysis", 
              command=lambda: plot_comprehensive_analysis(last_results)).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_row1, text="📋 Copy", 
              command=lambda: copy_to_clipboard(result_box)).pack(side=tk.LEFT, padx=2)
    
    # Row 2 buttons
    btn_row2 = ttk.Frame(button_frame)
    btn_row2.pack(fill=tk.X, pady=2)
    
    ttk.Button(btn_row2, text="💡 Price Recommendation", 
              command=lambda: suggest_buy_sell_price(last_results)).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_row2, text="📈 Forecast", 
              command=lambda: forecast_price_trend(last_results)).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_row2, text="🔔 Deal Alerts", 
              command=lambda: alert_below_avg(last_results)).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_row2, text="📉 Historical Trends", 
              command=lambda: compare_historical_searches(entry.get().strip())).pack(side=tk.LEFT, padx=2)
    
    # Bind Enter key to search
    entry.bind('<Return>', lambda e: on_search(entry, result_box, progress_var))
    
    # Save window geometry on close
    def on_closing():
        config['window_geometry'] = root.geometry()
        save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Status bar
    status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    root.mainloop()


if __name__ == "__main__":
    # Initialize
    load_config()
    init_database()
    
    logging.info("="*50)
    logging.info("Application started")
    logging.info("="*50)
    
    # Build and run GUI
    build_gui()
