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

#CARGA DE DATOS

df = pd.read_csv('./data/news.csv', encoding='latin-1')
df.dropna(inplace=True)
df_es = df.drop(df[df.lang != 'es'].index)
df_es = df_es['headline']
processed_texts = []
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
    
    sw_list = get_stop_words('es')
       
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
list(dictionary.items())

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

word_dict = {};
for i in range(num_topics):
    words = lda_model.show_topic(i, topn = 20)
    word_dict['Topic #' + '{:02d}'.format(i+1)] = [i[0] for i in words]
pd.DataFrame(word_dict)