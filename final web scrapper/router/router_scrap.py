from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import multiprocessing
import tempfile
import json
import os
from typing import List, Dict
import logging

# Import your spider class
from imf_spider import GenericScrapy

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str
    max_items: int = 1000

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

# Alternative approach using Manager for shared data
def run_spider_with_manager(start_url: str, max_items: int, shared_list):
    """Run spider with shared list using multiprocessing Manager."""
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
        return False

@router.post("/scrape", response_model=ScrapeResponse)
def scrape(request: ScrapeRequest):
    """Scrape articles from the provided URL."""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    if not request.url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    print(f"Request received: {request.url}")
    
    try:
        # Method 1: Using temporary file (recommended)
        with multiprocessing.Pool(1) as pool:
            result = pool.apply(run_spider_in_process, (request.url, request.max_items))
        
        if result['success']:
            return ScrapeResponse(
                success=True,
                message=f"Successfully scraped {result['total_scraped']} items",
                items_count=len(result['items']),
                items=result['items']
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Scraping failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logging.error(f"Error during scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

