Live Derivatives Options Flow & Open Interest Tracker
Real-time quantitative tracking and visualization of intraday Call/Put Open Interest (OI) divergence for NIFTY and BANKNIFTY indices.

🚀 Overview
This project is a Python-based data engineering and analytics pipeline designed to track institutional options flow in the Indian derivatives market. It bypasses standard exchange rate limits to scrape live intraday options chain data from the National Stock Exchange (NSE) API, dynamically calculates shifts in Open Interest across configurable strike ranges, and visualizes market momentum to identify real-time support and resistance bands.

🛠️ Tech Stack & Libraries
Language: Python 3.x

Data Engineering & Ingestion: requests, json (Custom headers for API rate-limit management)

Time-Series Analytics: pandas, numpy, collections.defaultdict

Visualization: matplotlib.pyplot

Environment: Jupyter Notebooks

🏗️ Core System Features
1. Real-Time Options Chain Ingestion

Engineered an automated polling script to ping the NSE API (/api/option-chain-indices) every 5 minutes during active market hours.

Implemented custom browser-header rotation to ensure uninterrupted data flow and prevent automated IP blocking by the exchange.

2. Dynamic OI Divergence Engine

Calculates real-time Change in Open Interest for both Calls and Puts within highly specific, dynamic strike-price ranges (e.g., At-The-Money ± 100 points, ± 300 points).

Identifies immediate intraday support and resistance levels by isolating the highest concentration of Put writing vs. Call writing.

3. Automated Batch Processing (End-of-Day)

Includes a robust EOD processing script (Stock_OI.py) that automates the downloading, parsing, and cleaning of exchange-provided Bhavcopy CSV files.

Dynamically maps equities to their respective sectors for broader macro-market analysis.

⚙️ Execution & Usage
Clone the repository:

Bash
git clone https://github.com/raval137/NIFTY-BANKNIFTY-CALL-PUT-Live-Market-Analysis.git
Install Dependencies:

Bash
pip install pandas numpy matplotlib requests pytz jupyter
Run the Intraday Trackers:
Open Jupyter Notebook and execute the desired tracker during Indian Standard Time (IST) market hours (09:15 - 15:30).

Bash
jupyter notebook "CHANGE_IN_OI_BANKNIFTY_300_Range.ipynb"
End of Day Processing:
Run the standalone Python script after market close to aggregate sector-wide Bhavcopy data.

Bash
python Stock_OI.py
