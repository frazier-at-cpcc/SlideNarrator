"""
ScriptGenerator module for generating narration scripts for slides using Claude Agent SDK.
"""

from typing import List, Dict, Any, Optional
import anyio
import os
from claude_agent_sdk import query
from .slide_parser import SlideContent


class SlideScript:
    """Represents a generated script for a slide."""

    def __init__(self, slide_number: int, narration: str, duration_estimate: Optional[int] = None):
        self.slide_number = slide_number
        self.narration = narration
        self.duration_estimate = duration_estimate  # in seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert slide script to dictionary format."""
        return {
            "slide_number": self.slide_number,
            "narration": self.narration,
            "duration_estimate": self.duration_estimate
        }

    def __str__(self) -> str:
        """String representation of slide script."""
        text = f"=== Slide {self.slide_number} ===\n"
        text += self.narration
        if self.duration_estimate:
            text += f"\n(Est. duration: {self.duration_estimate}s)"
        return text


class ScriptGenerator:
    """Generates narration scripts for slides using Claude Agent SDK."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the script generator.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
                     Note: Claude Agent SDK uses the environment variable by default
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and ANTHROPIC_API_KEY env var not set")

        # Set the environment variable for the Agent SDK
        os.environ["ANTHROPIC_API_KEY"] = self.api_key

    async def _query_agent(self, prompt: str) -> str:
        """
        Query the Claude Agent SDK and return the response.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            The complete response text from Claude
        """
        response_parts = []

        async for message in query(prompt=prompt):
            # Collect all message parts
            response_parts.append(str(message))

        # Join all parts to get complete response
        full_response = "".join(response_parts).strip()
        return full_response

    def generate_script_for_slide(
        self,
        slide: SlideContent,
        presentation_context: Optional[str] = None,
        previous_scripts: Optional[List[SlideScript]] = None,
        tone: str = "professional"
    ) -> SlideScript:
        """
        Generate a narration script for a single slide using Claude Agent SDK.

        Args:
            slide: SlideContent object containing slide information
            presentation_context: Optional context about the overall presentation
            previous_scripts: Optional list of previously generated scripts for context
            tone: Desired tone for the narration (professional, casual, educational, etc.)

        Returns:
            SlideScript object with generated narration
        """
        # Build the prompt
        prompt = self._build_slide_prompt(slide, presentation_context, previous_scripts, tone)

        # Query Claude Agent SDK
        try:
            # Run the async query in a sync context
            narration = anyio.run(self._query_agent, prompt)

            # Estimate duration (rough estimate: 150 words per minute)
            word_count = len(narration.split())
            duration_estimate = int((word_count / 150) * 60)

            return SlideScript(slide.slide_number, narration, duration_estimate)

        except Exception as e:
            raise Exception(f"Failed to generate script for slide {slide.slide_number}: {str(e)}")

    def _build_slide_prompt(
        self,
        slide: SlideContent,
        presentation_context: Optional[str],
        previous_scripts: Optional[List[SlideScript]],
        tone: str
    ) -> str:
        """Build the prompt for generating slide narration."""
        prompt = f"You are a professional presentation narrator. Generate a natural, engaging narration script for the following slide.\n\n"

        # Add presentation context if available
        if presentation_context:
            prompt += f"Presentation Context:\n{presentation_context}\n\n"

        # Add previous scripts for continuity
        if previous_scripts and len(previous_scripts) > 0:
            prompt += "Previous slide narrations (for context and continuity):\n"
            for prev_script in previous_scripts[-2:]:  # Include last 2 slides for context
                prompt += f"Slide {prev_script.slide_number}: {prev_script.narration}\n\n"

        # Add current slide information
        prompt += f"Current Slide Information:\n"
        prompt += f"Slide Number: {slide.slide_number}\n"

        if slide.title:
            prompt += f"Title: {slide.title}\n"

        if slide.text_content:
            prompt += f"Content:\n"
            for item in slide.text_content:
                prompt += f"  - {item}\n"

        if slide.notes:
            prompt += f"Speaker Notes: {slide.notes}\n"

        if slide.images_count > 0:
            prompt += f"Visual Elements: {slide.images_count} image(s)\n"

        if slide.has_chart:
            prompt += f"Contains: Chart/Graph\n"

        if slide.has_table:
            prompt += f"Contains: Table\n"

        # Add instructions
        prompt += f"\nInstructions:\n"
        prompt += f"- Generate a natural, {tone} narration script\n"
        prompt += f"- The script should be 2-4 sentences or 30-45 seconds when spoken\n"
        prompt += f"- Explain the key points clearly and engagingly\n"
        prompt += f"- If there are visual elements (images, charts, tables), reference them naturally\n"
        prompt += f"- Ensure smooth transition from previous slides\n"
        prompt += f"- Do not include slide numbers or formatting in the narration itself\n"
        prompt += f"- Write ONLY the narration text, nothing else\n"

        return prompt

    def generate_scripts_for_all_slides(
        self,
        slides: List[SlideContent],
        presentation_context: Optional[str] = None,
        tone: str = "professional"
    ) -> List[SlideScript]:
        """
        Generate narration scripts for all slides.

        Args:
            slides: List of SlideContent objects
            presentation_context: Optional context about the overall presentation
            tone: Desired tone for the narration

        Returns:
            List of SlideScript objects
        """
        scripts = []

        for slide in slides:
            print(f"Generating script for slide {slide.slide_number}...")

            script = self.generate_script_for_slide(
                slide,
                presentation_context=presentation_context,
                previous_scripts=scripts,
                tone=tone
            )

            scripts.append(script)

        return scripts

    def estimate_total_duration(self, scripts: List[SlideScript]) -> int:
        """
        Estimate the total duration of all scripts.

        Args:
            scripts: List of SlideScript objects

        Returns:
            Total duration in seconds
        """
        return sum(script.duration_estimate or 0 for script in scripts)
