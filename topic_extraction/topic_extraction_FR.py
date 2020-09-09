#LIBRERIAS NECESARIAS
import pandas as pd
import unicodedata
import string

from gensim.corpora import Dictionary
from gensim.models import LdaModel
import warnings
warnings.filterwarnings('ignore')

from num2words import num2words
from stop_words import get_stop_words

from datetime import date
import numpy as np
import os.path

#CARGA DE DATOS

language = 'fr'
df = pd.read_csv('../data/news.csv')
df.dropna(inplace=True)
today = np.datetime64(date.today())
df['scraping_date'] = pd.to_datetime(df['scraping_date'], format="%Y/%m/%d")
df = df.loc[df.loc[:, 'scraping_date'] == today]
df_lang = df.drop(df[df.lang != language].index)
df_lang = df_lang['headline']

processed_texts = []
sw_list = get_stop_words(language)

for text in df_lang:
    processed_text = []
    
    # Convierte el texto a minúsuculas
    text = text.lower()
    
    # Eliminar caracteres "extraños"
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    
    # Tabla para eliminar signos de puntuación
    table = str.maketrans('', '', string.punctuation)
    
    # Segmentar texto en frases
    sentences = text.split('.')
       
    prev_word = ""
    prev_word_2 = ""
    for sentence in sentences:
        words = sentence.split(' ')
        # Para cada palabra
        for word in words:
            if word not in string.punctuation and word not in sw_list and len(word)>3:  
                word = word.translate(table)
                if word.isdigit():
                    word = num2words(word, lang=language)
                if prev_word:
                    processed_text.append(prev_word + " " + word)
                    if prev_word_2:
                        processed_text.append(prev_word_2 + " " + prev_word + " " + word)
                prev_word_2 = prev_word
                prev_word = word
                
    processed_texts.append(processed_text)

#MODELO LDA

dictionary = Dictionary(processed_texts)

corpus = [dictionary.doc2bow(doc) for doc in processed_texts]

#ENTRENAMIENTO DEL MODELO
num_topics = 1
lda_model = LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=num_topics,
    iterations=5,
    passes=10,
    alpha='auto'
)

#DESCARGA DE DATOS A FICHEROS

word_dict = {}
today = date.today()
today_path = '../data/topic_today_FR.csv'
hist_path = '../data/topic_history_FR.csv'

for i in range(num_topics):
    words = lda_model.show_topic(i, topn = 10)
    word_dict['date'] = today
    word_dict['Topic #' + '{:02d}'.format(i+1)] = [i[0] for i in words]

topic_today = pd.DataFrame(word_dict)
topic_today.to_csv(today_path, index=False)

if os.path.isfile(hist_path):
    topic_hist = pd.read_csv(hist_path)
    topic_hist = pd.concat([topic_hist, topic_today])
    topic_hist.to_csv(hist_path, index=False)
else:
    topic_today.to_csv(hist_path, index=False)



