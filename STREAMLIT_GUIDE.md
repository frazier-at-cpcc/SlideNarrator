# SlideNarrator Streamlit Guide

Complete guide for using the SlideNarrator web interface.

## Getting Started

### Quick Start

The easiest way to start the web app:

**Mac/Linux:**
```bash
./run_web.sh
```

**Windows:**
```cmd
run_web.bat
```

These scripts will:
- Create a virtual environment if needed
- Install all dependencies
- Launch the Streamlit app
- Open your browser automatically

### Manual Start

If you prefer to start manually:

```bash
# Activate your virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Run Streamlit
streamlit run app.py
```

## Using the Web Interface

### Step 1: Configure API Key

You have two options:

**Option A: Environment Variable (Recommended)**
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

**Option B: Enter in Sidebar**
- Look for the "API Configuration" section in the left sidebar
- Paste your API key in the password field

### Step 2: Customize Settings

In the sidebar, you can configure:

**Narration Tone:**
- Professional (default) - Formal, business-appropriate
- Casual - Friendly, conversational
- Educational - Clear, instructive
- Enthusiastic - Energetic, motivational
- Formal - Academic, serious

**Presentation Context:**
- Optional but highly recommended
- Provide background about your presentation
- Example: "Quarterly sales review for executive team"
- Helps Claude generate more relevant narration

**Polish Focus Areas:**
- Transitions: Smooth flow between slides
- Consistency: Uniform tone and style
- Pacing: Appropriate speaking rhythm
- Engagement: Compelling delivery
- Clarity: Clear, understandable language

### Step 3: Upload Your Presentation

- Click "Browse files" or drag and drop
- Supported format: .pptx only
- Maximum file size: 50 MB
- File is processed securely and not stored

### Step 4: Generate Narration

1. Click the "Generate Narration" button
2. Watch the progress through three steps:
   - **Parsing** (20-40%): Extracting slide content
   - **Generating** (50-80%): Creating individual scripts
   - **Polishing** (85-100%): Improving overall flow

Processing time varies by presentation size:
- 10 slides: ~2-3 minutes
- 25 slides: ~5-7 minutes
- 50 slides: ~10-15 minutes

### Step 5: Review Results

**Metrics Dashboard:**
- Total slides processed
- Estimated presentation duration
- Average time per slide

**Complete Script Tab:**
- View all slides in sequence
- See the full narrative flow
- Copy text directly

**Individual Slides Tab:**
- Select specific slides from dropdown
- View narration with slide metadata
- See duration estimates per slide

### Step 6: Download Your Script

Three formats available:

**Markdown (.md):**
- Best for: Reading and editing
- Includes: Formatting, headings, metadata
- Use for: Rehearsal, sharing with team

**JSON (.json):**
- Best for: Programmatic access
- Includes: All data, structured format
- Use for: Integration, archiving

**Plain Text (.txt):**
- Best for: Simple viewing
- Includes: Just the narration
- Use for: Teleprompters, printing

## Advanced Features

### Reviewing Improvements

After polishing, expand "Improvements Made" to see:
- What changes were made
- Why they were made
- Areas that were enhanced

### Processing Multiple Presentations

After completing one presentation:
1. Click "Process Another Presentation"
2. Session state clears
3. Upload a new file
4. Start fresh with same or different settings

### Keyboard Shortcuts

Streamlit supports these shortcuts:
- `Ctrl/Cmd + R`: Refresh app
- `Ctrl/Cmd + Shift + R`: Clear cache and refresh
- `C`: Open command menu

## Customization

### Changing Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"  # Accent color
backgroundColor = "#FFFFFF"  # Main background
secondaryBackgroundColor = "#F0F2F6"  # Sidebar/cards
textColor = "#262730"  # Text color
```

### Adjusting Upload Limits

In `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 50  # Size in MB
```

## Troubleshooting

### App Won't Start

**Problem:** Port already in use
**Solution:**
```bash
streamlit run app.py --server.port 8502
```

**Problem:** Module not found
**Solution:**
```bash
pip install -r requirements.txt
```

### Upload Fails

**Problem:** File too large
**Solution:** Increase `maxUploadSize` in config or split presentation

**Problem:** Invalid file format
**Solution:** Ensure file is .pptx (not .ppt or Google Slides)

### API Errors

**Problem:** "API key not configured"
**Solution:** Check sidebar input or environment variable

**Problem:** "Rate limit exceeded"
**Solution:** Wait a few minutes, then try again

**Problem:** "Invalid API key"
**Solution:** Verify key at https://console.anthropic.com/

### Slow Performance

**Tips for faster processing:**
1. Fewer slides = faster processing
2. Simple slides process quicker than complex ones
3. Check your internet connection
4. Close other Claude API applications

## Deployment Options

### Local Network

Share with others on your network:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Access from other devices: `http://YOUR_IP:8501`

### Cloud Deployment

**Streamlit Cloud (Free):**
1. Push to GitHub
2. Sign up at https://streamlit.io/cloud
3. Deploy your repo
4. Add API key in secrets

**Docker:**
```bash
docker-compose up -d
```

**Heroku, AWS, GCP:**
See deployment guides in main README

## Best Practices

### For Better Results

1. **Add speaker notes** to PowerPoint slides
2. **Provide context** in the sidebar
3. **Choose appropriate tone** for your audience
4. **Review and edit** generated scripts
5. **Test pacing** by reading aloud

### Security

1. **Never commit** `.env` with API keys
2. **Use environment variables** in production
3. **Enable CORS protection** for public deployments
4. **Implement authentication** if needed
5. **Monitor API usage** to avoid surprises

### Performance

1. **Use latest Python version** (3.11+)
2. **Close app** when not in use
3. **Clear cache** if experiencing issues
4. **Limit file sizes** when possible

## Support

If you encounter issues:
1. Check this guide
2. Review main README.md
3. Check Streamlit documentation
4. Open GitHub issue with details

## Tips & Tricks

### Batch Processing

For multiple presentations:
1. Process first presentation
2. Download results
3. Click "Process Another"
4. Repeat

### Comparing Versions

Try different tones:
1. Process with "Professional"
2. Download results
3. Click "Process Another"
4. Process same file with "Casual"
5. Compare outputs

### Sharing Results

Best practices:
- **Markdown** for team reviews
- **JSON** for archival
- **Text** for quick sharing

### Rehearsal Mode

1. Generate scripts
2. Download markdown
3. Open in browser or markdown viewer
4. Practice presentation while reading

## FAQ

**Q: Can I edit the script in the app?**
A: Not directly. Download and edit in your preferred editor.

**Q: Are my files stored?**
A: No, files are processed in memory and immediately deleted.

**Q: Can I use without internet?**
A: No, Claude API requires internet connection.

**Q: How much does it cost?**
A: Only Claude API usage (~$0.25-$1.00 per presentation).

**Q: Can I customize prompts?**
A: Yes, edit `src/script_generator.py` and `src/script_polisher.py`.

**Q: Does it work with Google Slides?**
A: Export Google Slides as .pptx first.

**Q: Can I add my company logo?**
A: Yes, edit `app.py` to customize branding.

---

Happy presenting! 🎤
