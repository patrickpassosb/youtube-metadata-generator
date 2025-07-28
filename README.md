# YouTube Metadata Generator

A simple web app to extract YouTube captions and generate SEO-optimized titles and descriptions using Groq AI.

**Created by:** [Patrick Passos](https://github.com/patrickpassosb)  
**Contact:** patrickpassosb@gmail.com

## Features

- 🎥 Extract English auto-captions from YouTube videos
- 🤖 Generate catchy titles and SEO descriptions using Groq AI
- 🌐 User-friendly Streamlit web interface
- 💾 Download results as Markdown

## Quick Start

1. **Install dependencies:**
```bash
   pip install -r requirements.txt
   ```
2. **Get a Groq API key:** [console.groq.com](https://console.groq.com)
3. **Set your API key as an environment variable:**
```bash
export GROQ_API_KEY="your_api_key_here"
```
4. **Run the app:**
```bash
   streamlit run app.py
   ```
5. Open [http://localhost:8501](http://localhost:8501) in your browser.

## Requirements

- Python 3.11+
- Groq API key
- English auto-captions enabled on YouTube videos

## File Structure

```
.
├── app.py        # Streamlit web interface
├── core.py       # Main business logic
├── requirements.txt
└── README.md
```

## License

MIT License

---

If you find this project helpful, please consider starring the repository!
