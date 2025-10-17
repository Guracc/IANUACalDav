"""
Parser component for converting raw scraped data into calendar events.
"""

from typing import List, Dict, Any
from datetime import datetime
import re

class EventParser:
    """
    Parses raw event data into structured calendar events.
    """
    
    def __init__(self, date_format: str = "%Y-%m-%d"):
        """
        Initialize parser with date format.
        
        Args:
            date_format: Expected date format in scraped data
        """
        self.date_format = date_format
    
    def parse_event(self, raw_event: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse a single raw event into a calendar event.
        
        Args:
            raw_event: Dictionary with raw event data
            
        Returns:
            Dictionary with parsed event data
        """
        title = raw_event.get('title', 'Untitled Event')
        
        # Extract date from title or content (placeholder logic)
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', title)
        if date_match:
            try:
                start_date = datetime.strptime(date_match.group(), self.date_format).date()
            except ValueError:
                start_date = datetime.now().date()
        else:
            start_date = datetime.now().date()
        
        # Create event dictionary
        event = {
            'summary': title,
            'start_date': start_date,
            'end_date': start_date,  # Assume single day for now
            'description': raw_event.get('html', ''),
            'location': '',
            'url': raw_event.get('link', '')
        }
        
        return event
    
    def parse_events(self, raw_events: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Parse multiple raw events.
        
        Args:
            raw_events: List of raw event dictionaries
            
        Returns:
            List of parsed event dictionaries
        """
        return [self.parse_event(event) for event in raw_events]

def parse_events(raw_events: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Convenience function to parse events.
    
    Args:
        raw_events: List of raw event data
        
    Returns:
        List of parsed calendar events
    """
    parser = EventParser()
    return parser.parse_events(raw_events)