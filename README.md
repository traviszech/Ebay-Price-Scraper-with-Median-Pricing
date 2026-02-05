# eBay Sold Price Analyzer for Networking Equipment 🛠️📊

A professional Python desktop application that empowers IT professionals, resellers, and network engineers with comprehensive market intelligence for networking equipment. Built with advanced analytics, AI-powered forecasting, and enterprise-grade data management.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)](https://github.com/traviszech/Ebay-Price-Scraper-with-Median-Pricing/graphs/commit-activity)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Advanced Features](#-advanced-features)
- [Use Cases](#-use-cases)
- [Configuration](#-configuration)
- [Documentation](#-documentation)
- [Supported Platforms](#-supported-platforms)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The eBay Sold Price Analyzer is a sophisticated market research tool designed specifically for the networking equipment industry. Whether you're sourcing equipment for enterprise deployments, running a resale business, or conducting competitive price analysis, this application provides the data-driven insights you need to make informed decisions.

### What Sets This Tool Apart

- **Intelligent Data Collection** — Multi-page scraping with automatic retry logic and rate limiting
- **Historical Tracking** — SQLite database stores every search for long-term trend analysis
- **Smart Filtering** — Automatically excludes broken items, bulk lots, and outliers
- **Comprehensive Analytics** — Statistical analysis with quartile-based pricing recommendations
- **Time-Series Forecasting** — Machine learning models predict price movements
- **Professional Visualizations** — Multi-panel charts reveal market insights at a glance

---

## ✨ Key Features

### Core Functionality

- 🔍 **Advanced Search Engine**
  - Multi-page scraping (150+ items per search vs. competitors' 50)
  - Automatic retry with exponential backoff
  - Real-time progress tracking
  - Shipping cost integration for true total cost analysis

- 📊 **Professional Analytics**
  - Mean, median, mode, and quartile calculations
  - Outlier detection and removal
  - Box plots, histograms, and distribution analysis
  - Condition-based price breakdown

- 💾 **Enterprise Data Management**
  - SQLite database for persistent storage
  - Historical trend tracking across weeks/months
  - Searchable archive of all research
  - CSV export for external analysis

### Intelligence & Automation

- 🤖 **AI-Powered Price Recommendations**
  - **BUY BELOW** threshold (25th percentile)
  - **MARKET PRICE** guidance (median)
  - **SELL ABOVE** target (75th percentile)
  - Confidence scoring based on sample size

- 📈 **Time-Series Forecasting**
  - Polynomial regression with trend detection
  - Date-based analysis when available
  - Rising/falling/stable market indicators
  - Visual forecast with confidence intervals

- 🚨 **Smart Deal Alerts**
  - Customizable threshold (default: 85% of average)
  - Automatic savings calculation
  - Sorted by best deals first
  - Condition and shipping cost awareness

### Advanced Tools

- 🔄 **Model Comparison Mode**
  - Side-by-side analysis of multiple products
  - Visual comparison charts
  - Sample size and price range metrics
  - Perfect for vendor/model decision making

- 📉 **Historical Trend Analysis**
  - Track same products over time
  - Identify seasonal patterns
  - Market volatility indicators
  - Price trajectory visualization

- 🎯 **Smart Filtering System**
  - Auto-excludes: "broken", "for parts", "lot of", "as-is"
  - Customizable keyword blacklist
  - Price range bounds (min/max)
  - Condition-based filtering

### User Experience

- 🎨 **Modern GUI Interface**
  - Clean, professional design
  - Progress indicators for long operations
  - Quick-search favorite buttons
  - Dark mode support
  - Keyboard shortcuts (Enter to search)

- ⚙️ **Comprehensive Settings**
  - Tabbed settings interface
  - All preferences persist across sessions
  - Per-user customization
  - Import/export configuration

- 📋 **Batch Operations**
  - Import queries from TXT/CSV files
  - Two modes: Compare or Individual Search
  - Automated workflow for multiple products
  - Progress tracking

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for eBay scraping

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/traviszech/Ebay-Price-Scraper-with-Median-Pricing.git
cd ebay-price-scraper

# Install dependencies
pip install -r requirements.txt

# Run the application
python ebay_analyzer_enhanced.py
```

### Linux-Specific Setup

```bash
# Install Tkinter if not present
sudo apt-get update
sudo apt-get install python3-tk

# Continue with standard installation
pip install -r requirements.txt
python ebay_analyzer_enhanced.py
```

### Dependencies

The application requires the following packages (see `requirements.txt`):

```
requests>=2.31.0          # HTTP library for web scraping
beautifulsoup4>=4.12.3    # HTML parsing
matplotlib>=3.8.2         # Data visualization
numpy>=1.26.3             # Numerical computing
scikit-learn>=1.4.0       # Machine learning algorithms
```

*Note: `tkinter` and `sqlite3` are included with Python standard library*

---

## 🚀 Quick Start

### Basic Search Workflow

1. **Launch the application**
   ```bash
   python ebay_analyzer_enhanced.py
   ```

2. **Enter a product name**
   - Example: "Cisco Catalyst 2960-X 48 port"
   - Be specific for better results

3. **Click Search or press Enter**
   - Watch the progress bar
   - Results appear with prices, shipping, and conditions

4. **Analyze the data**
   - Click "Price Recommendation" for buy/sell guidance
   - Click "Plot Analysis" for visual insights
   - Click "Deal Alerts" to find bargains

### First-Time Setup Recommendations

1. **Configure Settings** (File → Settings)
   - Set your preferred price range
   - Add custom exclusion keywords
   - Adjust alert threshold
   - Save favorite searches

2. **Run Initial Searches**
   - Search for products you track regularly
   - Build historical data for trend analysis

3. **Test Batch Import**
   - Use the included `sample_batch_queries.txt`
   - Learn the comparison workflow

---

## 🔬 Advanced Features

### Historical Trend Tracking

Build a price history database by searching the same products over time:

1. Search for a product (e.g., "Juniper EX2200-48T")
2. Wait a few days/weeks
3. Search again
4. Click "Historical Trends" to see price changes

**Use Cases:**
- Identify seasonal price drops
- Track market recovery after hardware EOL announcements
- Find optimal buying windows

### Batch Comparison Analysis

Perfect for comparing similar models or vendors:

1. Create a text file with one product per line:
   ```
   Cisco Catalyst 2960-X 48 port
   Cisco Catalyst 2960-S 48 port
   Cisco Catalyst 3750-X 48 port
   ```

2. Click "Batch Import" → Select file → Choose "Compare"

3. View side-by-side metrics:
   - Average prices
   - Sample sizes
   - Price distributions
   - Visual bar charts

**Use Cases:**
- Vendor selection for bulk purchases
- Model comparison for budget optimization
- Market share analysis (item count = market availability)

### Smart Deal Detection

The deal alert system uses statistical analysis to find genuine bargains:

**Algorithm:**
1. Calculate average price of all listings
2. Apply threshold (default 85%)
3. Filter items below threshold
4. Sort by best savings
5. Factor in shipping and condition

**Pro Tips:**
- Adjust threshold in settings (80% = stricter, 90% = more results)
- Check condition carefully - "Used" may be a better deal than "Refurbished"
- Consider shipping costs (included in total)

### Price Forecasting

Machine learning forecasts help predict market direction:

**Methodology:**
- Polynomial regression (degree 2)
- Uses actual sale dates when available
- Trend classification: Rising, Falling, or Stable
- Visual prediction with confidence bands

**Interpretation:**
- **Rising** (>5% increase) — Prices trending up, buy now or wait for correction
- **Falling** (>5% decrease) — Wait for better prices
- **Stable** (±5%) — Consistent market, safe to purchase

---

## 💼 Use Cases

### For IT Professionals & Network Engineers

**Lab Equipment Sourcing**
- Compare pricing across switch models
- Track when enterprise gear hits used market
- Find deals on end-of-life equipment for labs

**Budget Planning**
- Historical trends inform budget forecasts
- Price forecasting for multi-year deployments
- Vendor cost comparison for proposals

### For Resellers & Flippers

**Inventory Acquisition**
- Deal alerts find underpriced inventory
- Price recommendations optimize resale margins
- Condition tracking ensures quality control

**Market Analysis**
- Track competitor pricing
- Identify high-margin products
- Seasonal trend analysis for inventory timing

### For Small Business IT

**Cost Optimization**
- Find "good enough" used equipment
- Compare new vs. refurbished pricing
- Track total cost of ownership (shipping included)

**Vendor Intelligence**
- Market availability (item count)
- Price stability indicators
- Alternative product discovery

---

## ⚙️ Configuration

### Settings Overview

Access via **File → Settings** in the application menu.

#### Scraping Settings
| Setting | Default | Description |
|---------|---------|-------------|
| Max Pages | 3 | Number of eBay pages to scrape (50 items/page) |
| Max Retries | 3 | Retry attempts for failed requests |

#### Filter Settings
| Setting | Default | Description |
|---------|---------|-------------|
| Min Price | $5 | Ignore items below this price |
| Max Price | $10,000 | Ignore items above this price |
| Exclude Keywords | lot of, broken, for parts, as-is | Auto-filter these terms |
| Alert Threshold | 0.85 | Deal alert trigger (85% of average) |

#### Appearance Settings
| Setting | Default | Description |
|---------|---------|-------------|
| Dark Mode | Off | Toggle dark theme (requires restart) |
| Window Size | 1200x700 | Default window dimensions |

### Configuration File

Settings are stored in `config.json`:

```json
{
  "default_max_pages": 3,
  "max_retries": 3,
  "min_price": 5,
  "max_price": 10000,
  "alert_threshold": 0.85,
  "default_exclude_keywords": [
    "lot of",
    "broken",
    "for parts",
    "as-is",
    "not working"
  ],
  "favorite_searches": [
    "Cisco Catalyst 2960-X",
    "Juniper EX2200"
  ],
  "dark_mode": false,
  "last_export_dir": "",
  "window_geometry": "1200x700"
}
```

### Database Schema

Data is stored in `ebay_data.db` (SQLite):

**items** table:
```sql
- id (INTEGER PRIMARY KEY)
- title (TEXT)
- price (REAL)
- shipping (REAL)
- total_cost (REAL)
- condition (TEXT)
- sale_date (TEXT)
- query (TEXT)
- scrape_date (TEXT)
- url (TEXT)
```

**searches** table:
```sql
- id (INTEGER PRIMARY KEY)
- timestamp (TEXT)
- query (TEXT)
- item_count (INTEGER)
- average_price (REAL)
- median_price (REAL)
- min_price (REAL)
- max_price (REAL)
```

---

## 📄 Documentation

### Included Resources

- **README.md** — This comprehensive guide
- **Network_Price_Tool_Guide.md** — Detailed user manual (Markdown)
- **Network_Price_Tool_Guide.pdf** — Printable user manual (PDF)
- **sample_batch_queries.txt** — Example batch import file

### Logging

Application events are logged to `ebay_analyzer.log`:

```
2026-02-05 10:30:15 - INFO - Application started
2026-02-05 10:30:20 - INFO - Database initialized
2026-02-05 10:30:45 - INFO - Scraping page 1 for query: Cisco 2960
2026-02-05 10:30:52 - INFO - Scraped 47 items for query: Cisco 2960
2026-02-05 10:30:53 - INFO - Filtered 47 items to 42 items
2026-02-05 10:30:54 - INFO - Saved 42 items to database
```

### File Structure

```
ebay-price-analyzer/
├── ebay_analyzer_enhanced.py    # Main application
├── requirements.txt              # Python dependencies
├── config.json                   # User configuration (auto-generated)
├── ebay_data.db                 # SQLite database (auto-generated)
├── ebay_analyzer.log            # Application logs (auto-generated)
├── sample_batch_queries.txt     # Example batch file
├── README.md                     # This file
├── Network_Price_Tool_Guide.md  # Detailed documentation
└── Network_Price_Tool_Guide.pdf # PDF documentation
```

---

## 🌐 Supported Platforms

### Tested Brands (Networking Equipment)

| Manufacturer | Example Models |
|-------------|----------------|
| **Cisco** | Catalyst 2960/3750/3850/9000 series, ASA, ISR |
| **Juniper** | EX2200/3300/4200, SRX, QFX series |
| **Palo Alto Networks** | PA-220/850/3020/5220 firewalls |
| **Ubiquiti** | EdgeSwitch, UniFi switches, EdgeRouter |
| **Arista** | 7050/7280/7500 series switches |
| **Fortinet** | FortiGate firewalls, FortiSwitch |
| **HPE / Aruba** | ProCurve, FlexFabric, Aruba switches |
| **Dell** | PowerConnect, Networking N-series |
| **MikroTik** | RouterBoard, Cloud Router Switch |
| **Netgear** | ProSafe, M4300 managed switches |
| **TP-Link** | JetStream, Omada SDN |
| **D-Link** | DGS/DES managed switches |

### Operating System Compatibility

| OS | Status | Notes |
|----|--------|-------|
| Windows 10/11 | ✅ Fully Supported | Native Tkinter support |
| macOS 11+ | ✅ Fully Supported | Native Tkinter support |
| Linux (Ubuntu/Debian) | ✅ Fully Supported | May require `python3-tk` package |
| Linux (RHEL/CentOS) | ✅ Fully Supported | May require `python3-tkinter` package |

---

## 🔧 Troubleshooting

### Common Issues

**"No results found"**
- Try broader search terms (e.g., "Cisco 2960" instead of full part number)
- Check filter settings (min/max price may be too restrictive)
- Verify internet connection
- Check if eBay is accessible from your network

**"Search is slow"**
- Reduce pages in settings (1-2 pages instead of 3)
- eBay may be rate-limiting (wait 5-10 minutes between searches)
- Check network speed

**"Missing shipping costs or dates"**
- eBay doesn't always provide this data in listings
- Some sellers don't specify shipping costs
- Sale dates may not be displayed for all listings
- Application will still function with partial data

**"Database errors"**
- Close all instances of the application
- Check disk space
- If persistent, delete `ebay_data.db` (loses history) and restart
- Check file permissions in application directory

**"Module not found" errors**
- Run `pip install -r requirements.txt` again
- Ensure you're using Python 3.8+
- Try upgrading pip: `pip install --upgrade pip`

---

## 🤝 Contributing

Contributions are welcome! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update README.md for new features
- Test on Windows, macOS, and Linux if possible
- Add logging for debugging

### Bug Reports

Please include:
- Operating system and Python version
- Full error message and stack trace
- Steps to reproduce the issue
- Screenshots if applicable

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ℹ️ Liability and warranty disclaimers apply

---

## ⚠️ Disclaimer

**Important Legal Information:**

- This application is **not affiliated with, endorsed by, or connected to eBay Inc.**
- Data is scraped from publicly accessible eBay listings
- Use this tool **for personal research and educational purposes only**
- Respect eBay's Terms of Service and robots.txt
- The application implements reasonable rate limiting to avoid server overload
- Price forecasts and recommendations are **for informational purposes only**
- No warranty is provided for accuracy of data or predictions
- Users are responsible for compliance with applicable laws and regulations

**Best Practices:**
- Use reasonable search intervals (avoid excessive scraping)
- Don't attempt to circumvent eBay's rate limits
- Verify critical pricing decisions with manual research
- Respect intellectual property and data usage rights

---

## 🎓 Tips for Optimal Results

### Search Strategy

1. **Be Specific but Not Too Specific**
   - ✅ Good: "Cisco Catalyst 2960-X 48 port"
   - ❌ Too broad: "Cisco switch"
   - ❌ Too specific: "WS-C2960X-48FPD-L with specific serial number"

2. **Build Historical Data**
   - Search products weekly/monthly
   - Historical trends require multiple data points
   - Patience pays off with better forecasting

3. **Leverage Batch Comparison**
   - Compare similar models before purchasing
   - Identify which vendors hold value better
   - Find "sweet spot" products with best price/performance

4. **Use Filters Wisely**
   - Add brand-specific keywords to exclusions ("knockoff", "compatible")
   - Adjust price ranges for your target market segment
   - Review excluded items occasionally to refine filters

5. **Monitor Total Cost**
   - Always consider shipping in total cost
   - Some "cheap" items have expensive shipping
   - Application automatically includes this in calculations

---

## 🔮 Future Roadmap

Potential enhancements under consideration:

- 📧 Email alerts for price drops on watched items
- ☁️ Cloud sync for database across devices
- 📱 Mobile companion app
- 🌍 Multi-marketplace support (Mercari, Facebook Marketplace)
- 🧠 Enhanced ML models with neural networks
- 📊 Advanced analytics dashboard
- 🔗 Integration with inventory management systems
- 📅 Scheduled automatic searches
- 🎨 Custom chart themes and export formats

---

## 👏 Acknowledgments

- **eBay** for providing publicly accessible marketplace data
- **BeautifulSoup** for powerful HTML parsing
- **scikit-learn** for machine learning capabilities
- **matplotlib** for professional visualizations
- The **open-source community** for invaluable tools and libraries

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/traviszech/Ebay-Price-Scraper-with-Median-Pricing/issues)
- **Discussions:** [GitHub Discussions](https://github.com/traviszech/Ebay-Price-Scraper-with-Median-Pricing/discussions)
- **Documentation:** See `Network_Price_Tool_Guide.pdf`

---

<div align="center">

**Built with ❤️ for IT professionals, resellers, and data-driven decision makers**

*Making smarter purchasing decisions through data intelligence*

[⭐ Star this repo](https://github.com/traviszech/Ebay-Price-Scraper-with-Median-Pricing) • [🐛 Report Bug](https://github.com/traviszech/Ebay-Price-Scraper-with-Median-Pricing/issues) • [✨ Request Feature](https://github.com/traviszech/Ebay-Price-Scraper-with-Median-Pricing/issues)

</div>
