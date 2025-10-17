"""
CalDav server component for hosting and serving calendars.
Uses Flask to serve iCal feeds that can be subscribed to.
"""

from flask import Flask, Response, request
from icalendar import Calendar, Event
from datetime import datetime
from typing import List, Dict, Any
import re
from urllib.parse import quote

class CalDavServer:
    """
    Simple CalDav-like server using Flask to serve iCal calendars.
    """
    
    def __init__(self, events: List[Dict[str, Any]] = None):
        """
        Initialize server with events.
        
        Args:
            events: List of calendar events
        """
        self.app = Flask(__name__)
        self.events = events or []
        self.subscription_events = self._group_events_by_subscription()
        self.setup_routes()
    
    def _group_events_by_subscription(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group events by subscription for separate feeds."""
        groups = {}
        for event in self.events:
            sub = event.get('subscription', 'unknown')
            if sub not in groups:
                groups[sub] = []
            groups[sub].append(event)
        return groups
    
    def _create_slug(self, subscription: str) -> str:
        """Create a URL-safe slug from subscription name."""
        # Remove parentheses content and clean
        clean = re.sub(r'\s*\([^)]*\)', '', subscription)
        # Replace spaces and special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', clean).strip().replace(' ', '-').lower()
        return quote(slug, safe='')
    
    def setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/calendar.ics')
        def get_full_calendar():
            """Serve the full calendar as iCal format."""
            return self._serve_calendar(self.events, "IANUA Full Calendar")
        
        @self.app.route('/calendar/<slug>.ics')
        def get_subscription_calendar(slug: str):
            """Serve a specific subscription calendar."""
            # Find the subscription that matches this slug
            for sub_name, events in self.subscription_events.items():
                if self._create_slug(sub_name) == slug:
                    return self._serve_calendar(events, f"IANUA {sub_name}")
            return Response("Subscription not found", 404)
        
        @self.app.route('/calendars')
        def list_calendars():
            """List available calendar subscriptions."""
            html = "<h1>IANUA Calendar Subscriptions</h1><ul>"
            html += '<li><a href="/calendar.ics">Full Calendar (All Events)</a></li>'
            for sub_name in sorted(self.subscription_events.keys()):
                slug = self._create_slug(sub_name)
                html += f'<li><a href="/calendar/{slug}.ics">{sub_name}</a></li>'
            html += "</ul>"
            return Response(html, mimetype='text/html')
    
    def _serve_calendar(self, events: List[Dict[str, Any]], name: str) -> Response:
        """Serve a calendar with given events."""
        cal = Calendar()
        cal.add('prodid', '-//IANUACalDav//')
        cal.add('version', '2.0')
        cal.add('name', name)
        
        for event_data in events:
            event = Event()
            event.add('summary', event_data['summary'])
            event.add('dtstart', event_data['start_date'])
            event.add('dtend', event_data['end_date'])
            if event_data.get('description'):
                event.add('description', event_data['description'])
            if event_data.get('location'):
                event.add('location', event_data['location'])
            if event_data.get('url'):
                event.add('url', event_data['url'])
            
            cal.add_component(event)
        
        response = Response(cal.to_ical(), mimetype='text/calendar')
        response.headers['Content-Disposition'] = f'attachment; filename="{name.replace(" ", "_")}.ics"'
        return response
    
    def update_events(self, events: List[Dict[str, Any]]):
        """
        Update the events in the calendar.
        
        Args:
            events: New list of events
        """
        self.events = events
        self.subscription_events = self._group_events_by_subscription()
    
    def run(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Run the Flask server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        print(f"Serving calendar at http://{host}:{port}/calendar.ics")
        self.app.run(host=host, port=port)

def setup_caldav_server(events: List[Dict[str, Any]]) -> CalDavServer:
    """
    Convenience function to set up the CalDav server.
    
    Args:
        events: Initial events for the calendar
        
    Returns:
        Configured CalDavServer instance
    """
    return CalDavServer(events)