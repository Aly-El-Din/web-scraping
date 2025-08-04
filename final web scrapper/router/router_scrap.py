from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import List, Dict

from ..service.firecrawl_service import FirecrawlService

import multiprocessing, tempfile, json, os, logging, uuid


router = APIRouter()

class ScrapeRequest(BaseModel):
    prompt: str

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    items_count: int
    items: List[Dict]

def run_spider_in_process(start_url: str, max_items: int = 50):
    """Run spider in a separate process and save results to a temporary file."""
    # Create a temporary file to store results
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
    temp_filename = temp_file.name
    temp_file.close()
    
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Create crawler process with custom settings
        settings = get_project_settings()
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('ROBOTSTXT_OBEY', False)  # Disable for testing
        settings.set('DOWNLOAD_DELAY', 0.5)
        settings.set('CONCURRENT_REQUESTS', 1)
        
        # Configure to save to JSON file
        settings.set('FEEDS', {
            temp_filename: {
                'format': 'json',
                'overwrite': True,
            }
        })
        
        process = CrawlerProcess(settings)
        
        # Start spider - your new spider doesn't need items parameter
        process.crawl(GenericScrapy, start_url=start_url)
        process.start()
        
        # Read results from temporary file
        items = []
        if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
            with open(temp_filename, 'r', encoding='utf-8') as f:
                items = json.load(f)
        
        return {
            'success': True,
            'items': items[:max_items],
            'total_scraped': len(items)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'items': [],
            'total_scraped': 0
        }
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

"""# Alternative approach using Manager for shared data
def run_spider_with_manager(start_url: str, max_items: int, shared_list):
    Run spider with shared list using multiprocessing Manager.
    try:
        settings = get_project_settings()
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('ROBOTSTXT_OBEY', False)
        settings.set('DOWNLOAD_DELAY', 0.5)
        settings.set('CONCURRENT_REQUESTS', 1)
        
        process = CrawlerProcess(settings)
        # Your new spider doesn't accept items parameter
        process.crawl(GenericScrapy, start_url=start_url)
        process.start()
        
        return True
    except Exception as e:
        print(f"Spider error: {e}")
        return False"""

@router.post("/scrape", response_model=ScrapeResponse)
def scrape(request: ScrapeRequest):
    """Scrape articles from the provided URL."""
    if not request.prompt:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        service = FirecrawlService()

        filename = request.filename or f"{uuid.uuid4().hex}.md"

        response = service.answer_prompt(prompt=request.prompt, filename=filename)
        
        return ScrapeResponse(
            success=True,
            message="Scraping and processing completed",
            items_count=1 if response else 0,
            items=[response] if response else []
        )
    
    except Exception as e:
            logging.error(f"Error during scraping: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

