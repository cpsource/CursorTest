import requests
from bs4 import BeautifulSoup
import gradio as gr
import pandas as pd
import time
from urllib.parse import urlencode

class SubletBot:
    def __init__(self):
        self.results = []
    
    def search_craigslist(self, bedrooms, bathrooms, needs_dishwasher, max_price=5000):
        """Search Craigslist SF Bay Area"""
        base_url = "https://sfbay.craigslist.org/search/sfc/sub"
        
        params = {
            'min_bedrooms': bedrooms,
            'min_bathrooms': bathrooms,
            'max_price': max_price,
            'availabilityMode': 0,
            'sale_date': 'all dates'
        }
        
        if needs_dishwasher:
            params['query'] = 'dishwasher'
        
        try:
            response = requests.get(base_url, params=params)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            listings = []
            for item in soup.find_all('li', class_='cl-search-result'):
                title_elem = item.find('a', class_='cl-app-anchor')
                price_elem = item.find('span', class_='priceinfo')
                
                if title_elem and price_elem:
                    listing = {
                        'site': 'Craigslist',
                        'title': title_elem.text.strip(),
                        'price': price_elem.text.strip(),
                        'url': title_elem['href'],
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms
                    }
                    listings.append(listing)
            
            return listings
            
        except Exception as e:
            print(f"Error searching Craigslist: {e}")
            return []
    
    def search_zillow(self, bedrooms, bathrooms, needs_dishwasher):
        """Search Zillow for furnished rentals"""
        # Zillow requires more sophisticated handling due to anti-bot measures
        # You'd need to use selenium or requests-html for dynamic content
        pass
    
    def format_results(self, all_results):
        """Format results for display"""
        if not all_results:
            return "No listings found matching your criteria."
        
        df = pd.DataFrame(all_results)
        return df.to_html(escape=False, index=False)

def search_apartments(bedrooms, bathrooms, dishwasher_required, max_price):
    """Main search function for Gradio interface"""
    bot = SubletBot()
    
    # Search multiple sites
    results = []
    results.extend(bot.search_craigslist(bedrooms, bathrooms, dishwasher_required, max_price))
    
    # Add artificial delay to be respectful
    time.sleep(2)
    
    return bot.format_results(results)

# Create Gradio interface
def create_interface():
    interface = gr.Interface(
        fn=search_apartments,
        inputs=[
            gr.Slider(0, 5, value=1, step=1, label="Minimum Bedrooms"),
            gr.Slider(1, 3, value=1, step=0.5, label="Minimum Bathrooms"),
            gr.Checkbox(label="Dishwasher Required", value=False),
            gr.Slider(1000, 8000, value=3000, step=100, label="Maximum Price ($)")
        ],
        outputs=gr.HTML(label="Search Results"),
        title="SF Sublet & Furnished Apartment Finder",
        description="Search for sublets and furnished apartments in San Francisco"
    )
    
    return interface

if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True)

