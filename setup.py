from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="youtube-metadata-generator",
    version="1.2.0",
    author="Patrick",
    author_email="your.email@example.com",
    description="Generate SEO-optimized titles and descriptions from YouTube videos using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube-metadata-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Content Creators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "yt-metadata=gen_meta:main",
        ],
    },
    include_package_data=True,
    keywords="youtube, metadata, seo, ai, groq, streamlit, fastapi",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/youtube-metadata-generator/issues",
        "Source": "https://github.com/yourusername/youtube-metadata-generator",
        "Documentation": "https://github.com/yourusername/youtube-metadata-generator#readme",
    },
) 