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
                self.triangulation_chain = None
                self.distance_chain = None
                return
            
            print(f"🔑 Using OpenAI API key: {api_key[:10]}...{api_key[-4:]}")
            
            # Initialize OpenAI LLM with higher token limit for detailed responses
            llm = OpenAI(
                temperature=0,  # Low temperature for consistent estimates
                max_tokens=500   # Higher limit for detailed triangulation analysis
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

            # NEW: Enhanced triangulation prompt template
            triangulation_template = """You are a geographic analyst and cartographer specializing in San Francisco. Given a list of known facilities and their distances from an unknown location, determine the most likely location that satisfies all these distance constraints. Provide a comprehensive analysis similar to a professional geographic survey.

Known facilities and distances from unknown location:
{facility_distances}

Reference location for final distance calculation: {reference_location}

Task: Perform a detailed triangulation analysis to find the mythical location that satisfies all distance constraints. Follow this format:

## 🧭 Mythical Location: **"[Creative Name for the Location]"**

**🎯 Coordinates:** [Estimated latitude/longitude coordinates]
Situated in **[Specific neighborhood/area]**, this location lies roughly central to the facilities listed:

* [Facility 1]: ~[distance] miles
* [Facility 2]: ~[distance] miles  
* [Facility 3]: ~[distance] miles
[etc. for all facilities]

This makes it an ideal "mythical convergence point" because [brief explanation of why this location works geometrically].

## 📏 Distance to Reference Location

The reference address, **{reference_location}**, is located approximately at:
* **[Estimated coordinates]**

Using triangulation geometry:
* **Mythical Location** ([coordinates])
* **Reference Location** ([coordinates])

→ **Approximate distance**: **[X.X] miles** (rounded to the nearest tenth)

## ✅ Summary

| Location | Distance to {reference_location} |
|----------|----------------------------------|
| [Mythical Location Name] | **[X.X] miles** |

Provide specific coordinates, real SF neighborhood names, and geometric reasoning for your triangulation. Be precise and professional like a geographic survey report.

Your triangulated location analysis:"""

            distance_template = """You are a real estate office assistant. Calculate the distance between two addresses in San Francisco. Provide approximations in tenths of miles.

From address: {from_address}
To address: {to_address}

Return ONLY the distance in tenths of miles as a decimal number (e.g., 0.8, 1.2, 2.5). Do not include units or explanations."""

            location_prompt = PromptTemplate(
                input_variables=["facility_name"],
                template=location_template
            )
            
            triangulation_prompt = PromptTemplate(
                input_variables=["facility_distances", "reference_location"],
                template=triangulation_template
            )
            
            distance_prompt = PromptTemplate(
                input_variables=["from_address", "to_address"],
                template=distance_template
            )
            
            # Create the chains
            self.location_chain = LLMChain(llm=llm, prompt=location_prompt)
            self.triangulation_chain = LLMChain(llm=llm, prompt=triangulation_prompt)
            self.distance_chain = LLMChain(llm=llm, prompt=distance_prompt)
            print("✅ Location, triangulation, and distance chains initialized successfully")
            
        except Exception as e:
            print(f"❌ Error setting up chains: {e}")
            import traceback
            traceback.print_exc()
            self.location_chain = None
            self.triangulation_chain = None
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
            print(f"❌ Location chain not available for: {facility_name}")
            return f"{facility_name}, San Francisco, CA"
        
        try:
            print(f"🔍 Estimating location for: '{facility_name}'")
            
            result = self.location_chain.run(facility_name=facility_name)
            estimated_location = result.strip()
            
            print(f"🎯 AI estimated location: '{estimated_location}'")
            
            # Validate response
            if len(estimated_location) < 5:
                print(f"⚠️  Warning: Estimated location seems too short")
                estimated_location = f"{facility_name}, San Francisco, CA"
            
            return estimated_location
            
        except Exception as e:
            print(f"❌ Error estimating location for {facility_name}: {e}")
            import traceback
            traceback.print_exc()
            return f"{facility_name}, San Francisco, CA"
    
    def calculate_distance(self, from_address, to_address):
        """Calculate distance between two addresses"""
        if not self.distance_chain:
            print(f"❌ Distance chain not available")
            return "N/A"
        
        try:
            print(f"📏 Calculating distance...")
            print(f"   From: '{from_address}'")
            print(f"   To: '{to_address}'")
            
            result = self.distance_chain.run(
                from_address=from_address,
                to_address=to_address
            )
            
            print(f"🤖 Distance AI raw response: '{result}'")
            
            # Clean up the result
            cleaned_result = result.strip()
            print(f"🧹 Cleaned distance response: '{cleaned_result}'")
            
            distance_match = re.search(r'(\d+\.?\d*)', cleaned_result)
            
            if distance_match:
                distance = float(distance_match.group(1))
                print(f"✅ Parsed distance: {distance} miles")
                return distance
            else:
                print(f"❌ Could not parse distance from: '{cleaned_result}'")
                return "Unable to calculate"
                
        except Exception as e:
            print(f"❌ Error calculating distance: {e}")
            import traceback
            traceback.print_exc()
            return "Error"
    
    def triangulate_location(self, facilities, reference_location):
        """Triangulate the mythical location based on facility distances"""
        if not self.triangulation_chain:
            print("❌ Triangulation chain not available")
            return "Unable to triangulate - AI not configured"
        
        try:
            print(f"🎯 Starting triangulation with {len(facilities)} constraints...")
            print(f"📍 Reference location: {reference_location}")
            
            # Build the facility distances string for the prompt
            facility_distances_text = ""
            print("\n--- Building facility constraints ---")
            
            for i, facility in enumerate(facilities, 1):
                print(f"🏥 {i}. Processing facility: {facility['name']}")
                print(f"   📏 Reported distance: {facility['reported_distance']} miles")
                
                estimated_location = self.estimate_location(facility['name'])
                print(f"   📍 Estimated location: {estimated_location}")
                
                distance = facility['reported_distance']
                facility_distances_text += f"- {facility['name']} ({estimated_location}): {distance} miles away\n"
            
            print(f"\n--- Final facility constraints text ---")
            print(f"📋 Facility distances text for AI:\n{facility_distances_text}")
            
            print(f"\n--- Calling triangulation AI ---")
            print(f"🤖 Sending to OpenAI for triangulation...")
            
            # Debug the exact prompt being sent
            full_prompt = f"""You are a geographic analyst and cartographer specializing in San Francisco. Given a list of known facilities and their distances from an unknown location, determine the most likely location that satisfies all these distance constraints. Provide a comprehensive analysis similar to a professional geographic survey.

Known facilities and distances from unknown location:
{facility_distances_text}

Reference location for final distance calculation: {reference_location}

Task: Perform a detailed triangulation analysis to find the mythical location that satisfies all distance constraints. Follow this format:

## 🧭 Mythical Location: **"[Creative Name for the Location]"**

**🎯 Coordinates:** [Estimated latitude/longitude coordinates]
Situated in **[Specific neighborhood/area]**, this location lies roughly central to the facilities listed:

* [Facility 1]: ~[distance] miles
* [Facility 2]: ~[distance] miles  
* [Facility 3]: ~[distance] miles
[etc. for all facilities]

This makes it an ideal "mythical convergence point" because [brief explanation of why this location works geometrically].

## 📏 Distance to Reference Location

The reference address, **{reference_location}**, is located approximately at:
* **[Estimated coordinates]**

Using triangulation geometry:
* **Mythical Location** ([coordinates])
* **Reference Location** ([coordinates])

→ **Approximate distance**: **[X.X] miles** (rounded to the nearest tenth)

## ✅ Summary

| Location | Distance to {reference_location} |
|----------|----------------------------------|
| [Mythical Location Name] | **[X.X] miles** |

Provide specific coordinates, real SF neighborhood names, and geometric reasoning for your triangulation. Be precise and professional like a geographic survey report.

Your triangulated location analysis:"""
            
            print(f"📝 Full prompt being sent:")
            print(f"=" * 50)
            print(full_prompt)
            print(f"=" * 50)
            
            # Run triangulation
            result = self.triangulation_chain.run(
                facility_distances=facility_distances_text,
                reference_location=reference_location
            )
            
            print(f"\n--- AI Response ---")
            print(f"🤖 Raw AI response: '{result}'")
            
            triangulated_location = result.strip()
            print(f"🎯 Cleaned triangulated location: '{triangulated_location}'")
            
            if len(triangulated_location) < 10:
                print(f"⚠️  Warning: Response seems too short")
            
            return triangulated_location
            
        except Exception as e:
            print(f"❌ Error in triangulate_location: {e}")
            import traceback
            traceback.print_exc()
            return f"Error in triangulation: {str(e)}"
    
    def process_facilities(self, facilities_text, reference_address="1945 Broadway, San Francisco, CA"):
        """Process the entire facilities text and triangulate the mythical location"""
        print(f"\n" + "="*60)
        print(f"=== TRIANGULATION ANALYSIS STARTED ===")
        print(f"="*60)
        
        print(f"📝 Input text length: {len(facilities_text)} characters")
        print(f"📍 Reference address: {reference_address}")
        
        # Parse facilities from text
        print(f"\n--- STEP 1: PARSING FACILITIES ---")
        facilities = self.parse_facilities_text(facilities_text)
        
        if not facilities:
            print(f"❌ No facilities parsed from input")
            return "No facilities found in the provided text. Please check the format."
        
        print(f"✅ Parsed {len(facilities)} total facilities")
        
        # Filter out facilities without distances
        facilities_with_distances = [f for f in facilities if f.get('reported_distance') is not None]
        
        print(f"📊 Facilities with distances: {len(facilities_with_distances)}")
        print(f"📊 Facilities without distances: {len(facilities) - len(facilities_with_distances)}")
        
        if len(facilities_with_distances) < 2:
            print(f"❌ Insufficient facilities for triangulation")
            return "Need at least 2 facilities with distances for triangulation."
        
        print(f"✅ Using {len(facilities_with_distances)} facilities for triangulation")
        
        # Debug each facility
        print(f"\n--- FACILITIES TO BE USED ---")
        for i, facility in enumerate(facilities_with_distances, 1):
            print(f"{i}. {facility['name']} - {facility['reported_distance']} miles")
        
        # Triangulate the mythical location
        print(f"\n--- STEP 2: TRIANGULATION ---")
        triangulated_location = self.triangulate_location(facilities_with_distances, reference_address)
        print(f"🎯 Final triangulated location: '{triangulated_location}'")
        
        # Calculate distance from triangulated location to reference
        print(f"\n--- STEP 3: FINAL DISTANCE CALCULATION ---")
        distance_to_reference = self.calculate_distance(triangulated_location, reference_address)
        print(f"📏 Final distance to reference: {distance_to_reference}")
        
        # Build results
        result = {
            'facilities': facilities_with_distances,
            'triangulated_location': triangulated_location,
            'reference_address': reference_address,
            'distance_to_reference': distance_to_reference
        }
        
        print(f"\n--- STEP 4: FORMATTING RESULTS ---")
        formatted_results = self.format_triangulation_results(result)
        print(f"✅ Results formatted successfully")
        
        print(f"\n" + "="*60)
        print(f"=== TRIANGULATION ANALYSIS COMPLETED ===")
        print(f"="*60)
        
        return formatted_results
    
    def format_triangulation_results(self, result):
        """Format triangulation results for display - now expects detailed AI analysis"""
        output = f"**🎯 LOCATION TRIANGULATION ANALYSIS**\n\n"
        
        output += f"**📍 Input Reference:** {result['reference_address']}\n\n"
        
        output += f"**🔍 Triangulation Constraints Used:**\n"
        for i, facility in enumerate(result['facilities'], 1):
            output += f"{i}. **{facility['name']}** - {facility['reported_distance']} miles away\n"
        
        output += f"\n**🎯 AI TRIANGULATION ANALYSIS:**\n\n"
        
        # The triangulated_location now contains the full AI analysis
        if isinstance(result['triangulated_location'], str) and len(result['triangulated_location']) > 50:
            # AI provided detailed analysis - display it directly
            output += result['triangulated_location']
        else:
            # Fallback for simple responses
            output += f"📍 **Estimated Location:** {result['triangulated_location']}\n\n"
            
            output += f"**📏 DISTANCE TO REFERENCE:**\n"
            if isinstance(result['distance_to_reference'], (int, float)):
                output += f"🎯 **Final Distance:** {result['distance_to_reference']} miles\n"
                output += f"   (From triangulated location to {result['reference_address']})\n"
            else:
                output += f"🎯 **Final Distance:** {result['distance_to_reference']}\n"
        
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
    
    with gr.Blocks(css=css, theme=gr.themes.Soft(), title="SF Location Triangulator") as demo:
        gr.Markdown("# 🎯 San Francisco Location Triangulator")
        gr.Markdown("Find the mythical location that satisfies all distance constraints, then calculate distance to reference point")
        
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
                    label="🎯 Facilities & Distances for Triangulation",
                    placeholder="""Paste facility list with distances, e.g.:
Laguna Honda Hospital & Rehabilitation Center
1.64 miles away
UCSF Medical Center
2.6 miles away
California Pacific Medical Ctr - St. Lukes Campus
2.76 miles away""",
                    lines=10,
                    elem_classes=["facility-input"],
                    info="The system will find the location that is these distances from all facilities"
                )
                
                triangulate_btn = gr.Button(
                    "🎯 Triangulate Location",
                    variant="primary",
                    size="lg"
                )
        
        with gr.Row():
            results_output = gr.Markdown(
                label="🎯 Triangulation Results",
                value="Results will appear here after triangulation..."
            )
        
        # Example data
        gr.Markdown("### 💡 How Triangulation Works:")
        gr.Markdown("""
**🎯 The Goal:** Find the mysterious location that is:
- 1.64 miles from Laguna Honda Hospital
- 2.6 miles from UCSF Medical Center  
- 2.76 miles from California Pacific Medical Center
- etc.

**🧠 The Process:**
1. **Locate facilities** on SF map using AI knowledge
2. **Draw circles** of specified radius around each facility
3. **Find intersection** point that satisfies all constraints
4. **Calculate distance** from that point to 1945 Broadway

This is like **geometric triangulation** - using known points and distances to find an unknown location!
        """)
        
        # Example data
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
        triangulate_btn.click(
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
    print("=== STARTING LOCATION TRIANGULATOR ===")
    print("San Francisco Location Triangulation System")
    print("Server will be available at: http://0.0.0.0:7864")
    
    app = create_interface()
    print("Launching Location Triangulator...")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7864,
        share=False,
        debug=True,
        show_error=True
    )
