#!/usr/bin/env python3
"""
LinkedIn Job Search Bot using LangChain and Claude
This bot searches for recommended jobs on LinkedIn and uses Claude to analyze them.
"""

import os
import time
import json
import requests
import tempfile
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
    applicants: str = ""


class JobAnalysis(BaseModel):
    """Structured output for job analysis"""
    relevance_score: int = Field(description="Job relevance score from 1-10")
    key_requirements: List[str] = Field(description="Main job requirements")
    pros: List[str] = Field(description="Positive aspects of the job")
    cons: List[str] = Field(description="Potential concerns or drawbacks")
    recommendation: str = Field(description="Overall recommendation (Apply/Consider/Skip)")
    reasoning: str = Field(description="Brief explanation of the recommendation")


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
            "model": "claude-3-sonnet-20240229",
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


class LinkedInJobBot:
    """
    A bot that searches LinkedIn for jobs and uses Claude to analyze them.
    Think of this as your personal job hunting assistant.
    """
    
    def __init__(self, claude_api_key: str, user_profile: Dict[str, str]):
        """
        Initialize the bot with Claude API key and user profile.
        
        Args:
            claude_api_key: Your Anthropic API key
            user_profile: Dict with keys like 'skills', 'experience', 'preferences'
        """
        self.claude_client = ClaudeClient(claude_api_key)
        self.user_profile = user_profile
        self.driver = None

    def setup_driver(self, headless: bool = True) -> webdriver.Chrome:
        """
        Set up Chrome WebDriver for LinkedIn scraping.
        Like preparing your web browser to automatically navigate LinkedIn.
        """
        # Create a unique temporary directory for this session
        temp_dir = tempfile.mkdtemp(prefix=f"chrome_data_{uuid.uuid4().hex[:8]}_")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        
        # Essential arguments to avoid conflicts
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-permissions-api")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--single-process")
        
        # Use the unique temporary directory
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        chrome_options.add_argument(f"--remote-debugging-port={9222 + os.getpid() % 1000}")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Store temp_dir for cleanup
        self.temp_dir = temp_dir
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return self.driver
        except Exception as e:
            # Clean up temp directory if driver creation fails
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    def login_linkedin(self, email: str, password: str):
        """
        Log into LinkedIn. Handle this carefully - think of it as
        unlocking the door to your professional network.
        """
        if not self.driver:
            self.setup_driver()
            
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter credentials
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
            )
            
            print("✓ Successfully logged into LinkedIn")
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise

    def search_jobs(self, keywords: str, location: str = "", limit: int = 10) -> List[JobListing]:
        """
        Search for jobs on LinkedIn. This is like casting a net
        in the ocean of job opportunities.
        """
        if not self.driver:
            raise Exception("Driver not initialized. Call login_linkedin first.")
        
        jobs = []
        
        try:
            # Navigate to jobs page
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}"
            self.driver.get(search_url)
            
            # Wait for job results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results"))
            )
            
            # Get job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
            
            for i, card in enumerate(job_cards[:limit]):
                try:
                    # Click on the job card to load details
                    card.click()
                    time.sleep(2)  # Wait for job details to load
                    
                    # Extract job information
                    title = self._safe_find_text(card, ".job-card-list__title")
                    company = self._safe_find_text(card, ".job-card-container__company-name")
                    location = self._safe_find_text(card, ".job-card-container__metadata-item")
                    
                    # Get job description from the details panel
                    description = self._safe_find_text(
                        self.driver, 
                        ".jobs-description-content__text", 
                        use_driver=True
                    )
                    
                    # Get job URL
                    job_url = self.driver.current_url
                    
                    # Get posted date and applicant info if available
                    posted_date = self._safe_find_text(card, ".job-card-container__listed-time")
                    applicants = self._safe_find_text(card, ".job-card-container__applicant-count")
                    
                    job = JobListing(
                        title=title,
                        company=company,
                        location=location,
                        description=description[:1000],  # Limit description length
                        url=job_url,
                        posted_date=posted_date,
                        applicants=applicants
                    )
                    
                    jobs.append(job)
                    print(f"✓ Scraped job {i+1}: {title} at {company}")
                    
                except Exception as e:
                    print(f"Error scraping job {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error searching jobs: {str(e)}")
            
        return jobs

    def _safe_find_text(self, element, selector: str, use_driver: bool = False) -> str:
        """Safely extract text from an element"""
        try:
            search_context = self.driver if use_driver else element
            found_element = search_context.find_element(By.CSS_SELECTOR, selector)
            return found_element.text.strip()
        except:
            return "N/A"

    def analyze_job_with_claude(self, job: JobListing) -> Dict:
        """
        Use Claude to analyze a job listing. Think of Claude as your
        experienced mentor reviewing opportunities with you.
        """
        return self.claude_client.analyze_job(job, self.user_profile)

    def run_job_search(self, email: str, password: str, keywords: str, 
                      location: str = "", limit: int = 10) -> List[Dict]:
        """
        Main method to run the complete job search and analysis pipeline.
        This orchestrates the entire process like a conductor leading an orchestra.
        """
        results = []
        
        try:
            # Step 1: Login to LinkedIn
            print("🔐 Logging into LinkedIn...")
            self.login_linkedin(email, password)
            
            # Step 2: Search for jobs
            print(f"🔍 Searching for '{keywords}' jobs...")
            jobs = self.search_jobs(keywords, location, limit)
            print(f"Found {len(jobs)} job listings")
            
            # Step 3: Analyze each job with Claude
            print("🤖 Analyzing jobs with Claude...")
            for i, job in enumerate(jobs):
                print(f"Analyzing job {i+1}/{len(jobs)}: {job.title}")
                
                analysis = self.analyze_job_with_claude(job)
                
                result = {
                    'job': job.__dict__,
                    'analysis': analysis,
                }
                
                results.append(result)
                
                # Add delay to be respectful to LinkedIn's servers
                time.sleep(1)
            
            # Step 4: Sort by relevance score
            results.sort(key=lambda x: x['analysis']['relevance_score'], reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Error in job search pipeline: {str(e)}")
            return results
            
        finally:
            if self.driver:
                self.driver.quit()
            # Clean up temporary directory
            if hasattr(self, 'temp_dir'):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)

    def save_results(self, results: List[Dict], filename: str = "job_search_results.json"):
        """Save results to a JSON file for later review"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved to {filename}")

    def print_summary(self, results: List[Dict]):
        """Print a nice summary of the job search results"""
        print("\n" + "="*60)
        print("🎯 JOB SEARCH SUMMARY")
        print("="*60)
        
        for i, result in enumerate(results[:5]):  # Show top 5
            job = result['job']
            analysis = result['analysis']
            
            print(f"\n#{i+1} - {job['title']} at {job['company']}")
            print(f"   📍 Location: {job['location']}")
            print(f"   ⭐ Relevance Score: {analysis['relevance_score']}/10")
            print(f"   💡 Recommendation: {analysis['recommendation']}")
            print(f"   📝 Reasoning: {analysis['reasoning']}")
            print(f"   🔗 URL: {job['url']}")


def main():
    """
    Example usage of the LinkedIn Job Bot
    """
    # Load environment variables from ~/.env file
    env_path = Path.home() / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Configuration
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    
    # Check if required environment variables are set
    if not CLAUDE_API_KEY:
        print(f"❌ ANTHROPIC_API_KEY not found in {env_path}")
        print("Get your API key from: https://console.anthropic.com/")
        return
    
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        print(f"❌ LinkedIn credentials not found in {env_path}")
        return
    
    # Your profile for job matching
    user_profile = {
        "skills": "Python, Machine Learning, Data Analysis, LangChain, API Development",
        "experience": "3 years in software development, 2 years in AI/ML",
        "preferences": "Remote work preferred, interested in AI/ML roles, growth opportunities"
    }
    
    # Create and run the bot
    bot = LinkedInJobBot(CLAUDE_API_KEY, user_profile)
    
    try:
        results = bot.run_job_search(
            email=LINKEDIN_EMAIL,
            password=LINKEDIN_PASSWORD,
            keywords="Python Developer Machine Learning",
            location="United States",
            limit=10
        )
        
        # Display and save results
        bot.print_summary(results)
        bot.save_results(results)
        
    except Exception as e:
        print(f"Bot execution failed: {str(e)}")


if __name__ == "__main__":
    main()
