import os
import re
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class DistanceCalculator:
    def __init__(self):
        print("DistanceCalculator initialized")
        
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
            
            # Create the distance calculation prompt template - updated for any two addresses
            distance_template = """You are a real estate office assistant. Your client has asked you to calculate the distance between two addresses in San Francisco. Provide approximations in tenths of miles.

From address: {from_address}
To address: {to_address}

Return ONLY the distance in tenths of miles as a decimal number (e.g., 0.8, 1.2, 2.5). Do not include units or explanations."""

            prompt = PromptTemplate(
                input_variables=["from_address", "to_address"],
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
    
    def calculate_distance(self, from_address, to_address):
        """Calculate distance between two addresses"""
        if not self.distance_chain:
            print(f"❌ Distance chain not available")
            return "N/A - OpenAI not configured"
        
        try:
            print(f"🔍 Calculating distance from '{from_address}' to '{to_address}'")
            
            # Run the LangChain to get distance
            result = self.distance_chain.run(
                from_address=from_address,
                to_address=to_address
            )
            print(f"🤖 OpenAI response: '{result}'")
            
            # Clean up the result - strip whitespace and extract number
            cleaned_result = result.strip()
            print(f"🧹 Cleaned response: '{cleaned_result}'")
            
            # More flexible regex to handle various formats
            distance_match = re.search(r'(\d+\.?\d*)', cleaned_result)
            if distance_match:
                distance = float(distance_match.group(1))
                final_result = f"{distance}"
                print(f"✅ Parsed distance: {final_result} miles")
                return final_result
            else:
                print(f"❌ Could not parse distance from: '{cleaned_result}'")
                return "Unable to parse distance"
                
        except Exception as e:
            print(f"❌ Error calculating distance: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"

# Create a global calculator instance
global_calculator = None

def get_calculator():
    """Get or create the global calculator instance"""
    global global_calculator
    if global_calculator is None:
        print("🧮 Creating new DistanceCalculator instance...")
        global_calculator = DistanceCalculator()
    return global_calculator

def calculate_distance_gradio(to_address):
    """Main calculation function for Gradio interface"""
    print(f"=== DISTANCE CALCULATION STARTED ===")
    print(f"To Address: {to_address}")
    
    # Fixed reference address
    from_address = "1945 Broadway, San Francisco, CA"
    
    # Use the global calculator instance
    calculator = get_calculator()
    
    # Validate input
    if not to_address or len(to_address.strip()) < 5:
        return "Please enter a valid address"
    
    # Add San Francisco context if not specified
    if "san francisco" not in to_address.lower() and "sf" not in to_address.lower():
        to_address += ", San Francisco, CA"
    
    print(f"From: {from_address}")
    print(f"To: {to_address}")
    
    # Calculate distance
    distance = calculator.calculate_distance(from_address, to_address)
    
    print(f"Distance calculation completed: {distance}")
    
    return distance

def create_interface():
    """Create Gradio interface for distance calculation"""
    print("Creating Distance Calculator interface...")
    
    # Custom CSS for better styling
    css = """
    .reference-address {
        font-size: 18px;
        font-weight: bold;
        color: #2e7d32;
        background-color: #e8f5e8;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
    }
    .distance-output {
        font-size: 20px;
        font-weight: bold;
        color: #1976d2;
        text-align: center;
    }
    """
    
    with gr.Blocks(css=css, theme=gr.themes.Soft(), title="SF Distance Calculator") as demo:
        gr.Markdown("# 🗺️ San Francisco Distance Calculator")
        gr.Markdown("Calculate distances from the reference address to any location in San Francisco")
        
        # Reference address display
        with gr.Row():
            gr.HTML("""
                <div class="reference-address">
                    📍 Reference Address: 1945 Broadway, San Francisco, CA
                </div>
            """)
        
        with gr.Row():
            with gr.Column(scale=3):
                to_address_input = gr.Textbox(
                    label="📮 To Address",
                    placeholder="Enter destination address (e.g., Union Square, SOMA, 123 Main St)",
                    lines=1,
                    info="Enter any San Francisco address, neighborhood, or landmark"
                )
            
            with gr.Column(scale=1):
                calculate_btn = gr.Button(
                    "Calculate Distance",
                    variant="primary",
                    size="lg"
                )
        
        with gr.Row():
            distance_output = gr.Textbox(
                label="📏 Distance (miles)",
                interactive=False,
                elem_classes=["distance-output"]
            )
        
        # Examples
        gr.Markdown("### 💡 Try these examples:")
        with gr.Row():
            example_buttons = [
                gr.Button("Union Square", size="sm"),
                gr.Button("Golden Gate Bridge", size="sm"),
                gr.Button("SOMA", size="sm"),
                gr.Button("Mission District", size="sm"),
            ]
        
        # Button click handlers
        calculate_btn.click(
            fn=calculate_distance_gradio,
            inputs=[to_address_input],
            outputs=[distance_output]
        )
        
        # Example button handlers
        example_buttons[0].click(lambda: "Union Square", outputs=[to_address_input])
        example_buttons[1].click(lambda: "Golden Gate Bridge", outputs=[to_address_input])
        example_buttons[2].click(lambda: "SOMA", outputs=[to_address_input])
        example_buttons[3].click(lambda: "Mission District", outputs=[to_address_input])
        
        # Allow Enter key to calculate
        to_address_input.submit(
            fn=calculate_distance_gradio,
            inputs=[to_address_input],
            outputs=[distance_output]
        )
    
    return demo

if __name__ == "__main__":
    print("=== STARTING DISTANCE CALCULATOR ===")
    print("San Francisco Distance Calculator")
    print("Server will be available at: http://0.0.0.0:7863")
    
    app = create_interface()
    print("Launching Distance Calculator...")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7863,
        share=False,
        debug=True,
        show_error=True
    )
