import pandas as pd

df_news = pd.read_csv('../data/news.csv')
df_urls = df_news['url']
keep = [not x for x in list(df_urls.duplicated())]
df_news = df_news[keep]
df_news.to_csv('../data/news.csv', index=False)