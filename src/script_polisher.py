"""
ScriptPolisher module for reviewing and improving the overall narration flow using Claude Agent SDK.
"""

from typing import List, Dict, Any, Optional
import anyio
import os
from claude_agent_sdk import query
from .script_generator import SlideScript


class PolishedScript:
    """Represents a polished version of the complete presentation script."""

    def __init__(self, scripts: List[SlideScript], improvements: Optional[str] = None):
        self.scripts = scripts
        self.improvements = improvements  # Description of changes made

    def to_dict(self) -> Dict[str, Any]:
        """Convert polished script to dictionary format."""
        return {
            "scripts": [script.to_dict() for script in self.scripts],
            "improvements": self.improvements
        }

    def __str__(self) -> str:
        """String representation of polished script."""
        text = "=== POLISHED PRESENTATION SCRIPT ===\n\n"

        for script in self.scripts:
            text += str(script) + "\n\n"

        if self.improvements:
            text += "\n=== IMPROVEMENTS MADE ===\n"
            text += self.improvements

        return text

    def to_markdown(self) -> str:
        """Export the polished script as markdown."""
        md = "# Presentation Narration Script\n\n"

        total_duration = sum(s.duration_estimate or 0 for s in self.scripts)
        md += f"**Total Slides:** {len(self.scripts)}\n"
        md += f"**Estimated Duration:** {total_duration // 60}m {total_duration % 60}s\n\n"
        md += "---\n\n"

        for script in self.scripts:
            md += f"## Slide {script.slide_number}\n\n"
            md += f"{script.narration}\n\n"
            if script.duration_estimate:
                md += f"*Duration: ~{script.duration_estimate}s*\n\n"
            md += "---\n\n"

        if self.improvements:
            md += "\n## Improvements Made\n\n"
            md += self.improvements + "\n"

        return md


class ScriptPolisher:
    """Polishes and improves the overall narration script using Claude Agent SDK."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the script polisher.

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

    def polish_scripts(
        self,
        scripts: List[SlideScript],
        focus_areas: Optional[List[str]] = None
    ) -> PolishedScript:
        """
        Review and polish the complete presentation script using Claude Agent SDK.

        Args:
            scripts: List of SlideScript objects
            focus_areas: Optional list of specific areas to focus on
                        (e.g., ["transitions", "consistency", "pacing"])

        Returns:
            PolishedScript object with improved narrations
        """
        print("Analyzing complete script for improvements...")

        # Build the prompt for reviewing the entire script
        prompt = self._build_polish_prompt(scripts, focus_areas)

        try:
            # Query Claude Agent SDK
            response = anyio.run(self._query_agent, prompt)

            # Parse the response to extract polished scripts
            polished_scripts, improvements = self._parse_polish_response(response, scripts)

            return PolishedScript(polished_scripts, improvements)

        except Exception as e:
            raise Exception(f"Failed to polish scripts: {str(e)}")

    def _build_polish_prompt(
        self,
        scripts: List[SlideScript],
        focus_areas: Optional[List[str]]
    ) -> str:
        """Build the prompt for polishing the complete script."""
        prompt = "You are an expert presentation coach and script editor. Review the following complete presentation narration and improve it for better flow, consistency, and engagement.\n\n"

        prompt += "CURRENT COMPLETE SCRIPT:\n"
        prompt += "=" * 50 + "\n\n"

        for script in scripts:
            prompt += f"[SLIDE {script.slide_number}]\n"
            prompt += f"{script.narration}\n\n"

        prompt += "=" * 50 + "\n\n"

        prompt += "TASK:\n"
        prompt += "Review the entire script and make improvements focusing on:\n"

        if focus_areas:
            for area in focus_areas:
                prompt += f"  - {area}\n"
        else:
            prompt += "  - Smooth transitions between slides\n"
            prompt += "  - Consistent tone and style throughout\n"
            prompt += "  - Eliminating repetition and redundancy\n"
            prompt += "  - Improving pacing and flow\n"
            prompt += "  - Ensuring the narrative has a clear beginning, middle, and end\n"
            prompt += "  - Making the content more engaging and memorable\n"

        prompt += "\nOUTPUT FORMAT:\n"
        prompt += "For each slide, provide the improved narration in this exact format:\n\n"
        prompt += "[SLIDE X]\n"
        prompt += "<improved narration text>\n\n"
        prompt += "After all slides, add a section:\n\n"
        prompt += "[IMPROVEMENTS]\n"
        prompt += "<summary of key changes made and why>\n\n"
        prompt += "IMPORTANT: Maintain the same number of slides. Do not merge or split slides.\n"

        return prompt

    def _parse_polish_response(
        self,
        response: str,
        original_scripts: List[SlideScript]
    ) -> tuple[List[SlideScript], str]:
        """
        Parse the AI response to extract polished scripts.

        Args:
            response: The AI-generated response
            original_scripts: Original scripts (used for fallback)

        Returns:
            Tuple of (polished_scripts, improvements_summary)
        """
        polished_scripts = []
        improvements = ""

        # Split response into sections
        lines = response.split('\n')
        current_slide = None
        current_narration = []
        in_improvements = False

        for line in lines:
            line_stripped = line.strip()

            # Check for slide marker
            if line_stripped.startswith('[SLIDE') and ']' in line_stripped:
                # Save previous slide if exists
                if current_slide is not None and current_narration:
                    narration_text = ' '.join(current_narration).strip()
                    if narration_text:
                        # Estimate duration
                        word_count = len(narration_text.split())
                        duration = int((word_count / 150) * 60)
                        polished_scripts.append(SlideScript(current_slide, narration_text, duration))

                # Extract slide number
                try:
                    slide_num_str = line_stripped.split('[SLIDE')[1].split(']')[0].strip()
                    current_slide = int(slide_num_str)
                    current_narration = []
                    in_improvements = False
                except (IndexError, ValueError):
                    pass

            # Check for improvements section
            elif line_stripped == '[IMPROVEMENTS]':
                # Save last slide if exists
                if current_slide is not None and current_narration:
                    narration_text = ' '.join(current_narration).strip()
                    if narration_text:
                        word_count = len(narration_text.split())
                        duration = int((word_count / 150) * 60)
                        polished_scripts.append(SlideScript(current_slide, narration_text, duration))

                in_improvements = True
                current_slide = None
                current_narration = []

            # Collect narration or improvements
            elif line_stripped:
                if in_improvements:
                    improvements += line_stripped + ' '
                elif current_slide is not None:
                    current_narration.append(line_stripped)

        # Save last slide if not saved yet
        if current_slide is not None and current_narration:
            narration_text = ' '.join(current_narration).strip()
            if narration_text:
                word_count = len(narration_text.split())
                duration = int((word_count / 150) * 60)
                polished_scripts.append(SlideScript(current_slide, narration_text, duration))

        # Fallback: if parsing failed, return original scripts
        if not polished_scripts:
            print("Warning: Failed to parse polished scripts, using originals")
            polished_scripts = original_scripts
            improvements = "Note: Parsing of polished scripts failed. Original scripts retained."

        # Ensure we have scripts for all slides
        if len(polished_scripts) != len(original_scripts):
            print(f"Warning: Script count mismatch. Expected {len(original_scripts)}, got {len(polished_scripts)}")
            # Fill in missing slides with originals
            slide_nums_polished = {s.slide_number for s in polished_scripts}
            for orig in original_scripts:
                if orig.slide_number not in slide_nums_polished:
                    polished_scripts.append(orig)

            # Sort by slide number
            polished_scripts.sort(key=lambda x: x.slide_number)

        return polished_scripts, improvements.strip()
