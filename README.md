## Orchids (YC-backed) mockup - website cloner 🌸
A mock website cloning tool developed as a take-home project for the Orchids internship final "interview." When given a URL, the application uses Next.js + TypeScript on the frontend and FastAPI + Playwright Chromium + Anthropic’s Claude Sonnet 3.5 on the backend to reconstruct the website's HTML and content.

⚠️ This project is purely for educational purposes. I am **not** attempting to copy or replicate Orchids' business model in any way.


<img width="1728" alt="github-readme-orchids" src="https://github.com/user-attachments/assets/728c180e-8c27-4d34-ba28-1fc7f613c89d" />


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

