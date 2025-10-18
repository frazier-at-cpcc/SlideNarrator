#!/usr/bin/env python3
"""
Example usage of SlideNarrator library

This script demonstrates how to use SlideNarrator programmatically
to generate narration scripts for PowerPoint presentations.
"""

import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

from src import SlideParser, ScriptGenerator, ScriptPolisher

# Load environment variables
load_dotenv()


def example_basic_usage():
    """Example 1: Basic usage - parse and generate scripts."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)

    # Replace with your actual .pptx file path
    pptx_path = "presentation.pptx"

    if not os.path.exists(pptx_path):
        print(f"Note: {pptx_path} not found. This is just an example.")
        return

    # Step 1: Parse the presentation
    parser = SlideParser(pptx_path)
    slides = parser.parse_all_slides()

    print(f"\nParsed {len(slides)} slides:")
    for slide in slides:
        print(f"  - Slide {slide.slide_number}: {slide.title or '(no title)'}")

    # Step 2: Generate scripts
    generator = ScriptGenerator()
    scripts = generator.generate_scripts_for_all_slides(slides)

    print(f"\nGenerated {len(scripts)} scripts")

    # Step 3: Polish the scripts
    polisher = ScriptPolisher()
    polished = polisher.polish_scripts(scripts)

    # Print the first slide's narration
    if polished.scripts:
        print(f"\nSample narration (Slide 1):")
        print(polished.scripts[0].narration)


def example_with_context():
    """Example 2: Using presentation context for better results."""
    print("\n" + "=" * 60)
    print("Example 2: With Presentation Context")
    print("=" * 60)

    pptx_path = "presentation.pptx"

    if not os.path.exists(pptx_path):
        print(f"Note: {pptx_path} not found. This is just an example.")
        return

    # Define context about your presentation
    context = """
    This is a quarterly business review presentation for executives.
    The presentation covers Q4 2024 results, market analysis, and 2025 strategy.
    The audience consists of C-level executives and board members.
    """

    # Parse slides
    parser = SlideParser(pptx_path)
    slides = parser.parse_all_slides()

    # Generate scripts with context and professional tone
    generator = ScriptGenerator()
    scripts = generator.generate_scripts_for_all_slides(
        slides,
        presentation_context=context,
        tone="professional"
    )

    # Polish with focus on specific areas
    polisher = ScriptPolisher()
    polished = polisher.polish_scripts(
        scripts,
        focus_areas=["transitions", "consistency", "engagement"]
    )

    print(f"\nGenerated polished scripts for {len(polished.scripts)} slides")
    print("\nImprovements made:")
    print(polished.improvements or "None specified")


def example_export_formats():
    """Example 3: Exporting in different formats."""
    print("\n" + "=" * 60)
    print("Example 3: Export Formats")
    print("=" * 60)

    pptx_path = "presentation.pptx"

    if not os.path.exists(pptx_path):
        print(f"Note: {pptx_path} not found. This is just an example.")
        return

    # Quick workflow
    parser = SlideParser(pptx_path)
    slides = parser.parse_all_slides()

    generator = ScriptGenerator()
    scripts = generator.generate_scripts_for_all_slides(slides)

    polisher = ScriptPolisher()
    polished = polisher.polish_scripts(scripts)

    # Export as markdown
    markdown = polished.to_markdown()
    with open("script.md", "w") as f:
        f.write(markdown)
    print("\nExported to script.md")

    # Export as JSON
    import json
    json_data = polished.to_dict()
    with open("script.json", "w") as f:
        json.dump(json_data, f, indent=2)
    print("Exported to script.json")

    # Print to console
    print("\nPlain text output:")
    print(str(polished))


def example_individual_slide():
    """Example 4: Generate script for a single slide."""
    print("\n" + "=" * 60)
    print("Example 4: Individual Slide")
    print("=" * 60)

    pptx_path = "presentation.pptx"

    if not os.path.exists(pptx_path):
        print(f"Note: {pptx_path} not found. This is just an example.")
        return

    # Parse slides
    parser = SlideParser(pptx_path)
    slides = parser.parse_all_slides()

    if len(slides) == 0:
        print("No slides found")
        return

    # Generate script for just the first slide
    generator = ScriptGenerator()
    first_slide = slides[0]

    script = generator.generate_script_for_slide(
        first_slide,
        tone="casual"
    )

    print(f"\nSlide {script.slide_number} narration:")
    print(script.narration)
    print(f"\nEstimated duration: {script.duration_estimate}s")


def example_custom_workflow():
    """Example 5: Custom workflow with additional processing."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Workflow")
    print("=" * 60)

    pptx_path = "presentation.pptx"

    if not os.path.exists(pptx_path):
        print(f"Note: {pptx_path} not found. This is just an example.")
        return

    # Parse
    parser = SlideParser(pptx_path)
    print(parser.get_presentation_summary())

    slides = parser.parse_all_slides()

    # Filter slides (e.g., only process slides with content)
    content_slides = [s for s in slides if s.text_content or s.title]
    print(f"\nProcessing {len(content_slides)} of {len(slides)} slides")

    # Generate scripts with different tones for different slides
    generator = ScriptGenerator()
    scripts = []

    for slide in content_slides:
        # Use enthusiastic tone for the first slide, professional for others
        tone = "enthusiastic" if slide.slide_number == 1 else "professional"

        script = generator.generate_script_for_slide(
            slide,
            previous_scripts=scripts,
            tone=tone
        )
        scripts.append(script)

    # Calculate total duration
    total_duration = sum(s.duration_estimate or 0 for s in scripts)
    print(f"\nTotal estimated duration: {total_duration // 60}m {total_duration % 60}s")

    # Polish
    polisher = ScriptPolisher()
    polished = polisher.polish_scripts(scripts)

    print(f"\nPolished {len(polished.scripts)} scripts")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("SlideNarrator - Example Usage")
    print("=" * 60)

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\nWARNING: ANTHROPIC_API_KEY not set in environment")
        print("Please set it in .env file or as an environment variable")
        print("\nThese examples will not run without an API key.")
        return

    # Note about example file
    print("\nNOTE: These examples assume you have a file named 'presentation.pptx'")
    print("Replace 'presentation.pptx' with your actual PowerPoint file path")
    print()

    # Run examples
    try:
        example_basic_usage()
        # example_with_context()
        # example_export_formats()
        # example_individual_slide()
        # example_custom_workflow()

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have:")
        print("  1. Set ANTHROPIC_API_KEY in .env")
        print("  2. Installed dependencies: pip install -r requirements.txt")
        print("  3. Created or specified a valid .pptx file")


if __name__ == "__main__":
    main()
