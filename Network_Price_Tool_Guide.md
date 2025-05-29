
# User Guide: eBay Sold Price Finder for Networking Equipment

---

## Overview

The eBay Sold Price Finder is a Python-based desktop application with a graphical interface designed for resellers, IT professionals, and analysts to track, evaluate, and forecast the market prices of networking equipment across major brands. The tool scrapes recent eBay listings and provides actionable insights including deal alerts and pricing trends.

---

## System Requirements
- Python 3.8+
- Internet connection
- OS: Windows, macOS, or Linux

## Installation
1. Install Python and pip (if not already installed).
2. Open a terminal and install dependencies:
   ```bash
   pip install requests beautifulsoup4 matplotlib scikit-learn openai tkinter pandas
   ```
3. (Linux users) Install tkinter:
   ```bash
   sudo apt-get install python3-tk
   ```

---

## Launching the App
Run the script via:
```bash
python EbayPriceScraper.py
```

---

## Main Features

1. **Manual Search**
   - Enter the name of any networking product (e.g., "Cisco Catalyst 2960-X").
   - Click "Search" to retrieve sold listings from eBay.
   - Results include individual titles, prices, and an average calculated price.

2. **Batch Search (Import Products)**
   - Click "Import Products" and select a `.txt` or `.csv` file with product names.
   - The app performs searches for each item sequentially.
   - Results for all items are shown in the main window.

3. **Export to CSV**
   - After performing a search, click "Save Results to CSV".
   - Choose a save location and export the full listing and average pricing data.

4. **Search Logging**
   - Every search is automatically logged in `search_history.csv`.
   - Logged info: timestamp, query, item count, and average price.

5. **Graphical Trend Display**
   - Click "Show Graph" after a search.
   - View a histogram of all sold prices to identify pricing distribution.

6. **Deal Alerts**
   - Click "Alerts" to scan current results for deals that are 15% or more below the average price.
   - Alerts are shown in a popup and flagged as high-potential resale opportunities.

7. **AI-Powered Pricing Insights**
   - The app includes an AI model that estimates future price trends based on scraped data.
   - Useful for deciding when to buy or sell.
   - Requires enough historical listings to activate.

8. **Smart Suggestions (AI)**
   - Based on entered queries, the app offers alternative or related models you may consider tracking.
   - Enhances sourcing strategy by uncovering similar or better-value items.

9. **Comprehensive Equipment List Support**
   - Sample `.csv` files with product names from brands like Cisco, Juniper, Palo Alto, Ubiquiti, MikroTik, Fortinet, Arista, HPE, Netgear, TP-Link, D-Link, and Dell can be imported for batch scanning.

---

## Supported Manufacturers (Examples)
- Cisco
- Juniper
- Palo Alto Networks
- Ubiquiti
- MikroTik
- Fortinet
- Arista
- Aruba / HPE
- Netgear
- TP-Link
- D-Link
- Dell

---

## Planned Future Features
- Integration with Google Sheets / Notion
- Real-time background deal alerts
- Email/SMS notifications for price drops
- Historical market trend analysis
- Custom alert thresholds

---

## Troubleshooting
- Ensure you are connected to the internet.
- If results fail to load, eBay may be temporarily blocking automated queries.
- Check for typos in product names.

---

## Contact & Contributions
If you'd like to suggest a feature or report a bug, reach out to the project maintainer or open a GitHub issue (if hosted).

---

## Disclaimer
This application uses public eBay data for informational purposes only and is not affiliated with eBay. Forecasts and suggestions are for research use and not guaranteed investment advice.

---

**End of Guide**
