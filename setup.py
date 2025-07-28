from setuptools import setup, find_packages

setup(
    name="youtube-metadata-generator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "groq>=0.30.0",
        "requests>=2.32.4", 
        "streamlit>=1.47.0",
        "yt-dlp>=2025.7.21",
    ],
    python_requires=">=3.11",
) 