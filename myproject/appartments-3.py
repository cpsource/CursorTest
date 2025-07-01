import requests
from bs4 import BeautifulSoup
import gradio as gr
import pandas as pd
import time
import json
import re

class SubletBot:
    def __init__(self):
        self.results = []
    
    def search_craigslist(self, bedrooms, bathrooms, max_price=5000):
        """Search Craigslist SF Bay Area using JSON-LD data"""
        base_url = "https://sfbay.craigslist.org/search/sfc/sub"
        
        params = {
            'min_bedrooms': bedrooms,
            'min_bathrooms': bathrooms,
            'max_price': max_price,
            'availabilityMode': 0,
            'sale_date': 'all dates'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the JSON-LD script tag
            json_script = soup.find('script', {'id': 'ld_searchpage_results', 'type': 'application/ld+json'})
            
            if not json_script:
                print("No JSON-LD data found")
                return []
            
            # Parse the JSON data
            json_data = json.loads(json_script.string)
            print(f"Found {len(json_data.get('itemListElement', []))} items in JSON data")
            
            listings = []
            for item_data in json_data.get('itemListElement', []):
                item = item_data.get('item', {})
                
                # Extract the data we need
                name = item.get('name', 'No title')
                num_bedrooms = item.get('numberOfBedrooms', 'N/A')
                num_bathrooms = item.get('numberOfBathroomsTotal', 'N/A')
                address = item.get('address', {})
                locality = address.get('addressLocality', 'Unknown')
                
                # Extract price from the name if it contains $
                price = "Price not listed"
                price_match = re.search(r'\$[\d,]+', name)
                if price_match:
                    price = price_match.group()
                
                # We need to construct the URL - this requires finding the actual listing URL
                # For now, we'll use a placeholder
                listing_url = f"https://sfbay.craigslist.org/search/sfc/sub"  # This needs to be improved
                
                listing = {
                    'site': 'Craigslist',
                    'title': name,
                    'price': price,
                    'url': listing_url,
                    'bedrooms': num_bedrooms,
                    'bathrooms': num_bathrooms,
                    'location': locality
                }
                listings.append(listing)
                
                # Debug print for first few items
                if len(listings) <= 3:
                    print(f"Listing {len(listings)}: {name}")
                    print(f"  Bedrooms: {num_bedrooms}, Bathrooms: {num_bathrooms}")
                    print(f"  Location: {locality}")
                    print(f"  Price: {price}")
                    print("---")
            
            return listings
            
        except Exception as e:
            print(f"Error searching Craigslist: {e}")
            return []
    
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
                <p><strong>Location:</strong> {result['location']}</p>
                <p><strong>Source:</strong> {result['site']}</p>
                <a href="{result['url']}" target="_blank" style='color: #007bff; text-decoration: none;'>View Listing →</a>
            </div>
            """
        
        html_output += "</div>"
        return html_output

def search_apartments(bedrooms, bathrooms, max_price):
    """Main search function for Gradio interface"""
    bot = SubletBot()
    
    results = []
    print(f"Searching for {bedrooms}BR/{bathrooms}BA apartments, max ${max_price}")
    
    results.extend(bot.search_craigslist(bedrooms, bathrooms, max_price))
    
    time.sleep(2)
    
    print(f"Found {len(results)} listings")
    return bot.format_results(results)

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
    
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=True,
        show_error=True
    )

