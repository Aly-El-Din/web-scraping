from firecrawl import FirecrawlApp

def crawl(url: str):
    try:
        print(f"Starting to crawl: {url}")
        app = FirecrawlApp(api_key="fc-78ab9738517d4c01a4a8532bbdd269cf")
        print("FirecrawlApp initialized successfully")
        
        response = app.scrape_url(url=url)

        # Check if response is None
        if response is None:
            print("Response is None!")
            return None

        print(response)
        
        return response
        
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def filter_response(response):
    

def main():
    url = 'https://www.imf.org/en/Countries/EGY'
    result = crawl(url=url)
    return result

if __name__ == '__main__':
    main()