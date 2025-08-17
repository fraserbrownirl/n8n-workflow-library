# 🚀 Setup Guide - n8n Workflow Library

## Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Test the Setup
```bash
python3 test_setup.py
```

### 3. Start the API Server
```bash
python3 scripts/api.py
```
Then visit: http://localhost:8000/docs

### 4. Test the Enhanced Scraper
```bash
python3 scripts/scrape_workflows.py
```

### 5. Generate Indexes
```bash
python3 scripts/generate_indexes.py
```

## GitHub Repository Setup

### 1. Create GitHub Repository
- Go to GitHub.com
- Create new repository: `n8n-workflow-library`
- Don't initialize with README (we already have one)

### 2. Push Your Code
```bash
git remote add origin https://github.com/YOUR_USERNAME/n8n-workflow-library.git
git push -u origin main
```

### 3. Test GitHub Action
- Go to Actions tab
- Click "Scrape n8n Workflows"
- Click "Run workflow"
- Set parameters and run

## API Endpoints

Once the API is running:

- **Health Check**: `GET /api/health`
- **Search**: `GET /api/search?q=email`
- **Categories**: `GET /api/categories`
- **Integrations**: `GET /api/integrations`
- **Quality**: `GET /api/quality`
- **Workflow**: `GET /api/workflow/{filename}`
- **Stats**: `GET /api/stats`

## File Structure

```
n8n-workflow-library/
├── workflows/           # 📁 Unaltered workflow JSONs
├── indexes/            # 📊 Generated search indexes
├── scripts/            # 🔧 Automation scripts
├── .github/workflows/  # 🤖 GitHub Actions
├── openapi.yaml        # 📖 API specification
├── README.md           # 📋 Documentation
├── requirements.txt    # 📦 Dependencies
└── test_setup.py       # 🧪 Setup verification
```

## Troubleshooting

### API Not Starting
- Check if port 8000 is available
- Install dependencies: `pip3 install fastapi uvicorn`
- Run: `python3 scripts/api.py`

### Scraper Issues
- Install Chrome browser
- Install dependencies: `pip3 install selenium requests`
- Check Chrome driver compatibility

### GitHub Action Fails
- Check repository permissions
- Verify workflow file syntax
- Check GitHub Actions logs

## Next Steps

1. ✅ **Setup Complete** - All components working
2. 🔄 **Add Workflows** - Use scraper or GitHub Action
3. 🔍 **Test API** - Verify all endpoints work
4. 📊 **Monitor** - Check indexes and stats
5. 🤖 **AI Integration** - Use with GPT/Claude

---

**Your n8n workflow library is ready to use!** 🎉
