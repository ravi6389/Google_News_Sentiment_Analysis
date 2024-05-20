import gradio as gr
import selenium
import requests
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from transformers import pipeline

# Search Query
def news_and_analysis(query):

# Encode special characters in a text string
    def encode_special_characters(text):
        encoded_text = ''
        special_characters = {'&': '%26', '=': '%3D', '+': '%2B', ' ': '%20'}  # Add more special characters as needed
        for char in text.lower():
            encoded_text += special_characters.get(char, char)
        return encoded_text

    query2 = encode_special_characters(query)
    url = f"https://news.google.com/search?q={query2}&hl=en-US&gl=in&ceid=US%3Aen&num=3"

    response = requests.get(url, verify = False)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('article')
    links = [article.find('a')['href'] for article in articles]
    links = [link.replace("./articles/", "https://news.google.com/articles/") for link in links]

    news_text = [article.get_text(separator='\n') for article in articles]
    news_text_split = [text.split('\n') for text in news_text]

    news_df = pd.DataFrame({
        'Title': [text[2] for text in news_text_split],
        'Source': [text[0] for text in news_text_split],
        'Time': [text[3] if len(text) > 3 else 'Missing' for text in news_text_split],
        'Author': [text[4].split('By ')[-1] if len(text) > 4 else 'Missing' for text in news_text_split],
        'Link': links
    })

    news_df = news_df.loc[0:5,:]
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.use_chromium = True
    driver = webdriver.Chrome(options = options)

    classification= pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
    
    news_df['Sentiment'] = ''
    for i in range(0, len(news_df)):
        # driver.get(news_df.loc[i,'Link'])
        # time.sleep(10)
        # headline = driver.find_element('xpath', '//h1').text
        #news_df.loc[i, 'Headline'] = headline
        title = news_df.loc[i, 'Title']
        news_df.loc[i, 'Sentiment'] = str(classification(title))
        print(news_df)

    return(news_df)

with gr.Blocks() as demo:

  
    topic= gr.Textbox(label="Topic for which you want Google news and sentiment analysis")
    
    btn = gr.Button(value="Submit")
    btn.click(news_and_analysis, inputs=topic, outputs= gr.Dataframe())

demo.launch()
