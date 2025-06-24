import requests
from bs4 import BeautifulSoup
import gradio as gr
import pandas as pd
import time
from urllib.parse import urlencode

class SubletBot:
    def __init__(self):
        self.results = []
    
    def search_craigslist(self, bedrooms, bathrooms, max_price=5000):
        """Search Craigslist SF Bay Area"""
        base_url = "https://sfbay.craigslist.org/search/sfc/sub"
        
        params = {
            'min_bedrooms': bedrooms,
            'min_bathrooms': bathrooms,
            'max_price': max_price,
            'availabilityMode': 0,
            'sale_date': 'all dates'
        }
        
        # Add headers to look more like a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            #print(f"soup = {soup}")
            print(soup.prettify()[:6000])  # First 2000 chars to avoid overwhelming output
            
            listings = []
            for item in soup.find_all('li', class_='cl-search-result'):
                #print(item.prettify()[:500])  # First 2000 chars to avoid overwhelming output

                title_elem = item.find('a', class_='cl-app-anchor')
                price_elem = item.find('span', class_='priceinfo')

                #print(f"craigslist: {price_elem}")

                if title_elem and price_elem:
                    listing = {
                        'site': 'Craigslist',
                        'title': title_elem.text.strip(),
                        'price': price_elem.text.strip(),
                        'url': f"https://sfbay.craigslist.org{title_elem['href']}",
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms
                    }
                    listings.append(listing)
            
            return listings
            
        except Exception as e:
            print(f"Error searching Craigslist: {e}")
            return []
    
    def search_zillow(self, bedrooms, bathrooms):
        """Search Zillow for furnished rentals"""
        # Zillow requires more sophisticated handling due to anti-bot measures
        # You'd need to use selenium or requests-html for dynamic content
        pass
    
    def format_results(self, all_results):
        """Format results for display"""
        if not all_results:
            return "<p>No listings found matching your criteria.</p>"
        
        html_output = "<div style='max-height: 600px; overflow-y: auto;'>"
        
        for result in all_results:
            html_output += f"""
            <div style='border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px;'>
                <h3 style='margin: 0 0 10px 0; color: #333;'>{result['title']}</h3>
                <p><strong>Price:</strong> {result['price']}</p>
                <p><strong>Bedrooms:</strong> {result['bedrooms']} | <strong>Bathrooms:</strong> {result['bathrooms']}</p>
                <p><strong>Source:</strong> {result['site']}</p>
                <a href="{result['url']}" target="_blank" style='color: #007bff; text-decoration: none;'>View Listing →</a>
            </div>
            """
        
        html_output += "</div>"
        return html_output

def search_apartments(bedrooms, bathrooms, max_price):
    """Main search function for Gradio interface"""
    bot = SubletBot()
    
    # Search multiple sites
    results = []
    print(f"Searching for {bedrooms}BR/{bathrooms}BA apartments, max ${max_price}")
    
    results.extend(bot.search_craigslist(bedrooms, bathrooms, max_price))
    
    # Add artificial delay to be respectful
    time.sleep(2)
    
    print(f"Found {len(results)} listings")
    return bot.format_results(results)

# Create Gradio interface
def create_interface():
    interface = gr.Interface(
        fn=search_apartments,
        inputs=[
            gr.Slider(0, 5, value=1, step=1, label="Minimum Bedrooms"),
            gr.Slider(1, 3, value=1, step=0.5, label="Minimum Bathrooms"),
            gr.Slider(1000, 8000, value=3000, step=100, label="Maximum Price ($)")
        ],
        outputs=gr.HTML(label="Search Results"),
        title="🏠 SF Sublet & Furnished Apartment Finder",
        description="Search for sublets and furnished apartments in San Francisco",
        theme=gr.themes.Soft(),
        allow_flagging="never"
    )
    
    return interface

if __name__ == "__main__":
    print("Starting SF Apartment Bot...")
    print("Server will be available at: http://0.0.0.0:7862")
    print("Access from other devices on your network using your IP address")
    
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7862,       # Changed to port 7862
        share=False,            # Set to True if you want a public gradio link
        debug=True,             # Enable debug mode
        show_error=True         # Show errors in the interface
    )

