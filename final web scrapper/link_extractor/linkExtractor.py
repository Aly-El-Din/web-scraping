import re
from urllib.parse import urlparse

class LinkExtractor():
    def __init__(self):
        # Regex pattern to catch http/https/www and domain-like patterns
        self.URL_REGEX = re.compile(
            r"""(?i)\b(                             
                (?:(?:https?|ftp)://)?             
                (?:www\.)?                         
                [a-z0-9.-]+\.[a-z]{2,}             
                (?:/[^\s]*)?                      
            )""",
            re.VERBOSE
        )

    def extract_urls_from_text(self, text: str):
        matches = self.URL_REGEX.findall(text)
        cleaned = []

        for raw_url in matches:
            if not raw_url.startswith("http"):
                raw_url = "https://" + raw_url  # default to HTTPS
            try:
                parsed = urlparse(raw_url)
                if parsed.scheme and parsed.netloc:
                    if raw_url.endswith('?'):
                        raw_url = raw_url.rstrip('?')
                    cleaned.append(raw_url)
            except Exception:
                continue
        print(f"extracted links from the prompt:{cleaned}")
        return list(dict.fromkeys(cleaned))  



def main():
    extractor = LinkExtractor()
    prompt = "Can you extract information from these websites about the latest banking and economic news? Here are the links: https://www.bloomberg.com/economy     https://www.cnbc.com/banking/    https://www.reuters.com/markets/europe/ https://www.wsj.com/news/economy  https://www.ft.com/banking"
    links = extractor.extract_urls_from_text(text=prompt)
    for link in links:
        print(link)

if __name__ == '__main__':
    main()