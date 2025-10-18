"""
SlideNarrator - AI-powered PowerPoint narration script generator
"""

from .slide_parser import SlideParser, SlideContent
from .script_generator import ScriptGenerator, SlideScript
from .script_polisher import ScriptPolisher, PolishedScript

__all__ = [
    'SlideParser',
    'SlideContent',
    'ScriptGenerator',
    'SlideScript',
    'ScriptPolisher',
    'PolishedScript'
]
