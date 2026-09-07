import time
from urllib.parse import quote
from .config import Config
from .result_extractor import extract_all_data

class MapsScraper:
    def __init__(self, page):
        self.page = page

    def search_location(self, keyword, location, update_progress_cb=None):
        query = f"{keyword} in {location}"
        url = f"https://www.google.com/maps/search/{quote(query)}"
        
        if update_progress_cb:
            update_progress_cb(f"Navigating to {url}")
            
        try:
            self.page.goto(url, timeout=60000)
            self.page.wait_for_selector('div[role="feed"]', timeout=30000)
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            if update_progress_cb:
                update_progress_cb(f"Error: Could not load results for {location}.")
            return []
            
        businesses = []
        unique_urls = set()
        
        no_new_results_count = 0
        scroll_attempts = 0
        
        if update_progress_cb:
            update_progress_cb(f"Scrolling results for {location}...")
            
        while scroll_attempts < Config.MAX_SCROLL_ATTEMPTS and len(businesses) < Config.MAX_RESULTS_PER_LOCATION:
            try:
                # Find the feed container to scroll
                feed = self.page.locator('div[role="feed"]')
                if feed.count() == 0:
                    break
                    
                # Extract currently visible cards
                # Note: We need to wait a moment for items to render
                self.page.wait_for_timeout(int(Config.SCROLL_PAUSE * 1000))
                
                cards = feed.locator('div.qBF1Pd.fontHeadlineSmall').locator('..').locator('..').locator('..').locator('..')
                
                # To get better elements, we can look for links to places
                items = self.page.query_selector_all('a[href*="/maps/place/"]')
                
                new_found = False
                for item in items:
                    # The parent elements usually contain the full info
                    parent = item.evaluate_handle('el => el.closest("[role=\'article\']")')
                    if not parent:
                        parent = item.evaluate_handle('el => el.parentElement.parentElement.parentElement')
                        
                    if parent:
                        try:
                            # We can use our extractor logic here
                            data = extract_all_data(parent, location)
                            if data:
                                # Simple deduplication during scraping by URL
                                url = data['google_maps_url']
                                if url not in unique_urls:
                                    unique_urls.add(url)
                                    businesses.append(data)
                                    new_found = True
                        except Exception as e:
                            # print("Extraction error:", e)
                            pass

                if update_progress_cb:
                    update_progress_cb(f"Found {len(businesses)} businesses...", businesses)

                if len(businesses) >= Config.MAX_RESULTS_PER_LOCATION:
                    break
                    
                # Scroll the feed down
                # We can execute JS to scroll the feed element
                self.page.evaluate('document.querySelector(\'div[role="feed"]\').scrollBy(0, 10000)')
                
                # Check if we hit the bottom
                end_of_list = self.page.evaluate('document.body.innerText.includes("You\'ve reached the end of the list")')
                if end_of_list:
                    if update_progress_cb:
                        update_progress_cb(f"Reached end of list for {location}.")
                    break
                    
                if not new_found:
                    no_new_results_count += 1
                else:
                    no_new_results_count = 0
                    
                if no_new_results_count >= Config.MAX_NO_NEW_RESULTS:
                    if update_progress_cb:
                        update_progress_cb(f"No new results appearing for {location}.")
                    break
                    
                scroll_attempts += 1
                
            except Exception as e:
                print(f"Error during scrolling: {e}")
                break
                
        return businesses
