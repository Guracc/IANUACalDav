#!/usr/bin/env python3
"""
Main entry point for IANUACalDav application.
Orchestrates scraping, parsing, and CalDav server setup.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from src.scraper.scraper import scrape_events
from src.caldav_server.server import setup_caldav_server

def main():
    # Initial scrape
    events = scrape_events()
    
    # Setup CalDav server with events
    server = setup_caldav_server(events)
    
    # Run scheduler for periodic updates
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: update_calendar(server), 'interval', hours=1)
    scheduler.start()
    
    # Run the server (blocking)
    try:
        server.run(port=8000)
    except KeyboardInterrupt:
        scheduler.shutdown()

def update_calendar(server):
    events = scrape_events()
    server.update_events(events)

if __name__ == "__main__":
    main()