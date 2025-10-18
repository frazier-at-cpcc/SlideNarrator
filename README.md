# SlideNarrator

AI-powered PowerPoint narration script generator using Claude. SlideNarrator automatically creates professional narration scripts for your presentations by analyzing slide content and ensuring smooth narrative flow.

## Features

- **Automatic Slide Parsing**: Extracts text, notes, images, charts, and tables from PowerPoint files
- **AI Script Generation**: Creates natural, engaging narration for each slide using Claude
- **Intelligent Polishing**: Reviews the complete script to ensure smooth transitions and consistent tone
- **Multiple Output Formats**: Exports scripts as Markdown, JSON, and plain text
- **Customizable Tone**: Choose from professional, casual, educational, enthusiastic, or formal tones
- **Duration Estimation**: Provides estimated speaking time for each slide and the full presentation

## Architecture

SlideNarrator consists of three main components:

1. **SlideParser** (`src/slide_parser.py`): Extracts content from PowerPoint slides
2. **ScriptGenerator** (`src/script_generator.py`): Generates AI-powered narration for individual slides
3. **ScriptPolisher** (`src/script_polisher.py`): Reviews and polishes the complete script for flow and consistency

## Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key (get one at https://console.anthropic.com/)

### Setup

1. Clone or download this repository:
```bash
cd SlideNarrator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key:
```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Generate a narration script for a PowerPoint presentation:

```bash
python main.py presentation.pptx
```

This will:
1. Parse all slides in the presentation
2. Generate narration scripts for each slide
3. Polish the complete script for smooth flow
4. Save the results to the `output/` directory

### Advanced Usage

**Specify output directory:**
```bash
python main.py presentation.pptx -o ./my_scripts
```

**Choose a different tone:**
```bash
python main.py presentation.pptx -t casual
```

Available tones: `professional`, `casual`, `educational`, `enthusiastic`, `formal`

**Provide presentation context:**
```bash
python main.py presentation.pptx -c "This is a sales pitch for a new product targeting enterprise customers"
```

**Focus on specific areas when polishing:**
```bash
python main.py presentation.pptx -f transitions pacing engagement
```

Available focus areas: `transitions`, `consistency`, `pacing`, `engagement`, `clarity`

**Combine options:**
```bash
python main.py presentation.pptx \
  -o ./output \
  -t educational \
  -c "Technical presentation for developers" \
  -f clarity consistency
```

**Use a different API key:**
```bash
python main.py presentation.pptx --api-key sk-ant-...
```

### Command-Line Options

```
usage: main.py [-h] [-o OUTPUT] [-t {professional,casual,educational,enthusiastic,formal}]
               [-c CONTEXT] [-f {transitions,consistency,pacing,engagement,clarity} ...]
               [--api-key API_KEY] [--no-export]
               pptx_file

positional arguments:
  pptx_file             Path to the PowerPoint (.pptx) file

optional arguments:
  -h, --help            Show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for generated scripts (default: ./output)
  -t TONE, --tone TONE  Tone for the narration (default: professional)
  -c CONTEXT, --context CONTEXT
                        Optional context about the presentation
  -f FOCUS, --focus FOCUS
                        Specific areas to focus on when polishing
  --api-key API_KEY     Anthropic API key (overrides env var)
  --no-export           Don't export results to files
```

## Output Files

SlideNarrator generates three types of output files:

1. **Markdown Script** (`*_script_*.md`):
   - Human-readable script with slide numbers and duration estimates
   - Perfect for presenters to read during rehearsal

2. **JSON Data** (`*_data_*.json`):
   - Complete data including slide content, initial scripts, and polished scripts
   - Useful for programmatic access or further processing

3. **Text Script** (`*_script_*.txt`):
   - Plain text version of the polished script
   - Easy to import into teleprompter software

### Example Output Structure

```
output/
├── presentation_script_20241018_143022.md
├── presentation_data_20241018_143022.json
└── presentation_script_20241018_143022.txt
```

## Programmatic Usage

You can also use SlideNarrator as a Python library:

```python
from src import SlideNarrator

# Initialize
narrator = SlideNarrator(
    pptx_path="presentation.pptx",
    api_key="your_api_key"
)

# Run the workflow
results = narrator.run(
    tone="professional",
    presentation_context="Sales pitch for enterprise customers",
    focus_areas=["transitions", "engagement"],
    output_dir="./output"
)

# Access the polished script
print(results["polished_script"].to_markdown())
```

### Using Individual Components

```python
from src import SlideParser, ScriptGenerator, ScriptPolisher

# Parse slides
parser = SlideParser("presentation.pptx")
slides = parser.parse_all_slides()

# Generate scripts
generator = ScriptGenerator()
scripts = generator.generate_scripts_for_all_slides(
    slides,
    tone="educational"
)

# Polish the complete script
polisher = ScriptPolisher()
polished = polisher.polish_scripts(
    scripts,
    focus_areas=["transitions", "pacing"]
)

# Export as markdown
markdown = polished.to_markdown()
```

## How It Works

### Step 1: Slide Parsing

SlideNarrator uses `python-pptx` to extract:
- Slide titles and text content
- Speaker notes
- Number of images
- Presence of charts and tables

### Step 2: Initial Script Generation

For each slide, Claude generates a narration script based on:
- The slide's content and visual elements
- Context from previous slides for continuity
- The specified tone and presentation context
- Best practices for presentation narration

### Step 3: Script Polishing

Claude reviews the complete script to:
- Ensure smooth transitions between slides
- Maintain consistent tone and style
- Eliminate repetition and redundancy
- Improve pacing and engagement
- Create a cohesive narrative arc

## Configuration

You can customize default settings in `config.py`:

```python
# Words per minute for duration estimation
WORDS_PER_MINUTE = 150

# Target narration duration per slide (seconds)
TARGET_NARRATION_SECONDS = 30

# Default focus areas for polishing
DEFAULT_FOCUS_AREAS = ["transitions", "consistency", "pacing", "engagement"]
```

## Tips for Best Results

1. **Add Speaker Notes**: Include speaker notes in your PowerPoint for better context
2. **Provide Context**: Use the `-c` flag to give Claude context about your presentation
3. **Choose the Right Tone**: Match the tone to your audience and presentation style
4. **Review and Edit**: Always review the generated scripts and make adjustments as needed
5. **Iterate**: Run multiple times with different focus areas to find the best version

## Examples

### Example 1: Educational Presentation

```bash
python main.py lecture.pptx \
  -t educational \
  -c "Introductory computer science lecture for college freshmen" \
  -f clarity engagement
```

### Example 2: Sales Pitch

```bash
python main.py pitch.pptx \
  -t enthusiastic \
  -c "Presenting our new SaaS product to potential investors" \
  -f engagement pacing
```

### Example 3: Technical Documentation

```bash
python main.py technical_overview.pptx \
  -t formal \
  -c "Architecture review for senior engineers" \
  -f clarity consistency
```

## Troubleshooting

### "Anthropic API key not configured"

Make sure you have either:
- Set `ANTHROPIC_API_KEY` in your `.env` file, or
- Passed `--api-key` on the command line

### "Failed to load presentation"

Ensure:
- The file exists and the path is correct
- The file is a valid `.pptx` file (not `.ppt`)
- You have read permissions for the file

### Script generation is slow

This is normal! Generating high-quality narration for each slide takes time. For a 20-slide presentation, expect 2-5 minutes.

### Scripts don't match my expectations

Try:
- Providing more context with `-c`
- Choosing a different tone with `-t`
- Adding speaker notes to your PowerPoint slides
- Adjusting focus areas with `-f`

## Cost Estimation

SlideNarrator uses Claude API calls. Approximate costs:
- Small presentation (10 slides): $0.10 - $0.20
- Medium presentation (25 slides): $0.25 - $0.50
- Large presentation (50 slides): $0.50 - $1.00

Actual costs depend on slide complexity and the Claude model used.

## License

This project is provided as-is for personal and commercial use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Support

For questions or issues:
1. Check the Troubleshooting section above
2. Review the examples in this README
3. Open an issue on GitHub with details about your problem

## Acknowledgments

- Built with [python-pptx](https://python-pptx.readthedocs.io/)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
