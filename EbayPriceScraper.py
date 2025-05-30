import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import os
import threading
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import statistics
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

last_results = []


def scrape_ebay_sold_items(query):
    url = "https://www.ebay.com/sch/i.html"
    params = {
        "_nkw": query,
        "_sop": "13",
        "_ipg": "50",
        "LH_Complete": "1",
        "LH_Sold": "1"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    items = soup.select(".s-item")

    for item in items:
        title_elem = item.select_one(".s-item__title")
        price_elem = item.select_one(".s-item__price")

        if title_elem and price_elem and "Shop on eBay" not in title_elem.text:
            title = title_elem.text.strip()
            price_text = price_elem.text.strip()
            match = re.search(r"\$([\d,.]+)", price_text)
            if match:
                price = float(match.group(1).replace(",", ""))
                results.append((title, price))

    return results


def log_search_to_history(query, results):
    filename = "search_history.csv"
    fieldnames = ["timestamp", "query", "item_count", "average_price"]
    avg_price = sum(p for _, p in results) / len(results) if results else 0

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "item_count": len(results),
        "average_price": f"{avg_price:.2f}"
    }

    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def export_results_to_csv(results):
    if not results:
        messagebox.showwarning("No Results", "Nothing to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    with open(file_path, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Title", "Price"])
        for title, price in results:
            writer.writerow([title, f"${price:.2f}"])
    messagebox.showinfo("Export Complete", f"Results exported to:\n{file_path}")


def plot_price_distribution(results):
    if not results:
        messagebox.showwarning("No Data", "No data to plot.")
        return

    prices = [p for _, p in results]
    titles = [t for t, _ in results]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(titles, prices, color='skyblue')
    ax.set_xlabel("Price (USD)")
    ax.set_title("Price Distribution of Sold Items")
    plt.tight_layout()

    win = tk.Toplevel()
    win.title("Price Graph")
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def ai_price_suggestion(results):
    if not results:
        messagebox.showwarning("No Data", "No data available.")
        return

    prices = sorted([p for _, p in results])
    avg = statistics.mean(prices)
    med = statistics.median(prices)
    try:
        mode = statistics.mode(prices)
    except:
        mode = "N/A"

    suggestion = f"Average Price: ${avg:.2f}\nMedian Price: ${med:.2f}\nMost Frequent Price: {mode}"
    messagebox.showinfo("AI Suggestion", suggestion)


def forecast_price_trend(results):
    if not results or len(results) < 3:
        messagebox.showwarning("Insufficient Data", "Need at least 3 data points to forecast.")
        return

    y = np.array([p for _, p in results])
    x = np.arange(len(y)).reshape(-1, 1)

    poly = PolynomialFeatures(degree=2)
    x_poly = poly.fit_transform(x)
    model = LinearRegression()
    model.fit(x_poly, y)

    x_future = np.arange(len(y) + 5).reshape(-1, 1)
    x_future_poly = poly.transform(x_future)
    y_pred = model.predict(x_future_poly)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, 'bo-', label='Actual')
    ax.plot(x_future, y_pred, 'r--', label='Forecast')
    ax.set_title("Price Forecast")
    ax.set_xlabel("Index")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    plt.tight_layout()

    win = tk.Toplevel()
    win.title("Price Forecast")
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def alert_below_avg(results):
    if not results:
        messagebox.showinfo("No Results", "No results to evaluate for deals.")
        return

    prices = [price for _, price in results]
    avg_price = sum(prices) / len(prices)
    threshold = avg_price * 0.85
    deals = [(title, price) for title, price in results if price < threshold]

    if not deals:
        messagebox.showinfo("No Alerts", "No items found below 85% of average price.")
        return

    alert_text = f"Deals found below 85% of average price (${avg_price:.2f}):\n\n"
    for title, price in deals:
        alert_text += f"- ${price:.2f} | {title}\n"

    messagebox.showinfo("Price Alerts", alert_text)


def run_search(query, text_widget):
    global last_results
    try:
        results = scrape_ebay_sold_items(query)
        last_results = results

        if not results:
            output = "No results found."
        else:
            avg_price = sum(p for _, p in results) / len(results)
            output = f"Found {len(results)} items:\n"
            for title, price in results:
                output += f"- ${price:.2f} | {title}\n"
            output += f"\nAverage Price: ${avg_price:.2f}"

        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, output)
        log_search_to_history(query, results)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def on_search(entry, text_widget):
    query = entry.get()
    if not query:
        messagebox.showwarning("Missing Input", "Please enter a search term.")
        return
    threading.Thread(target=run_search, args=(query, text_widget)).start()


def on_batch_import(text_widget):
    file_path = filedialog.askopenfilename(filetypes=[("Text/CSV Files", "*.txt *.csv")])
    if not file_path:
        return

    queries = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f) if file_path.endswith(".csv") else f
        for row in reader:
            if isinstance(row, list):
                queries.append(row[0])
            else:
                queries.append(row.strip())

    for query in queries:
        run_search(query, text_widget)


def build_gui():
    root = tk.Tk()
    root.title("eBay Sold Price Finder (Web Query Mode)")

    tk.Label(root, text="Enter Networking Equipment:").pack(pady=5)
    entry = tk.Entry(root, width=50)
    entry.pack(pady=5)

    result_box = scrolledtext.ScrolledText(root, width=100, height=20)
    result_box.pack(pady=10)

    frame = tk.Frame(root)
    frame.pack()

    tk.Button(frame, text="Search", command=lambda: on_search(entry, result_box)).grid(row=0, column=0, padx=5)
    tk.Button(frame, text="Batch Import", command=lambda: on_batch_import(result_box)).grid(row=0, column=1, padx=5)
    tk.Button(frame, text="Export Results", command=lambda: export_results_to_csv(last_results)).grid(row=0, column=2, padx=5)
    tk.Button(frame, text="Plot Prices", command=lambda: plot_price_distribution(last_results)).grid(row=0, column=3, padx=5)
    tk.Button(frame, text="AI Suggestion", command=lambda: ai_price_suggestion(last_results)).grid(row=0, column=4, padx=5)
    tk.Button(frame, text="Forecast", command=lambda: forecast_price_trend(last_results)).grid(row=0, column=5, padx=5)
    tk.Button(frame, text="Alerts", command=lambda: alert_below_avg(last_results)).grid(row=0, column=6, padx=5)

    root.mainloop()


if __name__ == "__main__":
    build_gui()

