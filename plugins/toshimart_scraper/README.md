# Toshimart Scraper Plugin

This plugin is designed to scrape data from Toshimart token pages to monitor market activity and holder behavior.

## Data Format

The scraper returns data in the following structure:

```python
{
    # Market Overview
    "marketCap": "20.62k",        # Current market cap in USD
    "progress": "42% - 27.38k",   # Progress to Uniswap listing
    
    # Holders List
    "holders": [
        {
            "address": "Detroit Tokens🪙",  # Holder name/address
            "percentage": "31.16",          # Holding percentage
            "labels": ["dev", "whale"]      # Special labels if any
        },
        # ... more holders
    ],
    
    # Transaction History
    "transactions": [
        {
            "time": "31 minutes ago",      # Transaction timestamp
            "address": "Wall Street Bets",  # Buyer/Seller name
            "action": "sell",              # Transaction type
            "eth": "< 0.001",             # Amount in ETH
            "usd": "$3",                  # Amount in USD
            "tokens": "123456",           # Amount in tokens
            "tags": ["whale", "dev"]      # Special tags if any
        },
        # ... more transactions
    ]
}
```

## Features

### Currently Working
- Market Data Collection
  - Market Cap (e.g., "$20.62k")
  - Uniswap Progress (e.g., "42% - 27.38k to Uniswap")

- Holder Tracking
  - Address/Name (full addresses or ENS names)
  - Percentage Holdings (exact percentage)
  - Special Labels (dev, whale) - Currently being enhanced

- Transaction History
  - Timestamps (relative time, e.g., "31 minutes ago")
  - Buy/Sell Actions
  - Amount in ETH and USD
  - Special Tags (dev, whale) - Currently being enhanced

### Coming Soon
- Chat Message Collection (In Development)
  - User Messages
  - Buy/Sell Announcements
  - User Tags/Labels
  - Timestamps

## Usage

```python
from plugins.toshimart_scraper import ToshimartScraper

async def monitor_token():
    # Initialize scraper
    scraper = ToshimartScraper("https://toshimart.xyz/your_token_address")
    
    # Get current market state
    data = await scraper.get_current_state()
    
    # Access market data
    print(f"Market Cap: {data['marketCap']}")
    print(f"Progress: {data['progress']}")
    
    # Access holder information
    for holder in data['holders']:
        labels = ', '.join(holder['labels']) if holder['labels'] else ''
        print(f"{holder['address']}: {holder['percentage']}% {labels}")
    
    # Access transactions
    for tx in data['transactions']:
        print(f"{tx['time']} - {tx['address']} {tx['action']} {tx['eth']} ({tx['usd']})")
```

## Testing

Use the provided test script to verify functionality:

```bash
python test_toshimart.py
```

## Known Issues and Improvements
1. Special labels (dev, whale) detection is being enhanced
2. Chat functionality is under development
3. Some transaction amounts might show as "< 0.001" for very small transactions

## Debugging

The scraper includes built-in debugging features:
- Detailed console logging
- Error screenshots
- Step-by-step data validation