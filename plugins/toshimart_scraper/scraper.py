import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from typing import Dict, Optional, List

class ToshimartScraper:
    def __init__(self, token_url: str, headless: bool = True):
        self.token_url = token_url
        self.headless = headless
        self._browser = None
        self._page = None

    async def initialize(self):
        playwright = await async_playwright().start()
        browser_options = {
            "headless": self.headless,
            "slow_mo": 50 if not self.headless else 0
        }
        self._browser = await playwright.chromium.launch(**browser_options)
        self._page = await self._browser.new_page()
        await self._page.set_viewport_size({"width": 1280, "height": 720})
        await self._page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

    async def get_market_data(self):
        return await self._page.evaluate("""
            const getText = (xpath) => {
                const element = document.evaluate(
                    xpath,
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue;
                return element ? element.textContent.trim() : '';
            };

            const marketCap = getText("//div[contains(text(), 'Market Cap')]/following-sibling::div");
            const progress = getText("//div[contains(text(), 'Uniswap Progress')]/following-sibling::div");

            const seenAddresses = new Set();
            const holders = [];
            
            const rows = Array.from(document.querySelectorAll('tr')).filter(row => 
                row.cells && row.cells.length >= 2 && !isNaN(parseFloat(row.cells[1]?.textContent || 'NaN'))
            );
            
            rows.forEach(row => {
                const addressCell = row.cells[0];
                const percentageCell = row.cells[1];
                
                if (!addressCell || !percentageCell) return;
                
                const rawAddress = addressCell.textContent.trim();
                const percentage = percentageCell.textContent.trim();
                
                if (seenAddresses.has(rawAddress) || rawAddress === 'Bonding curve') return;
                
                const labels = [];
                if (addressCell.querySelector('.dev')) labels.push('dev');
                if (addressCell.querySelector('.whale')) labels.push('whale');
                
                let address = rawAddress;
                labels.forEach(label => {
                    address = address.replace(label, '').trim();
                });
                
                seenAddresses.add(rawAddress);
                holders.push({
                    address,
                    percentage,
                    labels
                });
            });

            return { marketCap, progress, holders };
        """)

    async def get_transactions(self):
        print("Getting transactions...")
        await self._page.click('text=Transactions')
        await asyncio.sleep(2)
        
        return await self._page.evaluate("""
            const txs = [];
            document.querySelectorAll('tr').forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length < 4) return;
                
                const time = cells[0]?.textContent.trim();
                const address = cells[1]?.textContent.trim();
                const action = cells[2]?.textContent.trim();
                const usd = cells[3]?.textContent.trim();
                const eth = cells[4]?.textContent.trim();
                const tokens = cells[5]?.textContent.trim();
                
                if (!address || !action) return;
                
                const tags = [];
                if (row.querySelector('.dev')) tags.push('dev');
                if (row.querySelector('.whale')) tags.push('whale');
                
                txs.push({
                    time,
                    address,
                    action,
                    usd,
                    eth,
                    tokens,
                    tags
                });
            });
            return txs;
        """)

    async def get_current_state(self):
        if not self._page:
            await self.initialize()

        try:
            print("Navigating to page...")
            await self._page.goto(self.token_url, wait_until='networkidle')
            await self._page.wait_for_selector('body', timeout=60000)
            await asyncio.sleep(2)

            print("Getting market data and holders...")
            market_data = await self.get_market_data()
            
            print("Getting transactions...")
            transactions = await self.get_transactions()

            market_data['transactions'] = transactions
            
            print("Data extracted successfully")
            return market_data

        except Exception as e:
            print(f"Error scraping data: {e}")
            return {
                "marketCap": "N/A",
                "progress": "N/A",
                "holders": [],
                "transactions": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        
    async def take_debug_screenshot(self, name: str):
        if self._page:
            await self._page.screenshot(path=f"debug_{name}_{datetime.now().strftime('%H%M%S')}.png")

    async def cleanup(self):
        if self._browser:
            await self._browser.close()