from typing import Any, Optional
import requests
from openai import OpenAI
from newsapi import NewsApiClient
from newspaper import Article
import time
from enum import Enum

newsapi = NewsApiClient(api_key='9f63f43bd5284070841dc0c5a02007e9')
OPENAI_API_KEY = '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'
client = OpenAI(
    # base_url='http://localhost:11434/v1/',
    api_key = OPENAI_API_KEY,
)
DEFAULT_MODEL = "gpt-4o-mini" # "gemma2:2b" 

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

    event = "elon musk salute at inauguration"
    articles = fetch_articles(event)[:50]
    grouped = [[], [], []]
    for article in articles:
        # print(texts)
        title = article["title"]
        description = article["description"]
        content = url_to_text(article["url"])
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


if __name__ == "__main__":
    main()
