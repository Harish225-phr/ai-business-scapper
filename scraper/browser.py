from playwright.sync_api import sync_playwright
from .config import Config

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
    
    def start(self, headless=None):
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        
        if headless is None:
            headless = Config.BROWSER_HEADLESS
            
        if self.browser is None:
            # Using chromium for standard behavior
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-notifications",
                    "--no-sandbox"
                ]
            )
        
        if self.context is None:
            # Set a standard viewport and user agent
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
        return self.context
    
    def get_new_page(self):
        if self.context is None:
            self.start()
        return self.context.new_page()
    
    def stop(self):
        if self.context:
            self.context.close()
            self.context = None
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
