#!/usr/bin/env python3
"""
SlideNarrator - Main orchestration script

This script coordinates the complete workflow:
1. Parse PowerPoint slides
2. Generate narration scripts for each slide
3. Polish the complete script for smooth flow
4. Export results
"""

import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from src import SlideParser, ScriptGenerator, ScriptPolisher


class SlideNarrator:
    """Main orchestrator for the slide narration workflow."""

    def __init__(self, pptx_path: str, api_key: Optional[str] = None):
        """
        Initialize the SlideNarrator.

        Args:
            pptx_path: Path to the PowerPoint file
            api_key: Anthropic API key (optional, uses env var if not provided)
        """
        self.pptx_path = pptx_path
        self.api_key = api_key

        # Initialize components
        self.parser = SlideParser(pptx_path)
        self.generator = ScriptGenerator(api_key=api_key)
        self.polisher = ScriptPolisher(api_key=api_key)

        # Results storage
        self.slides = []
        self.initial_scripts = []
        self.polished_script = None

    def run(
        self,
        tone: str = "professional",
        presentation_context: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete narration generation workflow.

        Args:
            tone: Desired tone for narration (professional, casual, educational, etc.)
            presentation_context: Optional context about the presentation
            focus_areas: Optional list of areas to focus on when polishing
            output_dir: Directory to save output files (optional)

        Returns:
            Dictionary containing results and metadata
        """
        results = {
            "pptx_path": self.pptx_path,
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        }

        try:
            # Step 1: Parse PowerPoint
            print(f"\n{'=' * 60}")
            print("STEP 1: Parsing PowerPoint presentation")
            print(f"{'=' * 60}")

            self.parser.load_presentation()
            print(self.parser.get_presentation_summary())

            self.slides = self.parser.parse_all_slides()
            print(f"\nExtracted content from {len(self.slides)} slides\n")

            results["total_slides"] = len(self.slides)

            # Step 2: Generate initial scripts
            print(f"\n{'=' * 60}")
            print("STEP 2: Generating narration scripts for each slide")
            print(f"{'=' * 60}\n")

            self.initial_scripts = self.generator.generate_scripts_for_all_slides(
                self.slides,
                presentation_context=presentation_context,
                tone=tone
            )

            total_duration = self.generator.estimate_total_duration(self.initial_scripts)
            print(f"\n✓ Generated {len(self.initial_scripts)} scripts")
            print(f"✓ Estimated total duration: {total_duration // 60}m {total_duration % 60}s\n")

            results["initial_duration"] = total_duration

            # Step 3: Polish the complete script
            print(f"\n{'=' * 60}")
            print("STEP 3: Polishing complete script for smooth flow")
            print(f"{'=' * 60}\n")

            self.polished_script = self.polisher.polish_scripts(
                self.initial_scripts,
                focus_areas=focus_areas
            )

            polished_duration = sum(s.duration_estimate or 0 for s in self.polished_script.scripts)
            print(f"\n✓ Script polishing complete")
            print(f"✓ Final estimated duration: {polished_duration // 60}m {polished_duration % 60}s\n")

            if self.polished_script.improvements:
                print("Improvements made:")
                print(self.polished_script.improvements[:300] + "..." if len(self.polished_script.improvements) > 300 else self.polished_script.improvements)
                print()

            results["polished_duration"] = polished_duration
            results["status"] = "completed"

            # Step 4: Export results
            if output_dir:
                print(f"\n{'=' * 60}")
                print("STEP 4: Exporting results")
                print(f"{'=' * 60}\n")

                output_files = self._export_results(output_dir)
                results["output_files"] = output_files

                print("✓ Results exported successfully\n")

            return results

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            raise

    def _export_results(self, output_dir: str) -> Dict[str, str]:
        """
        Export results to files.

        Args:
            output_dir: Directory to save output files

        Returns:
            Dictionary mapping file types to file paths
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate base filename from pptx name
        base_name = Path(self.pptx_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_files = {}

        # Export markdown script
        md_path = os.path.join(output_dir, f"{base_name}_script_{timestamp}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self.polished_script.to_markdown())
        output_files["markdown"] = md_path
        print(f"  - Markdown script: {md_path}")

        # Export JSON with all data
        json_path = os.path.join(output_dir, f"{base_name}_data_{timestamp}.json")
        json_data = {
            "presentation": self.pptx_path,
            "timestamp": datetime.now().isoformat(),
            "slides_content": [slide.to_dict() for slide in self.slides],
            "initial_scripts": [script.to_dict() for script in self.initial_scripts],
            "polished_script": self.polished_script.to_dict()
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        output_files["json"] = json_path
        print(f"  - JSON data: {json_path}")

        # Export plain text script
        txt_path = os.path.join(output_dir, f"{base_name}_script_{timestamp}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(str(self.polished_script))
        output_files["text"] = txt_path
        print(f"  - Text script: {txt_path}")

        return output_files


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="SlideNarrator - Generate AI-powered narration scripts for PowerPoint presentations"
    )

    parser.add_argument(
        "pptx_file",
        help="Path to the PowerPoint (.pptx) file"
    )

    parser.add_argument(
        "-o", "--output",
        default="./output",
        help="Output directory for generated scripts (default: ./output)"
    )

    parser.add_argument(
        "-t", "--tone",
        default="professional",
        choices=["professional", "casual", "educational", "enthusiastic", "formal"],
        help="Tone for the narration (default: professional)"
    )

    parser.add_argument(
        "-c", "--context",
        help="Optional context about the presentation to guide script generation"
    )

    parser.add_argument(
        "-f", "--focus",
        nargs="+",
        choices=["transitions", "consistency", "pacing", "engagement", "clarity"],
        help="Specific areas to focus on when polishing the script"
    )

    parser.add_argument(
        "--api-key",
        help="Anthropic API key (overrides ANTHROPIC_API_KEY env var)"
    )

    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Don't export results to files (just print to console)"
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Validate input file
    if not os.path.exists(args.pptx_file):
        print(f"Error: File not found: {args.pptx_file}")
        sys.exit(1)

    if not args.pptx_file.lower().endswith('.pptx'):
        print(f"Error: File must be a PowerPoint (.pptx) file")
        sys.exit(1)

    # Run the workflow
    try:
        print("\n" + "=" * 60)
        print(" " * 15 + "SLIDE NARRATOR")
        print(" " * 10 + "AI-Powered Script Generation")
        print("=" * 60)

        narrator = SlideNarrator(
            pptx_path=args.pptx_file,
            api_key=args.api_key
        )

        results = narrator.run(
            tone=args.tone,
            presentation_context=args.context,
            focus_areas=args.focus,
            output_dir=None if args.no_export else args.output
        )

        print(f"\n{'=' * 60}")
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print(f"{'=' * 60}")
        print(f"Total slides processed: {results['total_slides']}")
        print(f"Final presentation duration: ~{results['polished_duration'] // 60}m {results['polished_duration'] % 60}s")

        if not args.no_export:
            print(f"\nResults saved to: {args.output}/")

        print()

    except Exception as e:
        print(f"\n{'=' * 60}")
        print("ERROR")
        print(f"{'=' * 60}")
        print(f"{str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    from typing import Optional, List, Dict, Any
    main()
