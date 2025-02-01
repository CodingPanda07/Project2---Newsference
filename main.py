from typing import Any, Optional
import requests
from openai import OpenAI
from newsapi import NewsApiClient
from newspaper import Article
import time
from enum import Enum

newsapi = NewsApiClient(api_key='9f63f43bd5284070841dc0c5a02007e9')
openai_api_key = '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'
client = OpenAI(api_key = openai_api_key)

class Alignment(Enum):
    Left = 0
    Right = 2
    Center = 1

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
    return Alignment.from_string(response.choices[0].message.content)

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

    articles = fetch_articles("elon musk salute at inauguration")[:5]
    grouped = [[], [], []]
    for article in articles:
        # print(texts)
        description = article["description"]
        content = url_to_text(article["url"])
        print(description)
        # print(content)
        leaning = (determine_political_leaning(content))
        print(leaning)
        grouped[leaning.value].append(description)
        time.sleep(10)

    print(grouped)


if __name__ == "__main__":
    main()
