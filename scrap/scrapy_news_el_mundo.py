import scrapy
from scrapy.crawler import CrawlerProcess
import json
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup

read_path = './data/' + str(date.today()) + '_url_el_mundo.csv'
df_url = pd.read_csv(read_path, header=None)
urls = list(df_url[0])
write_path = './data/' + str(date.today()) + '_news_el_mundo.csv'


class el_mundo_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = urls
    
    def parse(self, response):
        headline = response.css('h1.ue-c-article__headline ::text').get()
        extract_text = response.css('p').getall()
        extract_text = " ".join(extract_text)
        clean_text = BeautifulSoup(extract_text, "lxml").text
        print(f"\"{headline}\",\"{clean_text}\"", file=filep)

process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})

filep = open(write_path, 'w')
process.crawl(el_mundo_spider)
process.start()
filep.close()
