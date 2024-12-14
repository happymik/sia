import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def inspect_toshimart_page(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"\n🔍 Inspecting {url}\n")
        
        try:
            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)
            
            # Inspect all visible elements on the page
            elements = await page.evaluate('''
                Array.from(document.querySelectorAll('*'))
                    .filter(el => el.offsetParent !== null) // Only visible elements
                    .map(el => ({
                        tag: el.tagName.toLowerCase(),
                        id: el.id,
                        className: el.className,
                        text: el.textContent.trim(),
                        href: el.href || null,
                        src: el.src || null
                    }))
                    .filter(item => item.text) // Only elements with text
            ''')
            
            # Save raw results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(f'toshimart_raw_inspection_{timestamp}.json', 'w') as f:
                json.dump(elements, f, indent=2)
                
            # Process and categorize elements
            market_data = {}
            holders = []
            transactions = []
            
            for el in elements:
                text = el.get('text', '').strip()
                if not text:
                    continue
                    
                # Look for market cap
                if '$' in text and 'k' in text.lower():
                    market_data['possible_market_cap'] = text
                    
                # Look for percentages
                if '%' in text:
                    market_data['possible_progress'] = text
                    
                # Look for holder-like data (addresses)
                if '0x' in text:
                    holders.append(text)
                    
                # Look for transaction data
                if 'ETH' in text and ('bought' in text.lower() or 'sold' in text.lower()):
                    transactions.append(text)
            
            # Print findings
            print("\n📊 Market Data Found:")
            print(json.dumps(market_data, indent=2))
            
            print("\n👥 Possible Holders:")
            for holder in holders:
                print(holder)
                
            print("\n🔄 Recent Transactions:")
            for tx in transactions:
                print(tx)
                
            # Enter interactive inspection mode
            print("\n🔍 Interactive Inspection Mode")
            while True:
                selector = input("\nEnter CSS selector to test (or 'quit' to exit): ")
                if selector.lower() == 'quit':
                    break
                    
                elements = await page.query_selector_all(selector)
                print(f"\nFound {len(elements)} matching elements:")
                for idx, element in enumerate(elements):
                    text = await element.text_content()
                    print(f"{idx + 1}. {text.strip()}")
        
        except Exception as e:
            print(f"❌ Error during inspection: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    TOKEN_URL = "https://toshimart.xyz/0x9486467d507ce977e118d6d7a182f5a4413ca87a"
    asyncio.run(inspect_toshimart_page(TOKEN_URL))