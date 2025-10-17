#!/usr/bin/env python3
"""
Test script to validate the application components.
"""

from src.scraper.scraper import scrape_events
from src.parser.parser import parse_events
from src.caldav_server.server import setup_caldav_server
import csv

def test_scraper():
    """Test the scraper component."""
    print("Testing scraper...")
    # Scrape all events from caratterizzanti calendars
    events = scrape_events()  # Uses default URL
    print(f"Scraped {len(events)} events")
    if events:
        sample = events[0]
        print(f"Sample event: Course: {sample.get('course')}, Subscription: {sample.get('subscription')}, Summary: {sample.get('summary')}")
        print(f"URL: {sample.get('url')}")
        print(f"Has PDF link: {'PDF:' in sample.get('description', '')}")
    
    # Generate CSV
    generate_csv(events)
    return events

def generate_csv(events):
    """Generate a CSV file with the events."""
    if not events:
        return
    
    filename = 'events.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['course', 'subscription', 'summary', 'start_date', 'end_date', 'description', 'location', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow(event)
    
    print(f"CSV generated: {filename}")

def test_parser():
    """Test the parser component."""
    print("Testing parser...")
    raw_events = [{"title": "Test Event 2023-10-17", "html": "Test description"}]
    parsed = parse_events(raw_events)
    print(f"Parsed {len(parsed)} events")
    print(f"Sample event: {parsed[0] if parsed else 'None'}")
    return parsed

def test_server(events):
    """Test the server setup."""
    print("Testing server setup...")
    server = setup_caldav_server(events)
    print("Server setup successful")
    return server

if __name__ == "__main__":
    try:
        scraped_events = test_scraper()
        parsed_events = test_parser()
        server = test_server(scraped_events)
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")