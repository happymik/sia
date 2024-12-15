import asyncio
from datetime import datetime

async def test_toshimart_scraper(url: str, headless: bool = False):
    print("\n🔍 Starting Toshimart Test...\n")
    print(f"Mode: {'Headless' if headless else 'Visual'} browser")
    
    try:
        from .scraper import ToshimartScraper
    except ImportError as e:
        print("❌ Error: Could not load scraper.")
        print(f"Details: {e}")
        return

    try:
        print("📡 Connecting to Toshimart...")
        scraper = ToshimartScraper(url, headless=headless)
        await scraper.initialize()
        
        print("🔍 Fetching market data...\n")
        data = await scraper.get_current_state()
        
        print("=== 📊 Market Overview ===")
        print(f"Market Cap: {data.get('marketCap', 'N/A')}")
        print(f"Progress: {data.get('progress', 'N/A')}")
        
        print("\n=== 👥 Current Holders ===")
        for holder in data.get('holders', []):
            labels_text = f" [{', '.join(holder['labels'])}]" if holder.get('labels') else ""
            print(f"• {holder['address']}{labels_text}: {holder['percentage']}")
            
        print("\n=== 🔄 Recent Transactions ===")
        for tx in data.get('transactions', []):
            tags_text = f" [{', '.join(tx['tags'])}]" if tx.get('tags') else ""
            print(f"• {tx['time']} - {tx['address']}{tags_text} {tx['action']} {tx['eth']} ({tx['usd']})")
            
        await scraper.cleanup()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        print("\nPlease share this error message if you need help troubleshooting.")

def run_test(token_url: str):
    print("\n🚀 Simple Toshimart Tester")
    print("This will check if we can collect data from your token page.")
    asyncio.run(test_toshimart_scraper(token_url, headless=False))