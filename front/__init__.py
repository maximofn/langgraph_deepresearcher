"""
Front-end interface for Deep Researcher

This package provides a Gradio-based web interface for the Deep Researcher system.
"""

from front.event_tracker import EventTracker, get_tracker, reset_tracker, EventType
from front.deep_researcher_wrapper import DeepResearcherWrapper
from front.gradio_app import create_interface

__all__ = [
    'EventTracker',
    'get_tracker',
    'reset_tracker',
    'EventType',
    'DeepResearcherWrapper',
    'create_interface'
]
