import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup
import re
import string

today = str(date.today())
newspaper = "publico"
read_path = './data/' + today + '_url_' + newspaper + '.csv'
df_url = pd.read_csv(read_path, header=None)
urls = list(df_url[0])
write_path = './data/' + today + '_news_' + newspaper + '.csv'


class el_mundo_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = urls
    
    def __init__(self):
        print(f"scraping_date,url,headline,text", file=filep)

    def parse(self, response):
        list_replace = ['\n', '"', ',']
        # Extrae el titular
        headline = response.css('h1').get()
        # Elimina las etiquetas span y su contenido
        headline = re.sub(r'<span>.+</span>','',headline)
        # Elimina todas las etiquetas
        headline = BeautifulSoup(headline, "lxml").text
        # Extrae todos los párrafos del artículo
        extract_text = response.css('p.pb-article-item-iteration').getall()
        extract_text = " ".join(extract_text)
        clean_text = BeautifulSoup(extract_text, "lxml").text
        for char in list_replace:
            clean_text = clean_text.replace(char, "")
            headline = headline.replace(char, "")
        print(f"\"{today}\",\"{response.url}\",\"{headline}\",\"{clean_text}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(write_path, 'w')
process.crawl(el_mundo_spider)
process.start()
filep.close()
