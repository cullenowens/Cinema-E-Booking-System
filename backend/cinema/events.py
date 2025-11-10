"""
Event-Driven Architecture System for Cinema E-Booking System

This module provides a simple event bus for handling admin operations
in an event-driven manner. Events are dispatched, handlers process them,
and listeners can be notified of changes.

Event Types:
- ADMIN_LOGIN: When an admin successfully logs in
- ADMIN_LOGOUT: When an admin logs out
- MOVIE_CREATED: When a new movie is added
- MOVIE_UPDATED: When a movie is updated
- MOVIE_DELETED: When a movie is removed
- PROMOTION_CREATED: When a new promotion is added
- PROMOTION_UPDATED: When a promotion is updated
- PROMOTION_DELETED: When a promotion is removed
- USER_STATUS_CHANGED: When a user's status is modified
- SHOWTIME_CREATED: When a new showtime is added
- SHOWTIME_DELETED: When a showtime is removed
"""

from typing import Callable, Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Event:
    """Base event class for all system events"""
    def __init__(self, event_type: str, data: Dict[str, Any], user=None):
        self.event_type = event_type
        self.data = data
        self.user = user
        self.timestamp = datetime.now()
        self.event_id = f"{event_type}_{self.timestamp.timestamp()}"

    def __str__(self):
        return f"Event({self.event_type}, user={self.user}, timestamp={self.timestamp})"


class EventBus:
    """
    Central event bus for dispatching and handling events
    Implements the Observer pattern for event-driven architecture
    """
    def __init__(self):
        # Dictionary mapping event types to lists of handler functions
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 100  # Keep last 100 events

    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe a handler function to an event type
        
        Args:
            event_type: Type of event to listen for
            handler: Function to call when event occurs
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """Remove a handler from an event type"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            logger.info(f"Handler unsubscribed from {event_type}")

    def publish(self, event: Event):
        """
        Publish an event to all subscribed handlers
        
        Args:
            event: Event object to publish
        """
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Log the event
        logger.info(f"Event published: {event}")

        # Call all handlers for this event type
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")

    def get_event_history(self, event_type: str = None, limit: int = 10) -> List[Event]:
        """
        Get recent event history
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
        """
        history = self._event_history
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        return history[-limit:]


# Global event bus instance
event_bus = EventBus()


# Event type constants
class EventTypes:
    """Constants for all event types in the system"""
    # Admin events
    ADMIN_LOGIN = "admin_login"
    ADMIN_LOGOUT = "admin_logout"
    ADMIN_ACTION = "admin_action"
    
    # Movie events
    MOVIE_CREATED = "movie_created"
    MOVIE_UPDATED = "movie_updated"
    MOVIE_DELETED = "movie_deleted"
    
    # Promotion events
    PROMOTION_CREATED = "promotion_created"
    PROMOTION_UPDATED = "promotion_updated"
    PROMOTION_DELETED = "promotion_deleted"
    
    # User management events
    USER_STATUS_CHANGED = "user_status_changed"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    
    # Showtime events
    SHOWTIME_CREATED = "showtime_created"
    SHOWTIME_UPDATED = "showtime_updated"
    SHOWTIME_DELETED = "showtime_deleted"


# Default event handlers

def log_admin_action(event: Event):
    """Log all admin actions for audit trail"""
    logger.info(f"AUDIT: Admin {event.user} performed {event.event_type} at {event.timestamp}")
    # Could save to audit log table in future


def send_notification_on_promotion(event: Event):
    """Send notifications when promotions are created/updated"""
    if event.event_type in [EventTypes.PROMOTION_CREATED, EventTypes.PROMOTION_UPDATED]:
        logger.info(f"Notification: New promotion available - {event.data.get('movie_title')}")
        # Future: send emails to subscribed users


# Subscribe default handlers
event_bus.subscribe(EventTypes.ADMIN_LOGIN, log_admin_action)
event_bus.subscribe(EventTypes.ADMIN_ACTION, log_admin_action)
event_bus.subscribe(EventTypes.MOVIE_CREATED, log_admin_action)
event_bus.subscribe(EventTypes.MOVIE_UPDATED, log_admin_action)
event_bus.subscribe(EventTypes.MOVIE_DELETED, log_admin_action)
event_bus.subscribe(EventTypes.PROMOTION_CREATED, log_admin_action)
event_bus.subscribe(EventTypes.PROMOTION_CREATED, send_notification_on_promotion)
event_bus.subscribe(EventTypes.PROMOTION_UPDATED, send_notification_on_promotion)
event_bus.subscribe(EventTypes.USER_STATUS_CHANGED, log_admin_action)
event_bus.subscribe(EventTypes.SHOWTIME_CREATED, log_admin_action)
event_bus.subscribe(EventTypes.SHOWTIME_DELETED, log_admin_action)