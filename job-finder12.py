#!/usr/bin/env python3
"""
LinkedIn Job Search Bot with Gradio Web Interface
This bot searches for jobs using LinkedIn's public pages and uses Claude to analyze them.
"""

import os
import time
import json
import requests
import gradio as gr
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
from pydantic import BaseModel, Field
from dotenv import load_dotenv


@dataclass
class JobListing:
    """Represents a job listing from LinkedIn"""
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: str
    job_id: str = ""


class ClaudeClient:
    """Simple Claude API client without LangChain dependencies"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    def analyze_job(self, job: JobListing, user_profile: Dict[str, str]) -> Dict:
        """Send job analysis request to Claude API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        prompt = f"""You are a career advisor analyzing job opportunities. 
Evaluate this job based on the user's profile and provide structured feedback in JSON format.

User Profile:
Skills: {user_profile.get('skills', '')}
Experience: {user_profile.get('experience', '')}
Career Preferences: {user_profile.get('preferences', '')}

Job Details:
Title: {job.title}
Company: {job.company}
Location: {job.location}
Description: {job.description}

Please respond with a JSON object containing:
- relevance_score: integer from 1-10
- key_requirements: array of main job requirements
- pros: array of positive aspects
- cons: array of potential concerns
- recommendation: one of "Apply", "Consider", or "Skip"  
- reasoning: brief explanation of the recommendation

Return only valid JSON, no other text."""

        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            
            content = response.json()["content"][0]["text"]
            # Try to parse JSON from Claude's response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise
                
        except Exception as e:
            print(f"Claude API error: {str(e)}")
            return {
                "relevance_score": 5,
                "key_requirements": ["Analysis failed"],
                "pros": ["Unable to analyze"],
                "cons": ["Analysis error occurred"],
                "recommendation": "Consider",
                "reasoning": f"Could not complete analysis: {str(e)}"
            }


class LinkedInJobBotRequests:
    """
    A job search bot using HTTP requests instead of browser automation.
    Think of this as a lightweight scout that can quickly gather intel.
    """
    
    def __init__(self, claude_api_key: str, user_profile: Dict[str, str]):
        """Initialize the bot with Claude API key and user profile."""
        self.claude_client = ClaudeClient(claude_api_key)
        self.user_profile = user_profile
        self.session = requests.Session()
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def search_jobs(self, keywords: str, location: str = "", limit: int = 10) -> List[JobListing]:
        """
        Search for jobs using LinkedIn's public job search.
        This is like using LinkedIn's public job board without logging in.
        """
        jobs = []
        
        try:
            # Build search URL for LinkedIn jobs
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': keywords,
                'location': location,
                'f_TPR': 'r604800',  # Past week
                'position': 1,
                'pageNum': 0
            }
            
            search_url = f"{base_url}?{urlencode(params)}"
            print(f"Searching: {search_url}")
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards using LinkedIn's public job search structure
            job_cards = soup.find_all('div', class_='base-card')
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('li', class_='result-card')
                
            if not job_cards:
                print("No job cards found. LinkedIn might have changed their structure.")
                return jobs
                
            print(f"Found {len(job_cards)} job cards")
            
            for i, card in enumerate(job_cards[:limit]):
                try:
                    job = self._extract_job_info(card)
                    if job and job.title and job.company:
                        jobs.append(job)
                        print(f"✓ Extracted job {len(jobs)}: {job.title} at {job.company}")
                        
                        # Be respectful to LinkedIn's servers
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"Error extracting job {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error searching jobs: {str(e)}")
            
        return jobs

    def _extract_job_info(self, card) -> Optional[JobListing]:
        """Extract job information from a job card"""
        try:
            # Extract title
            title_elem = card.find('h3', class_='base-search-card__title') or card.find('h4', class_='result-card__title')
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Extract company
            company_elem = card.find('h4', class_='base-search-card__subtitle') or card.find('h5', class_='result-card__subtitle')
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            
            # Extract location
            location_elem = card.find('span', class_='job-search-card__location') or card.find('span', class_='result-card__location')
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            
            # Extract job URL
            link_elem = card.find('a', href=True)
            job_url = link_elem['href'] if link_elem else ""
            if job_url and not job_url.startswith('http'):
                job_url = f"https://www.linkedin.com{job_url}"
                
            # Extract job ID from URL
            job_id = ""
            if 'jobs/view/' in job_url:
                job_id = job_url.split('jobs/view/')[-1].split('?')[0]
            
            # Extract posted date
            date_elem = card.find('time', class_='job-search-card__listdate') or card.find('time')
            posted_date = date_elem.get('datetime', '') if date_elem else "N/A"
            
            # Get job description by fetching the job page
            description = self._get_job_description(job_url) if job_url else "N/A"
            
            return JobListing(
                title=title,
                company=company,
                location=location,
                description=description,
                url=job_url,
                posted_date=posted_date,
                job_id=job_id
            )
            
        except Exception as e:
            print(f"Error extracting job info: {str(e)}")
            return None

    def _get_job_description(self, job_url: str) -> str:
        """Fetch job description from the job detail page"""
        try:
            if not job_url:
                return "N/A"
                
            response = self.session.get(job_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job description
            desc_elem = soup.find('div', class_='show-more-less-html__markup') or \
                       soup.find('div', class_='description__text') or \
                       soup.find('section', class_='description')
            
            if desc_elem:
                # Clean up the description
                description = desc_elem.get_text(separator=' ', strip=True)
                # Limit length to avoid overwhelming Claude
                return description[:2000] + "..." if len(description) > 2000 else description
            else:
                return "Description not available"
                
        except Exception as e:
            print(f"Error fetching job description: {str(e)}")
            return "Could not fetch description"

    def analyze_job_with_claude(self, job: JobListing) -> Dict:
        """Use Claude to analyze a job listing"""
        return self.claude_client.analyze_job(job, self.user_profile)

    def run_job_search(self, keywords: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        Main method to run the complete job search and analysis pipeline.
        No login required - uses LinkedIn's public job search.
        """
        results = []
        
        try:
            # Step 1: Search for jobs
            print(f"🔍 Searching for '{keywords}' jobs...")
            jobs = self.search_jobs(keywords, location, limit)
            print(f"Found {len(jobs)} job listings")
            
            if not jobs:
                print("No jobs found. Try different keywords or check LinkedIn's structure.")
                return results
            
            # Step 2: Analyze each job with Claude
            print("🤖 Analyzing jobs with Claude...")
            for i, job in enumerate(jobs):
                print(f"Analyzing job {i+1}/{len(jobs)}: {job.title}")
                
                analysis = self.analyze_job_with_claude(job)
                
                result = {
                    'job': job.__dict__,
                    'analysis': analysis,
                }
                
                results.append(result)
                
                # Add delay to be respectful to both LinkedIn and Claude
                time.sleep(2)
            
            # Step 3: Sort by relevance score
            results.sort(key=lambda x: x['analysis']['relevance_score'], reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Error in job search pipeline: {str(e)}")
            return results


# Gradio Interface Functions
def search_jobs_interface(keywords, location, skills, experience, preferences, limit):
    """Gradio interface function for job searching"""
    
    # Load API key
    env_path = Path.home() / '.env'
    load_dotenv(dotenv_path=env_path)
    claude_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not claude_api_key:
        return "❌ ANTHROPIC_API_KEY not found. Please set it in ~/.env file", ""
    
    # Create user profile
    user_profile = {
        "skills": skills,
        "experience": experience,
        "preferences": preferences
    }
    
    # Initialize bot
    bot = LinkedInJobBotRequests(claude_api_key, user_profile)
    
    try:
        # Run job search
        results = bot.run_job_search(keywords, location, int(limit))
        
        if not results:
            return "No jobs found. Try different keywords.", ""
        
        # Format summary
        summary = "🎯 JOB SEARCH SUMMARY\n" + "="*60 + "\n\n"
        
        for i, result in enumerate(results[:5]):  # Show top 5 in summary
            job = result['job']
            analysis = result['analysis']
            
            summary += f"#{i+1} - {job['title']} at {job['company']}\n"
            summary += f"   📍 Location: {job['location']}\n"
            summary += f"   ⭐ Relevance Score: {analysis['relevance_score']}/10\n"
            summary += f"   💡 Recommendation: {analysis['recommendation']}\n"
            summary += f"   📝 Reasoning: {analysis['reasoning']}\n"
            summary += f"   🔗 URL: {job['url']}\n\n"
        
        # Format full JSON data
        json_data = json.dumps(results, indent=2, default=str)
        
        return summary, json_data
        
    except Exception as e:
        return f"Error: {str(e)}", ""


# Create Gradio Interface
def create_gradio_app():
    """Create and configure the Gradio interface"""
    
    with gr.Blocks(title="LinkedIn Job Search Bot", theme=gr.themes.Soft()) as app:
        
        gr.Markdown("""
        # 🔍 LinkedIn Job Search Bot
        
        Search for jobs on LinkedIn and get AI-powered analysis with Claude!
        
        **Features:**
        - No browser required - uses LinkedIn's public job search
        - AI analysis of job relevance based on your profile
        - Detailed job information and recommendations
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Search Parameters")
                
                keywords = gr.Textbox(
                    label="Job Keywords",
                    placeholder="e.g., Python Developer Machine Learning",
                    value="Python Developer Machine Learning"
                )
                
                location = gr.Textbox(
                    label="Location",
                    placeholder="e.g., United States, Remote, New York",
                    value="United States"
                )
                
                limit = gr.Number(
                    label="Number of Jobs to Analyze",
                    value=5,
                    minimum=1,
                    maximum=20
                )
                
                gr.Markdown("### Your Profile")
                
                skills = gr.Textbox(
                    label="Skills",
                    placeholder="e.g., Python, Machine Learning, Data Analysis, APIs",
                    value="Python, Machine Learning, Data Analysis, LangChain, API Development",
                    lines=2
                )
                
                experience = gr.Textbox(
                    label="Experience",
                    placeholder="e.g., 3 years in software development, 2 years in AI/ML",
                    value="3 years in software development, 2 years in AI/ML",
                    lines=2
                )
                
                preferences = gr.Textbox(
                    label="Career Preferences",
                    placeholder="e.g., Remote work preferred, growth opportunities, startup environment",
                    value="Remote work preferred, interested in AI/ML roles, growth opportunities",
                    lines=2
                )
                
                search_btn = gr.Button("🚀 Search Jobs", variant="primary", size="lg")
            
            with gr.Column(scale=2):
                gr.Markdown("### Results")
                
                summary_output = gr.Textbox(
                    label="Job Analysis Summary",
                    lines=20,
                    max_lines=30
                )
                
                json_output = gr.Code(
                    label="Full JSON Data",
                    language="json",
                    lines=15
                )
        
        # Connect the search button
        search_btn.click(
            fn=search_jobs_interface,
            inputs=[keywords, location, skills, experience, preferences, limit],
            outputs=[summary_output, json_output]
        )
        
        gr.Markdown("""
        ---
        **Note:** Make sure you have set your `ANTHROPIC_API_KEY` in `~/.env` file.
        
        Example .env file:
        ```
        ANTHROPIC_API_KEY=sk-ant-your-api-key-here
        ```
        """)
    
    return app


def main():
    """Main function to run the Gradio app"""
    
    # Check if API key is available
    env_path = Path.home() / '.env'
    load_dotenv(dotenv_path=env_path)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in ~/.env")
        print("The app will start but job analysis will fail without the API key.")
    
    # Create and launch the app
    app = create_gradio_app()
    
    print("🚀 Starting LinkedIn Job Search Bot...")
    print("🌐 Access the web interface at: http://0.0.0.0:7860")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()

