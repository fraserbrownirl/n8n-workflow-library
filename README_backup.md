# n8n Workflow Library 🚀

A comprehensive, AI-friendly collection of n8n workflows with rich metadata, search capabilities, and REST API access.

## 📋 Overview

This repository contains a curated library of n8n workflows, each enhanced with detailed metadata including:
- **Quality scoring** (0-100) based on documentation, error handling, and best practices
- **Category classification** (AI automation, email, data processing, etc.)
- **Integration detection** (Gmail, OpenAI, Slack, etc.)
- **Complexity assessment** (beginner, intermediate, advanced)
- **Complete workflow JSON** preserved exactly as captured

## 🏗️ Repository Structure

```
n8n-workflow-library/
├── workflows/           # 📁 Unaltered workflow JSONs (one per file)
├── indexes/            # 📊 Generated search indexes
│   ├── manifest.json   # Master catalog
│   ├── categories.json # Grouped by category
│   ├── quality.json    # Ranked by quality
│   └── integrations.json # Grouped by integration
├── scripts/            # 🔧 Automation scripts
│   ├── scrape_workflows.py    # Enhanced scraper with metadata
│   ├── generate_indexes.py    # Index generation
│   └── api.py                 # FastAPI REST server
├── .github/workflows/  # 🤖 GitHub Actions
│   └── scrape.yml      # Manual scraping with deduplication
├── openapi.yaml        # 📖 API specification
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/n8n-workflow-library.git
cd n8n-workflow-library

# Install dependencies
pip install -r requirements.txt

# Run the scraper (captures one workflow for testing)
python scripts/scrape_workflows.py

# Generate indexes
python scripts/generate_indexes.py

# Start the API server
python scripts/api.py
```

### 2. GitHub Actions (Recommended)

1. **Manual Trigger**: Go to Actions → "Scrape n8n Workflows" → "Run workflow"
2. **Configure**: Set max workflows and delay
3. **Monitor**: Watch the action run and commit new workflows

## 🔍 API Usage

### Search Workflows
```bash
# Basic search
curl "http://localhost:8000/api/search?q=email+automation"

# Advanced filtering
curl "http://localhost:8000/api/search?category=ai-automation&min_quality=80&complexity=intermediate"
```

### Browse by Category
```bash
# Get all categories
curl "http://localhost:8000/api/categories"

# Get workflows in a category
curl "http://localhost:8000/api/categories/ai-automation"
```

### Get Workflow Details
```bash
# Get complete workflow with metadata
curl "http://localhost:8000/api/workflow/Email_Filtering_AI_Summarization.json"
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: `openapi.yaml`

## 📊 Workflow Metadata

Each workflow includes rich metadata:

```json
{
  "_metadata": {
    "workflow_name": "Email Filtering AI Summarization",
    "quality_score": 85,
    "categories": ["ai-automation", "email-automation"],
    "integrations": ["gmail", "openai", "google-sheets"],
    "complexity": "intermediate",
    "node_count": 12,
    "connection_count": 15,
    "description": "Automate email filtering and AI summarization",
    "scraped_at": "2024-01-15T10:30:00Z",
    "source_url": "https://n8n.io/workflows/5678-email-filtering-ai-summarization"
  },
  "nodes": [...],      // Original workflow data unchanged
  "connections": [...]
}
```

## 🎯 Quality Scoring

Workflows are scored (0-100) based on:

| Criterion | Points | Description |
|-----------|--------|-------------|
| Documentation | 30 | Has sticky notes with substantial content |
| Credentials | 20 | Uses proper credential management |
| Error Handling | 15 | Includes error handling patterns |
| Organization | 10 | Well-organized with meaningful node names |
| Modern Integrations | 15 | Uses AI/API services |
| Parameterization | 10 | Uses expressions/variables |

## 🏷️ Categories

- **ai-automation**: GPT, Claude, LangChain, AI workflows
- **email-automation**: Gmail, email processing, notifications
- **data-processing**: CSV, Excel, database operations
- **communication**: Slack, Discord, Telegram, SMS
- **payment-processing**: Stripe, PayPal, invoicing
- **file-management**: Google Drive, Dropbox, file operations
- **web-scraping**: Data extraction, crawling
- **api-integration**: HTTP requests, webhooks, REST APIs
- **scheduling**: Cron jobs, time-based triggers
- **notifications**: Alerts, monitoring, status updates

## 🔗 Integrations

Detected integrations include:
- **AI Services**: OpenAI, Anthropic, Groq, LangChain
- **Communication**: Gmail, Slack, Discord, Telegram, Twilio
- **Data**: Google Sheets, MySQL, PostgreSQL, Notion, Airtable
- **Business**: Stripe, HubSpot, Salesforce, Zapier
- **File Storage**: Google Drive, Dropbox, AWS S3
- **APIs**: HTTP requests, webhooks, REST endpoints

## 🤖 AI Integration

### For AI Assistants (GPT, Claude, etc.)

This repository is designed for AI consumption:

1. **Structured Data**: All workflows have consistent metadata
2. **Searchable**: Rich indexing for semantic search
3. **API Access**: RESTful endpoints for programmatic access
4. **Quality Filtering**: Pre-scored workflows for recommendations
5. **Complete Context**: Full workflow JSON with metadata

### Example AI Prompts

```
"Find high-quality email automation workflows that use Gmail and have error handling"
"Show me beginner-friendly AI workflows with quality scores above 80"
"What are the best workflows for data processing with Google Sheets integration?"
```

## 🔧 Development

### Adding New Workflows

1. **Manual**: Run `python scripts/scrape_workflows.py`
2. **Automated**: Trigger GitHub Action manually
3. **Batch**: Modify scraper to handle multiple URLs

### Customizing Metadata

Edit `scripts/scrape_workflows.py` to modify:
- Quality scoring algorithm
- Category detection patterns
- Integration mapping
- Complexity calculation

### Extending the API

The FastAPI server (`scripts/api.py`) can be extended with:
- Additional search filters
- New endpoints
- Authentication
- Rate limiting

## 📈 Statistics

Current library stats (auto-generated):
- **Total Workflows**: [Generated by API]
- **Categories**: [Generated by API]
- **Integrations**: [Generated by API]
- **Average Quality**: [Generated by API]

View live stats: `GET /api/stats`

## 🤝 Contributing

1. **Fork** the repository
2. **Add workflows** using the scraper
3. **Test** the API endpoints
4. **Submit** a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **n8n.io**: https://n8n.io
- **n8n Documentation**: https://docs.n8n.io
- **API Documentation**: `/docs` (when server is running)
- **GitHub Actions**: `.github/workflows/scrape.yml`

---

**Built for AI, by humans, for the n8n community** 🤖✨
