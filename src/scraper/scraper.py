"""
Web scraper component for extracting event data from websites.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
from src.pdf_extractor import extract_pdf_location, extract_pdf_speaker

class EventScraper:
    """
    Handles web scraping for event data.
    """
    
    def __init__(self, url: str = "https://ianua.unige.it/calendari-lezioni-2025-2026"):
        """
        Initialize scraper with target URL.
        
        Args:
            url: The website URL to scrape
        """
        self.url = url
    
    def scrape_caratterizzanti(self) -> List[Dict[str, str]]:
        """
        Scrape the caratterizzanti modules from the IANUA page.
        
        Returns:
            List of dictionaries containing course and calendar link
        """
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links to caratterizzanti calendars
            links = soup.find_all('a', href=lambda x: x and 'caratterizzanti-25-26' in x)
            
            caratterizzanti = []
            for link in links:
                href = link['href']
                # Extract course from href, e.g., calendari-ISB-caratterizzanti-25-26 -> ISB
                course = href.split('-')[1]
                caratterizzanti.append({
                    'course': course,
                    'link': href if href.startswith('http') else f"https://ianua.unige.it{href}",
                    'title': link.get_text(strip=True)
                })
            
            return caratterizzanti
            
        except requests.RequestException as e:
            print(f"Error scraping {self.url}: {e}")
            return []
    
    def scrape_calendar(self, url: str, course: str) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        Scrape events from a specific calendar page.
        
        Args:
            url: The calendar page URL
            course: The course code
            
        Returns:
            Tuple of (events list, subscriptions list)
        """
        events = []
        subscriptions = []
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all h2 headers (subscription titles)
            headers = soup.find_all('h2')
            
            for header in headers:
                title = header.get_text(strip=True)
                if not title or not title.startswith(course + ' '):
                    continue
                
                subscription = title
                subscriptions.append(subscription)
                
                # Find the next table
                table = header.find_next('table')
                if not table:
                    continue
                
                # Parse table rows
                rows = table.find_all('tr')[1:]  # Skip header row
                current_date = None
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 9:
                        continue
                    
                    data = cells[0].get_text(strip=True)
                    ora = cells[2].get_text(strip=True)
                    modulo = cells[4].get_text(strip=True)
                    resp = cells[6].get_text(strip=True)
                    dettagli = cells[8].get_text(strip=True)
                    
                    # Update current date if provided
                    if data:
                        try:
                            current_date = datetime.strptime(data, '%d/%m/%Y').date()
                        except ValueError:
                            continue
                    
                    # Skip if missing required data
                    if not current_date or not ora or not modulo:
                        continue
                    
                    # Parse time range
                    try:
                        start_str, end_str = ora.split('-')
                        start_time = datetime.strptime(start_str.strip(), '%H:%M').time()
                        end_time = datetime.strptime(end_str.strip(), '%H:%M').time()
                        start_datetime = datetime.combine(current_date, start_time)
                        end_datetime = datetime.combine(current_date, end_time)
                    except (ValueError, AttributeError):
                        continue
                    
                    # Check for locandina link
                    dettagli_cell = cells[8]
                    locandina_link = None
                    a_tag = dettagli_cell.find('a')
                    if a_tag and a_tag.get('href'):
                        href = a_tag['href']
                        locandina_link = href if href.startswith('http') else f"https://ianua.unige.it{href}"
                    
                    # Extract PDF location if link exists
                    pdf_location = None
                    if locandina_link:
                        pdf_location = extract_pdf_location(locandina_link)
                    
                    # Extract PDF speaker info if link exists
                    pdf_speaker = None
                    if locandina_link:
                        pdf_speaker = extract_pdf_speaker(locandina_link)
                    
                    # Create description with responsabile and speaker
                    description_parts = []
                    if resp:
                        description_parts.append(f"Responsabile: {resp}")
                    if pdf_speaker:
                        description_parts.append(f"Speaker: {pdf_speaker}")
                    
                    description = "\n".join(description_parts) if description_parts else "TBD"
                    
                    # Set location from PDF if available
                    event_location = pdf_location if pdf_location else ""
                    
                    # Set URL to locandina PDF if available
                    event_url = locandina_link if locandina_link else url
                    
                    # Create event
                    event = {
                        'course': course,
                        'subscription': subscription,
                        'summary': modulo,
                        'start_date': start_datetime,
                        'end_date': end_datetime,
                        'description': description,
                        'location': event_location,
                        'url': event_url
                    }
                    events.append(event)
            
        except requests.RequestException as e:
            print(f"Error scraping calendar {url}: {e}")
        
        return events, subscriptions
    
    def scrape(self) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        Scrape all events from caratterizzanti calendars.
        
        Returns:
            Tuple of (events list, all subscriptions list)
        """
        caratterizzanti = self.scrape_caratterizzanti()
        all_events = []
        all_subscriptions = []
        for item in caratterizzanti:
            course = item['course']
            url = item['link']
            events, subscriptions = self.scrape_calendar(url, course)
            all_events.extend(events)
            all_subscriptions.extend(subscriptions)
        return all_events, all_subscriptions

def scrape_events(url: str = "https://ianua.unige.it/calendari-lezioni-2025-2026") -> tuple[List[Dict[str, Any]], List[str]]:
    """
    Convenience function to scrape events from a URL.
    
    Args:
        url: The URL to scrape events from
        
    Returns:
        Tuple of (events list, subscriptions list)
    """
    scraper = EventScraper(url)
    return scraper.scrape()