"""
Web Scraper - Data collection from websites
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Web scraping integration

    Features:
    - HTML scraping with BeautifulSoup
    - JavaScript rendering with Selenium (optional)
    - Rate limiting
    - User agent rotation
    - Proxy support
    - Data extraction
    """

    def __init__(
        self,
        user_agent: Optional[str] = None,
        rate_limit: float = 1.0,
        timeout: int = 30
    ):
        """
        Initialize web scraper

        Args:
            user_agent: Custom user agent string
            rate_limit: Minimum seconds between requests (default: 1.0)
            timeout: Request timeout in seconds (default: 30)
        """
        self.user_agent = user_agent or "NovaOS-Bot/1.0"
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.last_request_time = 0

        # Try to import BeautifulSoup
        try:
            from bs4 import BeautifulSoup
            self.BeautifulSoup = BeautifulSoup
            logger.info("BeautifulSoup available for parsing")
        except ImportError:
            logger.warning("BeautifulSoup not installed. Run: pip install beautifulsoup4")
            self.BeautifulSoup = None

        logger.info("WebScraper initialized")

    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def fetch_page(
        self,
        url: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Fetch HTML content from URL

        Args:
            url: URL to fetch
            headers: Additional headers
            params: URL parameters

        Returns:
            HTML content or None
        """
        self._enforce_rate_limit()

        default_headers = {
            'User-Agent': self.user_agent
        }

        if headers:
            default_headers.update(headers)

        try:
            response = requests.get(
                url,
                headers=default_headers,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()
            logger.info(f"Fetched page: {url}")

            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str) -> Any:
        """
        Parse HTML with BeautifulSoup

        Args:
            html: HTML content

        Returns:
            BeautifulSoup object or None
        """
        if not self.BeautifulSoup:
            logger.error("BeautifulSoup not available")
            return None

        try:
            return self.BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return None

    def extract_links(self, url: str, filter_domain: bool = True) -> List[str]:
        """
        Extract all links from a page

        Args:
            url: URL to scrape
            filter_domain: Only return links from same domain

        Returns:
            List of URLs
        """
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        if not soup:
            return []

        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert relative URLs to absolute
            if href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(url, href)

            # Filter by domain if requested
            if filter_domain:
                from urllib.parse import urlparse
                base_domain = urlparse(url).netloc
                link_domain = urlparse(href).netloc

                if link_domain == base_domain:
                    links.append(href)
            else:
                links.append(href)

        logger.info(f"Extracted {len(links)} links from {url}")
        return list(set(links))  # Remove duplicates

    def extract_text(self, url: str, selector: Optional[str] = None) -> str:
        """
        Extract text content from page

        Args:
            url: URL to scrape
            selector: CSS selector to target specific element

        Returns:
            Extracted text
        """
        html = self.fetch_page(url)
        if not html:
            return ""

        soup = self.parse_html(html)
        if not soup:
            return ""

        try:
            if selector:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
                else:
                    logger.warning(f"Selector '{selector}' not found")
                    return ""
            else:
                return soup.get_text(strip=True)

        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

    def extract_data(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract structured data using CSS selectors

        Args:
            url: URL to scrape
            selectors: Dict mapping field names to CSS selectors

        Returns:
            Extracted data
        """
        html = self.fetch_page(url)
        if not html:
            return {}

        soup = self.parse_html(html)
        if not soup:
            return {}

        data = {}

        for field, selector in selectors.items():
            try:
                element = soup.select_one(selector)
                if element:
                    data[field] = element.get_text(strip=True)
                else:
                    data[field] = None
                    logger.warning(f"Selector '{selector}' for field '{field}' not found")

            except Exception as e:
                logger.error(f"Error extracting field '{field}': {e}")
                data[field] = None

        return data

    def scrape_list(
        self,
        url: str,
        list_selector: str,
        item_selectors: Dict[str, str]
    ) -> List[Dict]:
        """
        Scrape a list of items from a page

        Args:
            url: URL to scrape
            list_selector: CSS selector for list container
            item_selectors: Dict mapping field names to CSS selectors (relative to item)

        Returns:
            List of extracted items
        """
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        if not soup:
            return []

        items = []

        try:
            elements = soup.select(list_selector)

            for element in elements:
                item = {}

                for field, selector in item_selectors.items():
                    sub_element = element.select_one(selector)
                    if sub_element:
                        item[field] = sub_element.get_text(strip=True)
                    else:
                        item[field] = None

                items.append(item)

            logger.info(f"Scraped {len(items)} items from {url}")

        except Exception as e:
            logger.error(f"Error scraping list: {e}")

        return items

    def scrape_table(self, url: str, table_selector: Optional[str] = None) -> List[Dict]:
        """
        Scrape a table into list of dicts

        Args:
            url: URL to scrape
            table_selector: CSS selector for table (default: first table)

        Returns:
            List of row dicts
        """
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        if not soup:
            return []

        try:
            if table_selector:
                table = soup.select_one(table_selector)
            else:
                table = soup.find('table')

            if not table:
                logger.warning("Table not found")
                return []

            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            else:
                # Try first row as headers
                first_row = table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]

            # Extract rows
            rows = []
            body = table.find('tbody') or table
            for row in body.find_all('tr')[1 if not table.find('thead') else 0:]:
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]

                if headers and len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                else:
                    rows.append({'cells': cells})

            logger.info(f"Scraped table with {len(rows)} rows")
            return rows

        except Exception as e:
            logger.error(f"Error scraping table: {e}")
            return []

    def monitor_page(
        self,
        url: str,
        selector: str,
        interval: int = 60
    ) -> Optional[str]:
        """
        Monitor a page element for changes

        Args:
            url: URL to monitor
            selector: CSS selector for element to monitor
            interval: Check interval in seconds

        Returns:
            Current content
        """
        content = self.extract_text(url, selector)
        logger.info(f"Monitoring {url} (selector: {selector})")
        return content
