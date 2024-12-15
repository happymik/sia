import asyncio
from datetime import datetime

async def test_toshimart_scraper(url: str, headless: bool = False):
    """Simple test script for Toshimart data collection"""
    print("\n🔍 Starting Toshimart Test...\n")
    print(f"Mode: {'Headless' if headless else 'Visual'} browser")
    
    try:
        from plugins.toshimart_scraper import ToshimartScraper
    except ImportError as e:
        print("❌ Error: Could not load scraper. Make sure you're in the right directory.")
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
            labels_str = f" [{', '.join(holder['labels'])}]" if holder.get('labels') else ""
            print(f"• {holder['address']}{labels_str}: {holder['percentage']}")
            
        print("\n=== 💬 Chat Messages ===")
        for msg in data.get('chat', []):
            tags_str = f" [{', '.join(msg['tags'])}]" if msg.get('tags') else ""
            time_str = msg.get('time', '')
            if msg.get('type') == 'transaction':
                print(f"• {time_str} - {msg['address']}{tags_str}: {msg['content']}")
            else:
                print(f"• {time_str} - {msg['address']}{tags_str}: {msg['content']}")
            
        print("\n=== 🔄 Recent Transactions ===")
        for tx in data.get('transactions', []):
            tags_str = f" [{', '.join(tx['tags'])}]" if tx.get('tags') else ""
            print(f"• {tx['time']} - {tx['address']}{tags_str} {tx['action']} {tx['eth']} ({tx['usd']})")n            
        await scraper.cleanup()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        print("\nPlease share this error message if you need help troubleshooting.")

def run_test():
    """Simple wrapper to run the test"""
    URL = "https://toshimart.xyz/0xc6f04d3efac4b8fc8b138d609d3568ee7ff641a0"
    print("\n🚀 Simple Toshimart Tester")
    print("This will check if we can collect data from your token page.")
    asyncio.run(test_toshimart_scraper(URL, headless=True))

if __name__ == "__main__":
    run_test()