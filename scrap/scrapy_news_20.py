import pandas as pd
import scrapy
import json
from scrapy.crawler import CrawlerProcess
from datetime import date

read_path = './data/' + str(date.today()) + '_url_20min.csv'
df_url = pd.read_csv(read_path, header=None)
urls = list(df_url[0])
write_path = './data/' + str(date.today()) + '_news_20min.csv'

class veinte_minutos_noticia_spider(scrapy.Spider):
    name = 'blogspider'
    start_urls = urls
    def parse(self, response):

        for article in response.css('main'):
            headline = article.css('section div h1 ::text').extract_first().strip()
            extract_text = article.css('section article div p ::text').getall()
            extract_text = " ".join(extract_text)
            print(f"\"{headline}\",\"{extract_text}\"", file=filep)


process = CrawlerProcess({
    'USER_AGENT': 'Google SEO Bot'
})


filep = open(write_path, 'w')
process.crawl(veinte_minutos_noticia_spider)
process.start()
filep.close()