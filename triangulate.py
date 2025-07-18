import os
import re
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class FacilityLocator:
    def __init__(self):
        print("FacilityLocator initialized")
        
        # Load environment variables from .env file
        self.load_environment()
        
        # Initialize LangChain for location estimation and distance calculation
        self.setup_chains()
    
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
    
    def setup_chains(self):
        """Setup LangChain for location estimation and distance calculation"""
        try:
            # Check if OpenAI API key is available
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("❌ OPENAI_API_KEY not found")
                self.location_chain = None
                self.distance_chain = None
                return
            
            print(f"🔑 Using OpenAI API key: {api_key[:10]}...{api_key[-4:]}")
            
            # Initialize OpenAI LLM
            llm = OpenAI(
                temperature=0,  # Low temperature for consistent estimates
                max_tokens=100   # Enough for address responses
            )
            
            # Location estimation prompt template
            location_template = """You are a San Francisco local expert. Given a facility name, provide the most likely full address or location in San Francisco.

Facility name: {facility_name}

Return the most likely address or location in this format: "Street Address, San Francisco, CA" or "Neighborhood, San Francisco, CA". Be as specific as possible. If you know the exact address, provide it. If not, provide the neighborhood or general area.

Examples:
- "UCSF Medical Center" → "505 Parnassus Ave, San Francisco, CA"
- "California Pacific Medical Center" → "2333 Buchanan St, San Francisco, CA"
- "Laguna Honda Hospital" → "375 Laguna Honda Blvd, San Francisco, CA"

Response:"""

            location_prompt = PromptTemplate(
                input_variables=["facility_name"],
                template=location_template
            )
            
            # Distance calculation prompt template
            distance_template = """You are a real estate office assistant. Calculate the distance between two addresses in San Francisco. Provide approximations in tenths of miles.

From address: {from_address}
To address: {to_address}

Return ONLY the distance in tenths of miles as a decimal number (e.g., 0.8, 1.2, 2.5). Do not include units or explanations."""

            distance_prompt = PromptTemplate(
                input_variables=["from_address", "to_address"],
                template=distance_template
            )
            
            # Create the chains
            self.location_chain = LLMChain(llm=llm, prompt=location_prompt)
            self.distance_chain = LLMChain(llm=llm, prompt=distance_prompt)
            print("✅ Location and distance chains initialized successfully")
            
        except Exception as e:
            print(f"❌ Error setting up chains: {e}")
            import traceback
            traceback.print_exc()
            self.location_chain = None
            self.distance_chain = None
    
    def parse_facilities_text(self, text):
        """Parse the facilities text to extract facility names and distances"""
        print(f"📋 Parsing facilities text...")
        
        facilities = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.lower().startswith('closest facilities'):
                continue
            
            # Look for patterns like "Facility Name" followed by "X.XX miles away"
            # Handle various formats including multi-line entries
            
            # Pattern 1: "Facility Name\nX.XX miles away"
            distance_match = re.search(r'(\d+\.?\d*)\s*miles?\s*away', line, re.IGNORECASE)
            
            if distance_match:
                reported_distance = distance_match.group(1)
                # The facility name is everything before the distance
                facility_name = re.sub(r'\s*\d+\.?\d*\s*miles?\s*away.*$', '', line, flags=re.IGNORECASE).strip()
                
                if facility_name:
                    facilities.append({
                        'name': facility_name,
                        'reported_distance': float(reported_distance)
                    })
                    print(f"  📍 Found: {facility_name} ({reported_distance} miles)")
            else:
                # Check if this line might be a facility name without distance on same line
                # Look ahead to next lines for distance
                potential_name = line.strip()
                if len(potential_name) > 3 and not re.search(r'\d+\.?\d*\s*miles', potential_name):
                    # This might be a facility name, distance could be on next line
                    facilities.append({
                        'name': potential_name,
                        'reported_distance': None
                    })
                    print(f"  📝 Potential facility: {potential_name}")
        
        # Try alternative parsing if we didn't find much
        if len(facilities) < 2:
            print("🔄 Trying alternative parsing...")
            # Split by common separators and look for facility-like names
            text_clean = re.sub(r'closest facilities', '', text, flags=re.IGNORECASE)
            
            # Split by distances and extract names
            distance_pattern = r'(\d+\.?\d*)\s*miles?\s*away'
            parts = re.split(distance_pattern, text_clean, flags=re.IGNORECASE)
            
            facilities = []
            for i in range(0, len(parts)-1, 2):
                if i+1 < len(parts):
                    facility_text = parts[i].strip()
                    distance_text = parts[i+1].strip()
                    
                    # Clean up facility name
                    facility_name = re.sub(r'[^\w\s&\-\.]', ' ', facility_text)
                    facility_name = ' '.join(facility_name.split())
                    
                    if len(facility_name) > 3:
                        try:
                            distance = float(distance_text)
                            facilities.append({
                                'name': facility_name,
                                'reported_distance': distance
                            })
                            print(f"  📍 Alternative parse: {facility_name} ({distance} miles)")
                        except ValueError:
                            continue
        
        print(f"✅ Parsed {len(facilities)} facilities")
        return facilities
    
    def estimate_location(self, facility_name):
        """Estimate the location of a facility using AI"""
        if not self.location_chain:
            return f"{facility_name}, San Francisco, CA"
        
        try:
            print(f"🔍 Estimating location for: {facility_name}")
            
            result = self.location_chain.run(facility_name=facility_name)
            estimated_location = result.strip()
            
            print(f"🎯 Estimated location: {estimated_location}")
            return estimated_location
            
        except Exception as e:
            print(f"❌ Error estimating location for {facility_name}: {e}")
            return f"{facility_name}, San Francisco, CA"
    
    def calculate_distance(self, from_address, to_address):
        """Calculate distance between two addresses"""
        if not self.distance_chain:
            return "N/A"
        
        try:
            print(f"📏 Calculating distance from '{from_address}' to '{to_address}'")
            
            result = self.distance_chain.run(
                from_address=from_address,
                to_address=to_address
            )
            
            # Clean up the result
            cleaned_result = result.strip()
            distance_match = re.search(r'(\d+\.?\d*)', cleaned_result)
            
            if distance_match:
                distance = float(distance_match.group(1))
                print(f"✅ Calculated distance: {distance} miles")
                return distance
            else:
                print(f"❌ Could not parse distance from: '{cleaned_result}'")
                return "Unable to calculate"
                
        except Exception as e:
            print(f"❌ Error calculating distance: {e}")
            return "Error"
    
    def process_facilities(self, facilities_text, reference_address="1945 Broadway, San Francisco, CA"):
        """Process the entire facilities text and return results"""
        print(f"=== PROCESSING FACILITIES ===")
        
        # Parse facilities from text
        facilities = self.parse_facilities_text(facilities_text)
        
        if not facilities:
            return "No facilities found in the provided text. Please check the format."
        
        results = []
        
        for facility in facilities:
            print(f"\n--- Processing: {facility['name']} ---")
            
            # Estimate location
            estimated_location = self.estimate_location(facility['name'])
            
            # Calculate distance from reference
            calculated_distance = self.calculate_distance(reference_address, estimated_location)
            
            # Compare with reported distance if available
            reported = facility.get('reported_distance')
            
            result = {
                'name': facility['name'],
                'estimated_location': estimated_location,
                'calculated_distance': calculated_distance,
                'reported_distance': reported,
                'reference_address': reference_address
            }
            
            results.append(result)
        
        return self.format_results(results)
    
    def format_results(self, results):
        """Format results for display"""
        if not results:
            return "No results to display."
        
        output = f"**📍 Reference Address:** {results[0]['reference_address']}\n\n"
        output += "**🏥 Facility Analysis:**\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"**{i}. {result['name']}**\n"
            output += f"   📍 **Estimated Location:** {result['estimated_location']}\n"
            
            if isinstance(result['calculated_distance'], (int, float)):
                output += f"   📏 **Calculated Distance:** {result['calculated_distance']} miles\n"
            else:
                output += f"   📏 **Calculated Distance:** {result['calculated_distance']}\n"
            
            if result['reported_distance']:
                output += f"   📊 **Original Distance:** {result['reported_distance']} miles\n"
                
                # Compare distances if both available
                if isinstance(result['calculated_distance'], (int, float)):
                    diff = abs(result['calculated_distance'] - result['reported_distance'])
                    if diff <= 0.5:
                        output += f"   ✅ **Match:** Close estimate (±{diff:.1f} miles)\n"
                    else:
                        output += f"   ⚠️ **Difference:** {diff:.1f} miles variance\n"
            
            output += "\n"
        
        return output

# Create a global locator instance
global_locator = None

def get_locator():
    """Get or create the global locator instance"""
    global global_locator
    if global_locator is None:
        print("🏥 Creating new FacilityLocator instance...")
        global_locator = FacilityLocator()
    return global_locator

def process_facilities_gradio(facilities_text):
    """Main processing function for Gradio interface"""
    print(f"=== FACILITY PROCESSING STARTED ===")
    
    # Use the global locator instance
    locator = get_locator()
    
    # Validate input
    if not facilities_text or len(facilities_text.strip()) < 10:
        return "Please paste the facilities text to analyze."
    
    # Process facilities
    results = locator.process_facilities(facilities_text)
    
    print(f"Facility processing completed")
    return results

def create_interface():
    """Create Gradio interface for facility location analysis"""
    print("Creating Facility Locator interface...")
    
    # Custom CSS for better styling
    css = """
    .facility-input {
        font-family: monospace;
        font-size: 14px;
    }
    .reference-address {
        font-size: 16px;
        font-weight: bold;
        color: #2e7d32;
        background-color: #e8f5e8;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(css=css, theme=gr.themes.Soft(), title="SF Facility Locator") as demo:
        gr.Markdown("# 🏥 San Francisco Facility Location Analyzer")
        gr.Markdown("Analyze facility lists, estimate locations, and calculate distances from reference point")
        
        # Reference address display
        with gr.Row():
            gr.HTML("""
                <div class="reference-address">
                    📍 Reference Address: 1945 Broadway, San Francisco, CA
                </div>
            """)
        
        with gr.Row():
            with gr.Column():
                facilities_input = gr.Textbox(
                    label="🏥 Facilities Text",
                    placeholder="""Paste your facilities text here, e.g.:
Closest facilities
Laguna Honda Hospital & Rehabilitation Center
1.64 miles away
UCSF Medical Center
2.6 miles away
California Pacific Medical Ctr - St. Lukes Campus
2.76 miles away""",
                    lines=10,
                    elem_classes=["facility-input"],
                    info="Paste the facility list with distances"
                )
                
                process_btn = gr.Button(
                    "🔍 Analyze Facilities",
                    variant="primary",
                    size="lg"
                )
        
        with gr.Row():
            results_output = gr.Markdown(
                label="📊 Analysis Results",
                value="Results will appear here after processing..."
            )
        
        # Example data
        gr.Markdown("### 💡 Example Input:")
        example_text = """Closest facilities
Laguna Honda Hospital & Rehabilitation Center
1.64 miles away
UCSF Medical Center
2.6 miles away
California Pacific Medical Ctr - St. Lukes Campus
2.76 miles away
Seton Medical Center
3.21 miles away
California Pacific Medical Ctr-Davies Campus Hosp
3.32 miles away"""
        
        with gr.Row():
            gr.Textbox(
                value=example_text,
                label="Sample Input Format",
                interactive=False,
                lines=8,
                elem_classes=["facility-input"]
            )
        
        with gr.Row():
            load_example_btn = gr.Button("📋 Load Example", size="sm")
        
        # Button click handlers
        process_btn.click(
            fn=process_facilities_gradio,
            inputs=[facilities_input],
            outputs=[results_output]
        )
        
        load_example_btn.click(
            lambda: example_text,
            outputs=[facilities_input]
        )
    
    return demo

if __name__ == "__main__":
    print("=== STARTING FACILITY LOCATOR ===")
    print("San Francisco Facility Location Analyzer")
    print("Server will be available at: http://0.0.0.0:7864")
    
    app = create_interface()
    print("Launching Facility Locator...")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7864,
        share=False,
        debug=True,
        show_error=True
    )
