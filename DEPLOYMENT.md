# 🚀 Deployment Guide

This guide covers deploying the YouTube Metadata Generator to various platforms.

## 🌐 Web Deployment Options

### 1. Streamlit Cloud (Recommended)

**Easiest deployment option:**

1. **Fork the repository** on GitHub
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Connect your GitHub account**
4. **Select your repository**
5. **Set deployment settings:**
   - Main file path: `app.py`
   - Python version: 3.10
6. **Add secrets:**
   - `GROQ_API_KEY`: Your Groq API key
7. **Deploy!**

**Pros:** Free, automatic deployments, easy setup
**Cons:** Limited to Streamlit interface only

### 2. Railway

**Full-stack deployment:**

1. **Connect GitHub repository** to Railway
2. **Set environment variables:**
   ```
   GROQ_API_KEY=your_api_key_here
   ```
3. **Deploy automatically**

**Pros:** Supports both web app and API, good free tier
**Cons:** Requires credit card for verification

### 3. Render

**Professional deployment:**

1. **Create new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure build settings:**
   ```bash
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
4. **Add environment variables**
5. **Deploy**

**Pros:** Reliable, good documentation, free tier available
**Cons:** Slower cold starts

### 4. Heroku

**Classic deployment:**

1. **Install Heroku CLI**
2. **Create Procfile:**
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
3. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set GROQ_API_KEY=your_api_key_here
   git push heroku main
   ```

**Pros:** Well-established platform
**Cons:** No longer free, requires credit card

## 📱 Mobile Deployment

### Progressive Web App (PWA)

The app is already PWA-ready! Users can:
1. **Visit the web app** on their phone
2. **Add to home screen** for app-like experience
3. **Use offline** (cached content)

### Native Mobile Apps

#### iOS (Shortcuts)
1. **Create Shortcut** in iOS Shortcuts app
2. **Add "Get Text from Input"** action
3. **Add "Get Contents of URL"** action:
   - URL: `https://your-deployed-api.com/meta`
   - Method: POST
   - Headers: `Content-Type: application/json`
   - Body: `{"url": "Shortcut Input"}`
4. **Add "Show Result"** action

#### Android (Termux)
```bash
# Install Termux and Python
pkg install python
pip install requests

# Create script
cat > yt_meta.py << 'EOF'
import requests
import sys

url = sys.argv[1] if len(sys.argv) > 1 else input("YouTube URL: ")
response = requests.post("https://your-deployed-api.com/meta", 
                        json={"url": url})
data = response.json()
print(f"Title: {data['title']}")
print(f"Description: {data['description']}")
EOF

# Use it
python yt_meta.py "https://youtube.com/watch?v=..."
```

## 🔧 Environment Variables

### Required Variables
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Optional Variables
```bash
# For custom configuration
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## 📊 Performance Optimization

### For Production Deployment

1. **Enable caching:**
   ```python
   @st.cache_data
   def expensive_function():
       # Your expensive operation
       pass
   ```

2. **Rate limiting:**
   - Implement request throttling
   - Add user authentication if needed

3. **Error handling:**
   - Add proper error pages
   - Implement logging

4. **Monitoring:**
   - Add health checks
   - Monitor API usage

## 🔒 Security Considerations

### API Key Security
- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Rotate keys regularly**

### Rate Limiting
- **Implement request limits** to prevent abuse
- **Add user authentication** for production use

### CORS Configuration
- **Configure CORS** properly for your domain
- **Limit allowed origins** in production

## 📈 Scaling Considerations

### For High Traffic
1. **Use a CDN** for static assets
2. **Implement caching** (Redis/Memcached)
3. **Use load balancers** for multiple instances
4. **Monitor resource usage**

### Database Integration
- **Add database** for user management
- **Store generated metadata** for reuse
- **Implement user analytics**

## 🐛 Troubleshooting

### Common Issues

1. **Port binding errors:**
   - Use `$PORT` environment variable
   - Set `server.address=0.0.0.0`

2. **API key errors:**
   - Check environment variables
   - Verify API key permissions

3. **Dependency issues:**
   - Use `requirements.txt`
   - Check Python version compatibility

### Debug Mode
```bash
# Enable debug logging
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run app.py
```

## 📞 Support

For deployment issues:
1. **Check platform documentation**
2. **Review error logs**
3. **Test locally first**
4. **Open an issue** on GitHub

Your YouTube Metadata Generator is ready for deployment! 🚀 