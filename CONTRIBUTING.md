# Contributing to YouTube Metadata Generator

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## 🚀 How to Contribute

### 1. Fork the Repository
- Click the "Fork" button on the GitHub repository page
- Clone your forked repository to your local machine

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

### 4. Test Your Changes
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Test the web app
streamlit run app.py

# Test the API
python server.py
```

### 5. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

### 6. Push and Create a Pull Request
```bash
git push origin feature/your-feature-name
```

## 📋 Development Setup

### Prerequisites
- Python 3.10+
- Groq API key
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-metadata-generator.git
cd youtube-metadata-generator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export GROQ_API_KEY="your_api_key_here"
```

## 🧪 Testing

### Running Tests
```bash
python -m pytest tests/
```

### Manual Testing
1. Start the web app: `streamlit run app.py`
2. Start the API server: `python server.py`
3. Test with various YouTube URLs

## 📝 Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused

## 🐛 Reporting Bugs

When reporting bugs, please include:
- Operating system and Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages and logs

## 💡 Feature Requests

When suggesting features:
- Describe the use case
- Explain the benefits
- Provide examples if possible

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Questions?

Feel free to open an issue for questions or discussions about the project. 