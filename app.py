#!/usr/bin/env python3
"""
SlideNarrator - Streamlit Web Application

Interactive web interface for generating AI-powered narration scripts
for PowerPoint presentations.
"""

import streamlit as st
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from src import SlideParser, ScriptGenerator, ScriptPolisher, PolishedScript


# Page configuration
st.set_page_config(
    page_title="SlideNarrator - AI Script Generator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .slide-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'slides' not in st.session_state:
        st.session_state.slides = None
    if 'initial_scripts' not in st.session_state:
        st.session_state.initial_scripts = None
    if 'polished_script' not in st.session_state:
        st.session_state.polished_script = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'pptx_name' not in st.session_state:
        st.session_state.pptx_name = None


def display_header():
    """Display the application header."""
    st.markdown('<div class="main-header">🎤 SlideNarrator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Presentation Script Generator</div>', unsafe_allow_html=True)


def get_api_key() -> Optional[str]:
    """Get API key from sidebar or environment."""
    with st.sidebar:
        st.markdown("### 🔑 API Configuration")

        api_key_input = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            help="Enter your Anthropic API key or set ANTHROPIC_API_KEY environment variable"
        )

        if api_key_input:
            return api_key_input

        if not os.getenv("ANTHROPIC_API_KEY"):
            st.warning("⚠️ API key not configured")
            st.markdown("""
                Get your API key from:
                [Anthropic Console](https://console.anthropic.com/)
            """)
            return None

        return os.getenv("ANTHROPIC_API_KEY")


def display_configuration_sidebar(api_key_available: bool) -> Dict[str, Any]:
    """Display configuration options in sidebar."""
    config = {}

    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Script Settings")

        config['tone'] = st.selectbox(
            "Narration Tone",
            ["professional", "casual", "educational", "enthusiastic", "formal"],
            index=0,
            help="Choose the tone for the narration",
            disabled=not api_key_available
        )

        config['context'] = st.text_area(
            "Presentation Context (Optional)",
            placeholder="e.g., 'This is a quarterly business review for executives...'",
            help="Provide context about your presentation for better results",
            disabled=not api_key_available
        )

        st.markdown("### 🎯 Polish Focus Areas")
        config['focus_areas'] = []

        col1, col2 = st.columns(2)
        with col1:
            if st.checkbox("Transitions", value=True, disabled=not api_key_available):
                config['focus_areas'].append("transitions")
            if st.checkbox("Pacing", value=True, disabled=not api_key_available):
                config['focus_areas'].append("pacing")
            if st.checkbox("Clarity", disabled=not api_key_available):
                config['focus_areas'].append("clarity")

        with col2:
            if st.checkbox("Consistency", value=True, disabled=not api_key_available):
                config['focus_areas'].append("consistency")
            if st.checkbox("Engagement", value=True, disabled=not api_key_available):
                config['focus_areas'].append("engagement")

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
            SlideNarrator uses Claude AI to:
            1. Parse your PowerPoint slides
            2. Generate narration for each slide
            3. Polish the complete script for flow

            [Documentation](https://github.com/yourusername/SlideNarrator)
        """)

    return config


def process_presentation(uploaded_file, api_key: str, config: Dict[str, Any]):
    """Process the uploaded presentation."""
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Initialize components
        parser = SlideParser(tmp_path)
        generator = ScriptGenerator(api_key=api_key)
        polisher = ScriptPolisher(api_key=api_key)

        # Step 1: Parse slides
        st.markdown("### 📄 Step 1: Parsing Presentation")
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Loading presentation...")
        parser.load_presentation()
        progress_bar.progress(20)

        status_text.text("Extracting slide content...")
        slides = parser.parse_all_slides()
        st.session_state.slides = slides
        st.session_state.pptx_name = uploaded_file.name
        progress_bar.progress(40)

        st.success(f"✅ Parsed {len(slides)} slides successfully")

        # Display slide summary
        with st.expander("📋 Slide Summary", expanded=False):
            for slide in slides:
                st.markdown(f"**Slide {slide.slide_number}**: {slide.title or '(no title)'}")
                if slide.text_content:
                    st.caption(f"Content items: {len(slide.text_content)}")
                if slide.images_count > 0:
                    st.caption(f"Images: {slide.images_count}")

        # Step 2: Generate scripts
        st.markdown("### 🤖 Step 2: Generating Narration Scripts")
        progress_bar.progress(50)

        scripts = []
        script_placeholder = st.empty()

        for idx, slide in enumerate(slides):
            status_text.text(f"Generating script for slide {slide.slide_number}/{len(slides)}...")

            script = generator.generate_script_for_slide(
                slide,
                presentation_context=config.get('context'),
                previous_scripts=scripts,
                tone=config['tone']
            )
            scripts.append(script)

            progress = 50 + int((idx + 1) / len(slides) * 30)
            progress_bar.progress(progress)

        st.session_state.initial_scripts = scripts

        total_duration = sum(s.duration_estimate or 0 for s in scripts)
        st.success(f"✅ Generated {len(scripts)} scripts (Est. duration: {total_duration // 60}m {total_duration % 60}s)")

        # Step 3: Polish scripts
        st.markdown("### ✨ Step 3: Polishing Complete Script")
        progress_bar.progress(85)
        status_text.text("Analyzing and polishing the complete script...")

        focus_areas = config.get('focus_areas') if config.get('focus_areas') else None
        polished = polisher.polish_scripts(scripts, focus_areas=focus_areas)
        st.session_state.polished_script = polished

        progress_bar.progress(100)
        status_text.text("Processing complete!")

        polished_duration = sum(s.duration_estimate or 0 for s in polished.scripts)
        st.success(f"✅ Script polishing complete (Final duration: {polished_duration // 60}m {polished_duration % 60}s)")

        if polished.improvements:
            with st.expander("📝 Improvements Made", expanded=False):
                st.write(polished.improvements)

        st.session_state.processing_complete = True

    except Exception as e:
        st.error(f"❌ Error processing presentation: {str(e)}")
        raise

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def display_results():
    """Display the generated scripts and download options."""
    if not st.session_state.processing_complete or not st.session_state.polished_script:
        return

    st.markdown("---")
    st.markdown("## 📜 Generated Narration Script")

    polished = st.session_state.polished_script

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    total_duration = sum(s.duration_estimate or 0 for s in polished.scripts)

    with col1:
        st.metric("Total Slides", len(polished.scripts))
    with col2:
        st.metric("Total Duration", f"{total_duration // 60}m {total_duration % 60}s")
    with col3:
        avg_duration = total_duration // len(polished.scripts) if polished.scripts else 0
        st.metric("Avg per Slide", f"{avg_duration}s")

    # Display scripts
    st.markdown("### 📝 Script Preview")

    # Tab view for scripts
    tab_all, tab_individual = st.tabs(["Complete Script", "Individual Slides"])

    with tab_all:
        for script in polished.scripts:
            with st.container():
                st.markdown(f"#### Slide {script.slide_number}")
                st.markdown(f"**Duration**: ~{script.duration_estimate}s")
                st.markdown(script.narration)
                st.markdown("---")

    with tab_individual:
        slide_num = st.selectbox(
            "Select Slide",
            options=range(1, len(polished.scripts) + 1),
            format_func=lambda x: f"Slide {x}"
        )

        selected_script = polished.scripts[slide_num - 1]

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### Slide {selected_script.slide_number}")
            st.markdown(selected_script.narration)

        with col2:
            st.markdown("### Slide Info")
            if st.session_state.slides:
                slide_content = st.session_state.slides[slide_num - 1]
                st.markdown(f"**Title**: {slide_content.title or 'N/A'}")
                st.markdown(f"**Duration**: ~{selected_script.duration_estimate}s")
                if slide_content.images_count > 0:
                    st.markdown(f"**Images**: {slide_content.images_count}")
                if slide_content.has_chart:
                    st.markdown("**Contains**: Chart")
                if slide_content.has_table:
                    st.markdown("**Contains**: Table")

    # Download options
    st.markdown("### 💾 Download Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Markdown download
        markdown_content = polished.to_markdown()
        st.download_button(
            label="📄 Download Markdown",
            data=markdown_content,
            file_name=f"{Path(st.session_state.pptx_name).stem}_script.md",
            mime="text/markdown"
        )

    with col2:
        # JSON download
        json_data = {
            "presentation": st.session_state.pptx_name,
            "timestamp": datetime.now().isoformat(),
            "polished_script": polished.to_dict()
        }
        st.download_button(
            label="📊 Download JSON",
            data=json.dumps(json_data, indent=2),
            file_name=f"{Path(st.session_state.pptx_name).stem}_data.json",
            mime="application/json"
        )

    with col3:
        # Plain text download
        text_content = str(polished)
        st.download_button(
            label="📝 Download Text",
            data=text_content,
            file_name=f"{Path(st.session_state.pptx_name).stem}_script.txt",
            mime="text/plain"
        )


def main():
    """Main application logic."""
    initialize_session_state()
    display_header()

    # Get API key
    api_key = get_api_key()
    api_key_available = api_key is not None

    # Get configuration
    config = display_configuration_sidebar(api_key_available)

    # Main content area
    st.markdown("### 📤 Upload Presentation")

    if not api_key_available:
        st.warning("⚠️ Please configure your Anthropic API key in the sidebar to continue.")
        st.info("""
            **Getting Started:**
            1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
            2. Enter it in the sidebar
            3. Upload your PowerPoint file
            4. Click 'Generate Narration'
        """)
        return

    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PowerPoint file (.pptx)",
        type=['pptx'],
        help="Upload your PowerPoint presentation to generate narration scripts"
    )

    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        # Show file info
        file_size = uploaded_file.size / 1024 / 1024  # Convert to MB
        st.caption(f"File size: {file_size:.2f} MB")

        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generate Narration", type="primary", use_container_width=True):
                with st.spinner("Processing presentation..."):
                    try:
                        process_presentation(uploaded_file, api_key, config)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.session_state.processing_complete = False

    # Display results if available
    display_results()

    # Reset button
    if st.session_state.processing_complete:
        st.markdown("---")
        if st.button("🔄 Process Another Presentation"):
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()
