import requests
from bs4 import BeautifulSoup
import gradio as gr
import pandas as pd
import time
import json
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class SubletBot:
    def __init__(self):
        self.results = []
        print("SubletBot initialized")
        
        # Load environment variables from .env file
        self.load_environment()
        
        # Initialize LangChain for distance calculation
        self.setup_distance_chain()
    
    def load_environment(self):
        """Load environment variables from .env file"""
        try:
            # Try multiple .env file locations
            env_locations = [
                ".env",                    # Current directory
                "~/.env",                  # Home directory
                os.path.expanduser("~/.env"),  # Expanded home directory
                Path.home() / ".env",      # Using pathlib
            ]
            
            env_loaded = False
            for env_path in env_locations:
                env_path_str = str(env_path)
                if os.path.exists(env_path_str):
                    load_dotenv(env_path_str)
                    print(f"✅ Loaded environment variables from: {env_path_str}")
                    env_loaded = True
                    break
                else:
                    print(f"📁 Checked: {env_path_str} (not found)")
            
            if not env_loaded:
                print("⚠️  No .env file found. Checking for existing environment variables...")
            
            # Check if OPENAI_API_KEY is now available
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                print(f"✅ OPENAI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
            else:
                print("❌ OPENAI_API_KEY not found in environment variables")
                print("💡 Create a .env file with: OPENAI_API_KEY=your-key-here")
                
        except Exception as e:
            print(f"❌ Error loading environment: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_distance_chain(self):
        """Setup LangChain for distance calculations"""
        try:
            # Check if OpenAI API key is available (should be loaded from .env now)
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("❌ OPENAI_API_KEY still not found after loading .env")
                print("💡 Make sure your .env file contains: OPENAI_API_KEY=your-key-here")
                self.distance_chain = None
                return
            
            print(f"🔑 Using OpenAI API key: {api_key[:10]}...{api_key[-4:]}")
            
            # Initialize OpenAI LLM
            llm = OpenAI(
                temperature=0,  # Low temperature for consistent distance estimates
                max_tokens=50   # Short responses for distance only
            )
            
            # Create the distance calculation prompt template
            distance_template = """You are a real estate office assistant. Your client has asked you to calculate the distance from a reference address to a listing address. Provide approximations in tenths of miles.

Reference address: 1945 Broadway, San Francisco, CA
Listing location: {listing}

Return ONLY the distance in tenths of miles as a decimal number (e.g., 0.8, 1.2, 2.5). Do not include units or explanations."""

            prompt = PromptTemplate(
                input_variables=["listing"],
                template=distance_template
            )
            
            # Create the chain
            self.distance_chain = LLMChain(llm=llm, prompt=prompt)
            print("✅ Distance calculation chain initialized successfully")
            
        except Exception as e:
            print(f"❌ Error setting up distance chain: {e}")
            import traceback
            traceback.print_exc()
            self.distance_chain = None
    
    def extract_location_from_title(self, title):
        """Extract specific neighborhood from listing title"""
        # Convert to lowercase for matching
        title_lower = title.lower()
        
        # SF neighborhood patterns - look for these in the title
        neighborhoods = {
            'soma': 'SOMA',
            'south beach': 'South Beach',
            'mission': 'Mission',
            'castro': 'Castro',
            'haight': 'Haight-Ashbury',
            'lower haight': 'Lower Haight',
            'upper haight': 'Upper Haight',
            'nob hill': 'Nob Hill',
            'russian hill': 'Russian Hill',
            'pacific heights': 'Pacific Heights',
            'marina': 'Marina',
            'richmond': 'Richmond',
            'inner richmond': 'Inner Richmond',
            'outer richmond': 'Outer Richmond',
            'sunset': 'Sunset',
            'inner sunset': 'Inner Sunset',
            'outer sunset': 'Outer Sunset',
            'mission bay': 'Mission Bay',
            'financial district': 'Financial District',
            'fidi': 'Financial District',
            'chinatown': 'Chinatown',
            'north beach': 'North Beach',
            'tenderloin': 'Tenderloin',
            'hayes valley': 'Hayes Valley',
            'cole valley': 'Cole Valley',
            'noe valley': 'Noe Valley',
            'potrero hill': 'Potrero Hill',
            'dogpatch': 'Dogpatch',
            'bernal heights': 'Bernal Heights',
            'glen park': 'Glen Park',
            'excelsior': 'Excelsior',
            'visitacion valley': 'Visitacion Valley',
            'ucsf': 'UCSF/Parnassus',
            'parnassus': 'UCSF/Parnassus'
        }
        
        # Look for neighborhood matches
        for key, neighborhood in neighborhoods.items():
            if key in title_lower:
                print(f"🏘️  Found neighborhood '{neighborhood}' in title: {title}")
                return neighborhood
        
        # If no specific neighborhood found, return generic SF
        print(f"🏙️  No specific neighborhood found in: {title}")
        return 'San Francisco, CA'
    
    def sort_by_distance(self, listings):
        """Sort listings by distance, closest first"""
        def get_distance_value(listing):
            """Extract numeric distance value for sorting"""
            distance_str = listing.get('distance', 'N/A')
            
            # Handle various distance formats
            if distance_str in ['N/A', 'Unknown', 'Error']:
                return float('inf')  # Put these at the end
            
            # Extract number from "1.5 mi" format
            distance_match = re.search(r'(\d+\.?\d*)', str(distance_str))
            if distance_match:
                return float(distance_match.group(1))
            else:
                return float('inf')
        
        try:
            sorted_listings = sorted(listings, key=get_distance_value)
            
            # Print sorting results for debugging
            print("📍 Distance sorting results:")
            for i, listing in enumerate(sorted_listings[:5]):  # Show first 5
                print(f"  {i+1}. {listing['location']}: {listing['distance']}")
            
            return sorted_listings
            
        except Exception as e:
            print(f"❌ Error sorting by distance: {e}")
            return listings  # Return unsorted if sorting fails

    def calculate_distance(self, location):
        """Calculate distance from reference address to listing location"""
        if not self.distance_chain:
            print(f"❌ Distance chain not available for location: {location}")
            return "N/A"
        
        try:
            print(f"🔍 Calculating distance for location: '{location}'")
            
            # Run the LangChain to get distance
            result = self.distance_chain.run(listing=location)
            print(f"🤖 OpenAI response: '{result}'")
            
            # Clean up the result - strip whitespace and extract number
            cleaned_result = result.strip()
            print(f"🧹 Cleaned response: '{cleaned_result}'")
            
            # More flexible regex to handle various formats
            distance_match = re.search(r'(\d+\.?\d*)', cleaned_result)
            if distance_match:
                distance = float(distance_match.group(1))
                final_result = f"{distance} mi"
                print(f"✅ Parsed distance: {final_result}")
                return final_result
            else:
                print(f"❌ Could not parse distance from: '{cleaned_result}'")
                return "Unknown"
                
        except Exception as e:
            print(f"❌ Error calculating distance for {location}: {e}")
            import traceback
            traceback.print_exc()
            return "Error"
    
    def search_craigslist(self, bedrooms, bathrooms, max_price=5000):
        """Search Craigslist SF Bay Area for real listings"""
        print(f"=== SEARCH STARTED ===")
        print(f"Parameters: {bedrooms}BR, {bathrooms}BA, max ${max_price}")
        
        base_url = "https://sfbay.craigslist.org/search/sfc/sub"
        
        params = {
            'min_bedrooms': bedrooms,
            'min_bathrooms': bathrooms,
            'max_price': max_price,
            'availabilityMode': 0,
            'sale_date': 'all dates'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"Making request to: {base_url}")
        print(f"With params: {params}")
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response length: {len(response.content)} bytes")
            
            if response.status_code != 200:
                print(f"Bad response: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"BeautifulSoup created, parsing HTML...")
            
            # Debug: Let's see what the actual HTML structure looks like
            listings = []
            
            # Check for various possible listing containers
            possible_selectors = [
                ('li', 'cl-search-result'),
                ('li', 'result-row'),
                ('div', 'cl-search-result'),
                ('div', 'result-row'),
                ('li', None),  # Any li element
                ('div', 'result-info'),
                ('article', None),
                ('section', None)
            ]
            
            print("=== DEBUGGING HTML STRUCTURE ===")
            for tag, class_name in possible_selectors:
                if class_name:
                    elements = soup.find_all(tag, class_=class_name)
                    print(f"Found {len(elements)} <{tag} class='{class_name}'> elements")
                else:
                    elements = soup.find_all(tag)
                    print(f"Found {len(elements)} <{tag}> elements total")
                
                if elements and len(elements) > 0:
                    print(f"Sample {tag} element: {str(elements[0])[:300]}...")
                    print("---")
            
            # Let's also check what classes are actually being used
            all_elements_with_classes = soup.find_all(attrs={'class': True})
            all_classes = set()
            for elem in all_elements_with_classes:
                classes = elem.get('class', [])
                if isinstance(classes, list):
                    all_classes.update(classes)
                else:
                    all_classes.add(classes)
            
            print(f"All CSS classes found on page: {sorted(list(all_classes))[:20]}...")  # Show first 20
            
            # Try current Craigslist structure
            search_results = soup.find_all('li', class_='cl-search-result')
            print(f"Found {len(search_results)} cl-search-result elements")
            
            if not search_results:
                # Try other common patterns
                search_results = soup.find_all('li', class_='result-row')
                print(f"Found {len(search_results)} result-row elements")
                
            if not search_results:
                # Look for any div that might contain listing data
                search_results = soup.find_all('div', attrs={'data-pid': True})
                print(f"Found {len(search_results)} elements with data-pid")
                
            if not search_results:
                # Look for links that might be listings
                all_links = soup.find_all('a', href=True)
                listing_links = [link for link in all_links if '/sub/' in link.get('href', '')]
                print(f"Found {len(listing_links)} links containing '/sub/'")
                if listing_links:
                    print(f"Sample listing link: {listing_links[0]}")
                    # Convert these links to fake results for now
                    search_results = listing_links[:10]
            
            for result in search_results[:10]:  # Limit to first 10 results
                try:
                    # Handle different types of elements
                    if result.name == 'a':  # If we're working with direct links
                        title = result.get_text(strip=True)
                        url = result.get('href', '')
                        
                        # Try to extract price from title for direct links too
                        price_match = re.search(r'\$[\d,]+', title)
                        if price_match:
                            price = price_match.group()
                            # Clean title by removing price
                            title = re.sub(r'\$[\d,]+', '', title).strip()
                            print(f"Extracted price {price} from link title")
                        else:
                            price = 'See listing'
                        
                        # Extract location from title
                        location = self.extract_location_from_title(title)
                        posted = 'Recent'
                    else:
                        # Extract title and URL from container elements
                        title_link = (result.find('a', class_='cl-app-anchor') or 
                                    result.find('a', class_='result-title') or
                                    result.find('a', href=True))
                        
                        if not title_link:
                            print(f"No title link found in: {str(result)[:200]}...")
                            continue
                        
                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')
                        
                        # Extract price with multiple possible selectors
                        price_elem = (result.find('span', class_='priceinfo') or 
                                    result.find('span', class_='result-price') or
                                    result.find('span', class_='price') or
                                    result.find(string=re.compile(r'\$\d+')))
                        
                        if isinstance(price_elem, str):
                            price = price_elem.strip()
                        elif price_elem:
                            price = price_elem.get_text(strip=True)
                        else:
                            # If no separate price element, try to extract from title
                            price_match = re.search(r'\$[\d,]+', title)
                            if price_match:
                                price = price_match.group()
                                # Clean title by removing price
                                title = re.sub(r'\$[\d,]+', '', title).strip()
                                print(f"Extracted price {price} from title")
                            else:
                                price = 'Price not listed'
                        
                        # Extract location with multiple possible selectors
                        location_elem = (result.find('span', class_='supertitle') or 
                                       result.find('span', class_='result-hood') or
                                       result.find('span', class_='nearby'))
                        
                        if location_elem:
                            location = location_elem.get_text(strip=True)
                        else:
                            # Try to extract location from title - look for neighborhood info
                            location = self.extract_location_from_title(title)
                        
                        location = location.strip('() ')
                        
                        # Clean up title - remove trailing dashes and extra spaces
                        title = re.sub(r'\s*-\s*$', '', title).strip()
                        title = re.sub(r'\s+', ' ', title)
                        
                        # Extract posting time
                        time_elem = result.find('time') or result.find('span', class_='result-date')
                        posted = time_elem.get('datetime') or time_elem.get_text(strip=True) if time_elem else 'Recent'
                    
                    # Make sure URL is absolute
                    if url.startswith('/'):
                        url = 'https://sfbay.craigslist.org' + url
                    elif not url.startswith('http'):
                        url = 'https://sfbay.craigslist.org' + url
                    
                    # Extract bedroom/bathroom info from title if possible
                    br_match = re.search(r'(\d+)\s*br', title.lower())
                    ba_match = re.search(r'(\d+(?:\.\d+)?)\s*ba', title.lower())
                    
                    listing = {
                        'site': 'Craigslist',
                        'title': title,
                        'price': price,
                        'url': url,
                        'bedrooms': br_match.group(1) if br_match else f"{bedrooms}+",
                        'bathrooms': ba_match.group(1) if ba_match else f"{bathrooms}+",
                        'location': location,
                        'square_feet': 'N/A',
                        'amenities': [],
                        'description': title,  # Use title as description for now
                        'posted': posted,
                        'distance': self.calculate_distance(location)  # Add distance calculation
                    }
                    
                    listings.append(listing)
                    print(f"Added listing: {title[:50]}...")
                    
                except Exception as e:
                    print(f"Error parsing individual result: {e}")
                    print(f"Result HTML: {str(result)[:300]}...")
                    continue
            
            print(f"=== SEARCH COMPLETED ===")
            print(f"Successfully parsed {len(listings)} listings")
            
            # Sort listings by distance (closest first)
            if listings:
                print("🔄 Sorting listings by distance...")
                listings = self.sort_by_distance(listings)
                print("✅ Listings sorted by closest distance first")
            
            # If no listings found, return debug info
            if not listings:
                # Check if page has any content at all
                all_links = soup.find_all('a')
                print(f"Page has {len(all_links)} total links")
                
                # Return debug listing
                debug_listing = {
                    'site': 'Craigslist',
                    'title': f'DEBUG: No listings found. Page has {len(all_links)} links total.',
                    'price': 'N/A',
                    'url': response.url,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'location': 'Debug Mode',
                    'square_feet': 'N/A',
                    'amenities': [],
                    'description': f'Response status: {response.status_code}, Content length: {len(response.content)}',
                    'posted': 'Now',
                    'distance': 'N/A'
                }
                return [debug_listing]
            
            return listings
            
        except Exception as e:
            print(f"Error in search_craigslist: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error as listing for debugging
            error_listing = {
                'site': 'Error',
                'title': f'Search Error: {str(e)}',
                'price': 'N/A',
                'url': '#',
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'location': 'Error',
                'square_feet': 'N/A',
                'amenities': [],
                'description': f'Full error: {traceback.format_exc()}',
                'posted': 'Error',
                'distance': 'N/A'
            }
            return [error_listing]
    
    def format_results(self, all_results):
        """Format results for display"""
        print(f"Formatting {len(all_results)} results")
        
        if not all_results:
            return "<p>No listings found matching your criteria.</p>"
        
        html_output = "<div style='max-height: 600px; overflow-y: auto;'>"
        
        for result in all_results:
            html_output += f"""
            <div style='border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px;'>
                <h3 style='margin: 0 0 10px 0; color: #333;'>{result['title']}</h3>
                <p><strong>Price:</strong> {result['price']}</p>
                <p><strong>Bedrooms:</strong> {result['bedrooms']} | <strong>Bathrooms:</strong> {result['bathrooms']}</p>
                <p><strong>Location:</strong> {result['location']} | <strong>Distance from 1945 Broadway:</strong> {result['distance']}</p>
                <p><strong>Source:</strong> {result['site']}</p>
                <a href="{result['url']}" target="_blank" style='color: #007bff; text-decoration: none;'>View Listing →</a>
            </div>
            """
        
        html_output += "</div>"
        return html_output

def search_apartments(bedrooms, bathrooms, max_price):
    """Main search function for Gradio interface"""
    print(f"=== GRADIO FUNCTION CALLED ===")
    print(f"Inputs: bedrooms={bedrooms}, bathrooms={bathrooms}, max_price={max_price}")
    
    bot = SubletBot()
    
    results = []
    print(f"Calling bot.search_craigslist...")
    
    results.extend(bot.search_craigslist(bedrooms, bathrooms, max_price))
    
    print(f"Search completed. Found {len(results)} listings")
    
    formatted_results = bot.format_results(results)
    print(f"Results formatted. Output length: {len(formatted_results)} characters")
    
    return formatted_results

def create_interface():
    print("Creating Gradio interface...")
    
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
    print("=== STARTING APPLICATION ===")
    print("Starting SF Apartment Bot...")
    print("Server will be available at: http://0.0.0.0:7862")
    
    app = create_interface()
    print("Launching Gradio app...")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=True,
        show_error=True
    )
