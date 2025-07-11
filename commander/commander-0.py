#!/usr/bin/env python3
"""
commander.py - A smart code processor using Gemini 2.5 Pro

This tool reads Python files (optionally recursively), reads instructions from
commander.txt, and applies those instructions to all files using Gemini AI.

Usage:
    python commander.py [-r]
    
    -r: Process files recursively through subdirectories
"""

import os
import sys
import argparse
import glob
from pathlib import Path
from typing import List, Dict, Tuple
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage


class PythonFileProcessor:
    """Handles finding and reading Python files"""
    
    def __init__(self, recursive: bool = False):
        self.recursive = recursive
        self.files_found = []
        
    def find_python_files(self, directory: str = ".") -> List[str]:
        """Find all Python files in the specified directory"""
        pattern = "**/*.py" if self.recursive else "*.py"
        python_files = list(Path(directory).glob(pattern))
        
        # Filter out __pycache__ and other unwanted directories
        filtered_files = []
        for file_path in python_files:
            if not any(part.startswith('__pycache__') or part.startswith('.') 
                      for part in file_path.parts):
                filtered_files.append(str(file_path))
        
        self.files_found = filtered_files
        return filtered_files
    
    def read_file_content(self, file_path: str) -> str:
        """Read the content of a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return ""


class CommanderInstructions:
    """Handles reading and processing commander.txt instructions"""
    
    def __init__(self, instructions_file: str = "commander.txt"):
        self.instructions_file = instructions_file
        self.instructions = ""
        
    def read_instructions(self) -> str:
        """Read the instructions from commander.txt"""
        try:
            with open(self.instructions_file, 'r', encoding='utf-8') as f:
                self.instructions = f.read().strip()
                return self.instructions
        except FileNotFoundError:
            print(f"Error: {self.instructions_file} not found!")
            print("Please create commander.txt with your processing instructions.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading {self.instructions_file}: {e}")
            sys.exit(1)


class GeminiProcessor:
    """Handles communication with Gemini AI"""
    
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",  # Using the latest available model
            google_api_key=api_key,
            temperature=0.1  # Low temperature for consistent code generation
        )
        
    def create_prompt(self, instructions: str, files_data: Dict[str, str]) -> str:
        """Create a comprehensive prompt for Gemini"""
        prompt = f"""You are a skilled Python developer tasked with modifying multiple Python files according to specific instructions.

INSTRUCTIONS:
{instructions}

FILES TO PROCESS:
"""
        
        for filename, content in files_data.items():
            prompt += f"\n---{filename}---\n```python\n{content}\n```\n"
        
        prompt += """

RESPONSE FORMAT:
Please return the modified files in the exact same format, with each file preceded by its filename marker:
---filename.py---
```python
[modified code here]
```

Only return files that need to be changed. If a file doesn't need modification, don't include it in your response.
Ensure all code is syntactically correct and follows Python best practices.
"""
        
        return prompt
    
    def process_files(self, instructions: str, files_data: Dict[str, str]) -> str:
        """Send files to Gemini for processing"""
        prompt = self.create_prompt(instructions, files_data)
        
        try:
            messages = [
                SystemMessage(content="You are an expert Python developer who carefully modifies code according to instructions."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(f"Error communicating with Gemini: {e}")
            return ""


class ResponseParser:
    """Parses Gemini's response and extracts modified files"""
    
    def parse_response(self, response: str) -> Dict[str, str]:
        """Parse Gemini's response and extract modified files"""
        modified_files = {}
        
        # Pattern to match file blocks: ---filename--- followed by ```python code ```
        pattern = r'---([^-]+)---\s*```python\s*\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for filename, code in matches:
            filename = filename.strip()
            code = code.strip()
            modified_files[filename] = code
            
        return modified_files
    
    def write_modified_files(self, modified_files: Dict[str, str]) -> None:
        """Write the modified files back to disk"""
        for filename, content in modified_files.items():
            try:
                # Create backup
                backup_name = f"{filename}.backup"
                if os.path.exists(filename):
                    os.rename(filename, backup_name)
                    print(f"📁 Created backup: {backup_name}")
                
                # Write new content
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated: {filename}")
                
            except Exception as e:
                print(f"❌ Error writing {filename}: {e}")


def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv(os.path.expanduser("~/.env"))
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in ~/.env file")
        print("Please add your Google API key to ~/.env as: GOOGLE_API_KEY=your_key_here")
        sys.exit(1)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process Python files with Gemini AI")
    parser.add_argument("-r", "--recursive", action="store_true", 
                       help="Process files recursively through subdirectories")
    args = parser.parse_args()
    
    print("🚀 Commander.py - Python File Processor")
    print("=" * 50)
    
    # Step 1: Find Python files
    print(f"📂 Finding Python files {'(recursive)' if args.recursive else '(current directory only)'}...")
    file_processor = PythonFileProcessor(args.recursive)
    python_files = file_processor.find_python_files()
    
    if not python_files:
        print("No Python files found!")
        sys.exit(1)
    
    print(f"Found {len(python_files)} Python files:")
    for file in python_files:
        print(f"  • {file}")
    
    # Step 2: Read instructions
    print("\n📋 Reading instructions from commander.txt...")
    instructions_reader = CommanderInstructions()
    instructions = instructions_reader.read_instructions()
    print(f"Instructions loaded: {len(instructions)} characters")
    
    # Step 3: Read file contents
    print("\n📖 Reading file contents...")
    files_data = {}
    for file_path in python_files:
        content = file_processor.read_file_content(file_path)
        if content:
            files_data[file_path] = content
            print(f"  • Read {file_path}: {len(content)} characters")
    
    if not files_data:
        print("No files could be read!")
        sys.exit(1)
    
    # Step 4: Process with Gemini
    print("\n🤖 Processing files with Gemini AI...")
    gemini_processor = GeminiProcessor(api_key)
    response = gemini_processor.process_files(instructions, files_data)
    
    if not response:
        print("No response from Gemini!")
        sys.exit(1)
    
    print(f"Received response: {len(response)} characters")
    
    # Step 5: Parse response and update files
    print("\n🔄 Parsing response and updating files...")
    parser = ResponseParser()
    modified_files = parser.parse_response(response)
    
    if not modified_files:
        print("No files were modified by Gemini.")
        return
    
    print(f"Files to be modified: {len(modified_files)}")
    for filename in modified_files.keys():
        print(f"  • {filename}")
    
    # Ask for confirmation
    confirm = input("\nProceed with file modifications? (y/N): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Write modified files
    parser.write_modified_files(modified_files)
    
    print("\n✨ Processing complete!")
    print("Backups created with .backup extension")


if __name__ == "__main__":
    main()

