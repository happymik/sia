# Toshimart Scraper Plugin

This plugin scrapes data from Toshimart token pages to monitor market activity, holder behavior, and chat messages.

## Features

### Market Data
- Market Cap
- Uniswap Progress
- Progress to Listing

### Holder Tracking
- Address/Name
- Percentage Holdings
- Special Labels (dev, whale)

### Transaction History
- Buy/Sell Actions
- Amount in ETH & USD
- Timestamps
- Special Labels

### Chat Messages
- Transaction announcements
- Regular chat messages
- Message timestamps
- User tags/labels

## Data Format

```python
{
    # Market Overview
    "marketCap": "$20.62k",
    "progress": "42% - 27.39k to Uniswap",
    
    # Holders List
    "holders": [
        {
            "address": "Detroit Tokens",
            "percentage": "31.16",
            "labels": ["dev", "whale"]
        }
    ],
    
    # Chat Messages
    "chat": [
        {
            "address": "Detroit Tokens",
            "content": "bought 0.0121 ETH of $SDETROIT",
            "time": "6 days ago",
            "tags": ["dev", "whale"],
            "type": "transaction"
        },
        {
            "address": "0x309d...fa9d",
            "content": "If you buy my coin, I will make all of your wildest dreams come true. Vote For Pedro!",
            "time": "6 days ago",
            "tags": [],
            "type": "chat"
        }
    ],
    
    # Transaction History
    "transactions": [
        {
            "time": "6 days ago",
            "address": "Detroit Tokens",
            "action": "buy",
            "eth": "0.0121",
            "usd": "$47",
            "tags": ["dev", "whale"]
        }
    ]
}
```

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
    
    # Access chat messages
    for msg in data['chat']:
        print(f"{msg['time']} - {msg['address']}: {msg['content']}")
    
    # Access transactions
    for tx in data['transactions']:
        print(f"{tx['time']} - {tx['address']} {tx['action']} {tx['eth']} ({tx['usd']})")
```

## Testing

Use the provided test script:
```bash
python test_toshimart.py
```

## Features Coming Soon
- Historical data tracking
- Market trend analysis
- Advanced chat analysis
- Sentiment analysis for chat messages
- Real-time event streaming

## Known Issues
- Some emoji characters might be stripped from messages
- Very short messages might be filtered out
- Time parsing might vary based on browser locale