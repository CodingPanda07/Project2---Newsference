from typing import Any, Optional
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from typing import List, Dict
import json
import aiohttp
import time
import requests
from openai import OpenAI
from newsapi import NewsApiClient
from newspaper import Article
import time
from enum import Enum

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

newsapi = NewsApiClient(api_key='9f63f43bd5284070841dc0c5a02007e9')
OPENAI_API_KEY = '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'
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key = OPENAI_API_KEY,
)
DEFAULT_MODEL = "yi:9b-chat-v1.5-q6_K"  # "gpt-4o-mini"

class Alignment(Enum):
    Left = 0
    Center = 1
    Right = 2

    @classmethod
    def from_string(cls, value: str) -> Optional['Alignment']:
        # Mapping of strings to enum members
        string_map = {
            "left": cls.Left,
            "right": cls.Right,
            "center": cls.Center
        }

        try:
            return string_map[value.lower()]
        except KeyError:
            return None

# # Example usage
# print(Alignment.Left.value)        # Output: 0
# print(Alignment.Right.value)       # Output: 2
# print(Alignment.Center.value)      # Output: 1
#
# print(Alignment.from_string("left"))    # Output: Alignment.Left (with value 0)
# print(Alignment.from_string("RIGHT"))   # Output: Alignment.Right (with value 2)
# print(Alignment.from_string("invalid")) # Output: None

def fetch_articles(topic) -> list[Any]:
    '''
    API call to NewsAPI, fetch article links

    topic - user input, topic of articles to parse
    '''
    # url_list = []
    response = newsapi.get_everything(q=topic, language='en', sort_by="popularity")
    articles = response["articles"]
    # for article in articles['articles']:
    #     url_list.append(article['url'])
    return articles

def url_to_text(url: str) -> str:
    '''
    Convert list of urls to list of article text
    '''
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def determine_political_leaning(article: str) -> Alignment:
    '''
    API call to ChatGPT, give political rating
    '''
    prompt = '''
    Read this news article and determine whether it is politically left, right, or center-leaning.
    If you are unsure, just reply "center".
    Respond with EXACTLY one word: left, right, or center. Do not explain the reasoning.
    VERY IMPORTANT: respond with EXACTLY one word: "left", "right", or "center".
    The article may not be properly formatted, causing no useful information to
    be extracted. In that case, reply with "center".

    Since the contents of the article may be long and contain many breaks, the
    content is enclosed in a pair of TWO words: "CONTENT BEGIN" and "CONTENT
    END". Keep that in mind when reading the article.

    If there is an error reading the content, reply with "center".

    The article is as follows:

    CONTENT BEGIN
    {0}
    CONTENT END
    '''

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        store=False,
        messages=[
            {
                "role": "user",
                "content": prompt.format(article),
            }
        ],
    )
    print(response.choices[0])
    return Alignment.from_string(response.choices[0].message.content.strip()) or Alignment.Center

def summarize_articles(event: str, articles: list[Any]) -> str:
    prompt = f'''
    Summarize to me, in one to three key points, on what happend in the event "{event}".

    You're allowed to use existing knowledge, plus the information provided in
    the following articles. You do NOT need to maintain netural or bias-less.
    Your job is to accurately report what the information that the articles provided
    tell about the event asked, even though the articles themselves might be
    biased towards one side or the other.

    Since the contents of the articles may be long and contain many breaks, each
    content is enclosed in a pair of TWO words: "CONTENT BEGIN" and "CONTENT
    END". Keep that in mind when reading the articles.

    Output your summary in HTML format. Output plain, raw HTML ONLY.
    DO NOT add a heading element. Assume that the HTML is already inside a <body></body>.
    Summarize in bullet points.
    Remember to surround the bullet points with <ul></ul>, and for each bullet
    point it should be in a <li></li>.

    Here are the articles:
    '''

    for i, article in enumerate(articles):
        prompt += f'''

        Article {i + 1}:
        Title: {article["title"]}
        Description: {article["description"]}
        Content:
        CONTENT BEGINS
        {article["content"]}
        CONTENT ENDS
        '''

    response = client.chat.completions.create(
        model = DEFAULT_MODEL,
        store = False,
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return response.choices[0].message.content

async def main():
    # topic = input("Enter the article topic: ")
    # articles = fetch_articles(topic)
    
    # left_articles = []
    # center_articles = []
    # right_articles = []

    # for article in articles:
    #     url = article['url']
    #     leaning = determine_political_leaning(url)
    #     if leaning == 'left':
    #         left_articles.append(url)
    #     elif leaning == 'center':
    #         center_articles.append(url)
    #     elif leaning == 'right':
    #         right_articles.append(url)

    # left_summary = summarize_articles(left_articles)
    # center_summary = summarize_articles(center_articles)
    # right_summary = summarize_articles(right_articles)

    # print("Left Articles Summary:")
    # print(left_summary)
    # print("\nCenter Articles Summary:")
    # print(center_summary)
    # print("\nRight Articles Summary:")
    # print(right_summary)

    event = "elon musk salute at inauguration"
    articles = fetch_articles(event)[:5]
    grouped = [[], [], []]
    for article in articles:
        # print(texts)
        title = article["title"]
        description = article["description"]
        content = url_to_text(article["url"])
        article["contet"] = content
        print(title)
        leaning = (determine_political_leaning(content))
        print(leaning)
        grouped[leaning.value].append(article)
        # time.sleep(10)

    for leaning in Alignment:
        print(leaning)
        relevant_articles = grouped[leaning.value]
        if len(relevant_articles) < 2:
            print("Not enough articles to tell")
        else:
            print(summarize_articles(event, relevant_articles))

async def process_event(event: str):
    yield ("event: " + event + "\n")
    yield "data: <p>fetching news articles</p>" + "\n\n"
    # event = "elon musk salute at inauguration"
    articles = (fetch_articles(event))[:5]

    grouped = [[], [], []]
    for i, article in enumerate(articles):
        yield ("event: " + event + "\n")
        yield f"data: <p>Processing article {i + 1} of {len(articles)}</p>" + "\n\n"

        # print(texts)
        title = article["title"]
        description = article["description"]
        content = url_to_text(article["url"])
        # print(title)
        leaning = (determine_political_leaning(content))
        # print(leaning)
        grouped[leaning.value].append(article)
        # time.sleep(10)

    yield ("event: " + event + "\n")
    yield f"data: <p>Generating summaries</p>" + "\n\n"

    final_html = '''
    '''
    for leaning in Alignment:
        print(leaning)
        relevant_articles = grouped[leaning.value]
        final_html += f"<div id={leaning.name.lower()} class='tabcontent'>\n"
        if len(relevant_articles) == 0:
            print("Not enough articles to tell")
        else:
            summary = (summarize_articles(event, relevant_articles))
            print(summary)
            final_html += f'''
                <div class="summary">Summary</div>
                <div class="summary-text">
                    {summary}
                </div>
                <div class="line"></div>
                <div class="articles">Articles</div>
                <div class="article-text">
                </div>
            '''
        final_html += f"</div>\n"
    print(final_html)

    yield ("event: " + event + "\n")
    for line in final_html.splitlines():
        yield f"data: {line}" + "\n"
    yield "\n"

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

@app.post("/submit", response_class=HTMLResponse)
async def submit(text: str = Form(...)):
    event = text.strip()
    return f'''
        <div id="sseContainer"
             hx-ext="sse"
             sse-swap="{event}"
             sse-connect="/process/{event}"
             sse-close="close">
            <p>Hello</p>
        </div>
    '''


if __name__ == "__main__":
    main()
