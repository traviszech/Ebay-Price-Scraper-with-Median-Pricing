import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import os
import threading
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

last_results = []

def scrape_ebay_sold_items(query):
    url = "https://www.ebay.com/sch/i.html"
    params = {
        "_nkw": query,
        "_sop": "13",  # Sort by: Best Match
        "_ipg": "50",  # Items per page
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

def build_gui():
    root = tk.Tk()
    root.title("eBay Sold Price Finder (No API)")

    tk.Label(root, text="Enter Networking Equipment:").pack(pady=5)
    entry = tk.Entry(root, width=50)
    entry.pack(pady=5)

    result_box = scrolledtext.ScrolledText(root, width=80, height=20)
    result_box.pack(pady=10)

    frame = tk.Frame(root)
    frame.pack()

    search_btn = tk.Button(frame, text="Search", command=lambda: on_search(entry, result_box))
    search_btn.grid(row=0, column=0, padx=10)

    export_btn = tk.Button(frame, text="Save Results to CSV", command=lambda: export_results_to_csv(last_results))
    export_btn.grid(row=0, column=1, padx=10)

    root.mainloop()

if __name__ == "__main__":
    build_gui()
