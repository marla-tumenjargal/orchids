## Orchids (YC-backed) mockup - website cloner 🌸
When given a URL, the website cloner uses next.js +  TypeScript as the frontend and fastapi + Anthropic (Claude Sonnet 3.5) + Playwright Chromium in the backend to clone the frontend with HTML. 

### how the application works
**class llm_cloner.py**: interprets scraped data from scraper.py to prompt Claude to recreate the given website given user preferences 

**class scraper.py**: uses Playwright to "scrape" website elements such as HTML, text, images, and forms, to analyze the given website.

**class main.py**: accepts clone requests via REST API + controls API usage

**class utils.py**: ensures URLs are properly formatted, deals with temporary failures (retry logic), and configures logging for debugging


### to install backend:
cd backend
uv sync
uv run fastapi dev

### to install front end:
cd frontend
npm install
npm run dev
