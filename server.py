from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from typing import List, Dict
import json
import aiohttp
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

async def fetch_news_urls(event: str) -> List[str]:
    # Simulate API call to get news URLs
    await asyncio.sleep(1)  # Simulate API delay
    return [
        "http://example.com/article1",
        "http://example.com/article2",
        # "http://example.com/article3",
        # "http://example.com/article4",
        # "http://example.com/article5",
        # ... more URLs ...
    ]

async def scrape_article(url: str) -> str:
    # Simulate article scraping
    await asyncio.sleep(1)  # Simulate scraping delay
    return "Article content..."

async def categorize_article(content: str) -> str:
    # Simulate ChatGPT categorization
    await asyncio.sleep(1)  # Simulate API delay
    return "left"  # or "right" or "center"

async def generate_summary(articles: List[str]) -> str:
    # Simulate ChatGPT summary generation
    await asyncio.sleep(1)  # Simulate API delay
    return "Summary of articles..."

async def process_event(event: str):
    # Step 1: Fetch URLs
    # yield "data: " + json.dumps({"step": "fetching_urls", "message": "Fetching news articles..."}) + "\n\n"
    yield ("event: " + event + "\n")
    yield "data: <p>fetching news articles</p>" + "\n\n"
    urls = await fetch_news_urls(event)
    
    # Step 2: Process each article
    categorized_articles = {"left": [], "right": [], "center": []}
    
    for i, url in enumerate(urls):
        # yield "data: " + json.dumps({
        #     "step": "processing_article",
        #     "message": f"Processing article {i + 1} of {len(urls)}",
        #     "progress": (i + 1) / len(urls) * 100
        # }) + "\n\n"
        yield ("event: " + event + "\n")
        yield f"data: <p>Processing article {i + 1} of {len(urls)}</p>" + "\n\n"
        
        content = await scrape_article(url)
        category = await categorize_article(content)
        if category in categorized_articles:
            categorized_articles[category].append({"url": url, "content": content})
    
    # Step 3: Generate summaries
    # yield "data: " + json.dumps({"step": "generating_summaries", "message": "Generating summaries..."}) + "\n\n"
    yield ("event: " + event + "\n")
    yield f"data: <p>Generating summaries</p>" + "\n\n"
    
    result = {}
    for category in categorized_articles:
        if categorized_articles[category]:
            summary = await generate_summary([a["content"] for a in categorized_articles[category]])
            result[category] = {
                "summary": summary,
                "articles": [a["url"] for a in categorized_articles[category]]
            }
    
    # Final result
    # yield "data: " + json.dumps({
    #     "step": "complete",
    #     "message": "Processing complete",
    #     "result": result
    # }) + "\n\n"
    yield ("event: " + event + "\n")
    yield "data: <p>Complete</p>" + "\n\n"

    yield "event: close\ndata:\n\n"

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/process/{event}")
async def process(event: str):
    return StreamingResponse(
        process_event(event),
        media_type="text/event-stream"
    )
