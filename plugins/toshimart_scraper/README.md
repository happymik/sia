# Toshimart Scraper Plugin

This plugin is designed to scrape data from Toshimart token pages to monitor market activity and holder behavior.

## Features

### Currently Working
- Market Data Collection
  - Market Cap
  - Uniswap Progress
  - Progress to Listing
- Holder Tracking
  - Address/Name
  - Percentage Holdings
  - Special Labels (dev, whale)
- Transaction History
  - Buy/Sell Actions
  - Amount (ETH & USD)
  - Timestamps
  - Special Labels

### Coming Soon
- Chat Message Collection (In Development)
  - User Messages
  - Buy/Sell Announcements
  - User Tags/Labels
  - Timestamps

## Usage

```python
from plugins.toshimart_scraper import ToshimartScraper

# Initialize scraper
scraper = ToshimartScraper("https://toshimart.xyz/your_token_address")

# Get current market state
data = await scraper.get_current_state()

# Access different data points
market_cap = data["marketCap"]
progress = data["progress"]
holders = data["holders"]
transactions = data["transactions"]
```

## Testing

Use the provided test script to verify functionality:

```bash
python test_toshimart.py
```

## Debugging

The scraper includes built-in debugging features:
- Detailed console logging
- Error screenshots
- Step-by-step data validation