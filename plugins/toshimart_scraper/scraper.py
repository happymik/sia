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

    async def get_market_data(self) -> Dict:
        script = r'''() => {
            const holders = [];
            const seenAddresses = new Set();
            
            document.querySelectorAll('tr').forEach(row => {
                const cell = row.cells?.[0];
                if (!cell) return;
                
                let address = cell.querySelector('.text-primary-foreground')?.textContent.trim();
                
                if (!address) {
                    const addressMatch = cell.textContent.match(/(0x[a-fA-F0-9]{4,}|\w+\s*[^\d]+)/);
                    address = addressMatch ? addressMatch[0].trim() : null;
                }
                
                if (address && !seenAddresses.has(address) && address !== 'Bonding curve') {
                    const labels = [];
                    
                    if (cell.querySelector('[class*="dev"]')) labels.push('dev');
                    if (cell.querySelector('[class*="whale"]')) labels.push('whale');
                    
                    address = address.replace(/[\u{1F300}-\u{1F9FF}]/gu, '').replace(/\s+/g, ' ').trim();
                    seenAddresses.add(address);
                    
                    holders.push({
                        address,
                        percentage: row.cells[1]?.textContent.trim() || '0',
                        labels
                    });
                }
            });
            
            const marketCap = document.evaluate("//div[contains(text(), 'Market Cap')]/following-sibling::div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.textContent || 'N/A';
            const progress = document.evaluate("//div[contains(text(), 'Uniswap Progress')]/following-sibling::div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue?.textContent || 'N/A';
            
            return { marketCap, progress, holders };
        }'''
        return await self._page.evaluate(script)

    async def get_chat_messages(self) -> List[Dict]:
        print("Getting chat messages...")
        try:
            await self._page.click('text=Chat')
            await asyncio.sleep(2)
            
            script = r'''() => {
                const messages = [];
                
                const containers = Array.from(document.querySelectorAll('.flex.flex-col.overflow-auto'));
                containers.forEach(container => {
                    try {
                        const nameElement = container.querySelector('span.text-primary-foreground');
                        if (!nameElement) return;
                        const name = nameElement.textContent.trim();
                        
                        const timeDiv = Array.from(container.querySelectorAll('div'))
                            .find(div => div.textContent.includes('ago') && !div.children.length);
                        const time = timeDiv ? timeDiv.textContent.trim() : '';
                        
                        const tags = [];
                        container.querySelectorAll('.inline-flex, div[class*="dev"], div[class*="whale"]')
                            .forEach(tag => {
                                const tagText = tag.textContent.trim().toLowerCase();
                                if (tagText && ['dev', 'whale'].includes(tagText)) {
                                    tags.push(tagText);
                                }
                            });
                        
                        let messageContent = '';
                        const textNodes = Array.from(container.childNodes)
                            .filter(node => node.nodeType === Node.TEXT_NODE)
                            .map(node => node.textContent.trim())
                            .filter(text => text.length > 0);
                        
                        const lastText = textNodes[textNodes.length - 1];
                        if (lastText && lastText.includes('ETH of $')) {
                            messageContent = lastText;
                        } else {
                            messageContent = textNodes.join(' ').trim();
                        }
                        
                        if (messageContent) {
                            messages.push({
                                address: name,
                                content: messageContent,
                                time: time,
                                tags: tags,
                                type: messageContent.includes('ETH of $') ? 'transaction' : 'chat'
                            });
                        }
                    } catch (e) {
                        console.error('Error processing chat item:', e);
                    }
                });
                
                return messages;
            }'''
            
            messages = await self._page.evaluate(script)
            print(f"Found {len(messages)} chat messages")
            return messages
            
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            await self.take_debug_screenshot("chat_error")
            return []

    async def get_transactions(self) -> List[Dict]:
        print("Getting transactions...")
        await self._page.click('text=Transactions')
        await asyncio.sleep(2)
        
        script = r'''() => {
            const txs = [];
            document.querySelectorAll('tr').forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length < 4) return;
                
                const time = cells[0]?.textContent.trim() || '';
                const address = cells[1]?.textContent.trim() || '';
                const action = cells[2]?.textContent.trim() || '';
                const usd = cells[3]?.textContent.trim() || '';
                const eth = cells[4]?.textContent.trim() || '';
                const tokens = cells[5]?.textContent.trim() || '';
                
                if (!address || !action) return;
                
                const tags = [];
                const cell = cells[1];
                
                if (cell.querySelector('[class*="dev"]')) tags.push('dev');
                if (cell.querySelector('[class*="whale"]')) tags.push('whale');
                
                txs.push({
                    time,
                    address: address.replace(/[\u{1F300}-\u{1F9FF}]/gu, '').trim(),
                    action,
                    usd,
                    eth,
                    tokens,
                    tags
                });
            });
            return txs;
        }'''
        return await self._page.evaluate(script)

    async def get_current_state(self) -> Dict:
        if not self._page:
            await self.initialize()

        try:
            print("Navigating to page...")
            await self._page.goto(self.token_url, wait_until='networkidle')
            await self._page.wait_for_selector('body', timeout=60000)
            await asyncio.sleep(2)

            print("Getting market data and holders...")
            market_data = await self.get_market_data()
            
            print("Getting chat messages...")
            chat_messages = await self.get_chat_messages()
            
            print("Getting transactions...")
            transactions = await self.get_transactions()

            market_data['chat'] = chat_messages
            market_data['transactions'] = transactions
            market_data['timestamp'] = datetime.now().isoformat()
            
            print("Data extracted successfully")
            return market_data

        except Exception as e:
            print(f"Error scraping data: {e}")
            await self.take_debug_screenshot("error_state")
            return {
                "marketCap": "N/A",
                "progress": "N/A",
                "holders": [],
                "chat": [],
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