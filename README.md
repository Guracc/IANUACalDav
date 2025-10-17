# IANUACalDav

A Python server-side application that scrapes a website for event data and automatically generates a subscribable calendar using CalDav/iCal format.

## Features

- Web scraping component for extracting events
- Data parsing into calendar events
- iCal calendar generation and serving
- Subscribable by iCloud Calendar and similar apps
- Automated periodic updates

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Configure the scraper URL in `src/scraper/scraper.py`
2. Run the application:
   ```bash
   python src/main.py
   ```
3. Subscribe to the calendar at `http://localhost:5000/calendar.ics` in your calendar app

## Project Structure

- `src/scraper/`: Web scraping functionality
- `src/parser/`: Event data parsing
- `src/caldav_server/`: Calendar serving
- `src/main.py`: Application entry point

## Dependencies

- requests: HTTP requests
- beautifulsoup4: HTML parsing
- icalendar: iCal format handling
- flask: Web server
- apscheduler: Task scheduling
