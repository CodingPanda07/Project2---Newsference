from typing import Any
import requests
from openai import OpenAI
from newsapi import NewsApiClient
from newspaper import Article


newsapi = NewsApiClient(api_key='9f63f43bd5284070841dc0c5a02007e9')
openai_api_key = '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'
client = OpenAI(api_key = openai_api_key)

def fetch_articles(topic) -> list[Any]:
    '''
    API call to NewsAPI, fetch article links

    topic - user input, topic of articles to parse
    '''
    # url_list = []
    articles = newsapi.get_everything(q=topic, language='en', sort_by="popularity")
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

def determine_political_leaning(article: str) -> str:
    '''
    API call to ChatGPT, give political rating
    '''
    prompt = '''
    Read this article and determine whether it is politically left, right, or center-leaning.
    Only respond with one-word: left, right, or center. Do not explain the reasoning. The article is as follows:
    '''

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        store=False,
        messages=[
            {
                "role": "user",
                "content": prompt + article,
            }
        ],
    )
    return (response.choices[0].message)

def summarize_articles(urls):
    # Hypothetical API call to GeminiAPI for summarization
    response = requests.post('https://geminiapi.com/summarize', json={'urls': urls, 'apiKey': GEMINI_API_KEY})
    return response.json().get('summary')

def main():
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

    articles = fetch_articles("DC Plane Crash")[:5]
    for article in articles:
        # print(texts)
        print(article["description"])
        content = url_to_text(article["url"])
        print(determine_political_leaning(content))
     


if __name__ == "__main__":
    main()
