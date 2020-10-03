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

from datetime import datetime, date, time, timedelta
import numpy as np
import os.path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#CARGA DE DATOS

cred = credentials.Certificate('../key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

today = date.today()
up_limit = datetime.timestamp(datetime.strptime(str(today)+' 23:59:59','%Y-%m-%d %H:%M:%S'))
low_limit = datetime.timestamp(datetime.strptime(str(today)+' 00:00:00','%Y-%m-%d %H:%M:%S'))
news = db.collection('news').where('date', '>=', low_limit).where('date', '<=', up_limit).stream()
news_list = []
for new in news:
    new = new.to_dict()
    news_list.append(new)

df = pd.DataFrame(news_list)
df.dropna(inplace=True)
df_es = df.drop(df[df.lang != 'es'].index)
df_es = df_es['headline']

processed_texts = []
sw_list = get_stop_words('es')

for text in df_es:
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
                    word = num2words(word, lang='es')
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
now = datetime.now()
today = datetime.timestamp(now)

for i in range(num_topics):
    words = lda_model.show_topic(i, topn = 10)
    word_dict['date'] = today
    word_dict['Topic'] = [i[0] for i in words]

db.collection('topics').add(word_dict)



