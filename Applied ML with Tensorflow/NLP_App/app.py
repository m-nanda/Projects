import streamlit as st
import pandas as pd
import numpy as np
import langdetect
from googletrans import Translator
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from PIL import Image
import plotly.express as px
import os
import string
import re

st.set_page_config(page_title='Applied ML App', 
                   page_icon='📰', 
				   layout='wide', 
				   initial_sidebar_state='collapsed')

# Load necessary file
training_setting = pickle.load(open('training_setting.pkl', 'rb'))
tokenizer = pickle.load(open('tokenizer.pkl', 'rb'))
word_index = tokenizer.word_index

#model = load_model('news_cat_model.h5')#, compile=False)
@st.cache(allow_output_mutation=True)
def load_models():
  my_model = load_model('news_cat_model.h5')
  return my_model
model = load_models()

news_categories = ['sport', 'business', 'politics', 'tech', 'entertainment']
news_categories_imgs = ['Sport.png', 'Business.png', 'Politics.png', 'Tech.png', 'Entertainment.png']
dir = './img/'

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])
def decode_article(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])
	
st.title('Applied Machine Learning App with Tensorflow')
st.subheader('News Category Prediction Based on Its Content')
st.write('This application is to predict the topic of a news article based on its content into 5 categories, (_sport_, _business_, _politics_, _tech_, or _entertainment_). Simply enter the article then click the `Predict` button.')

with st.sidebar:
  st.write('## **Contact:**')
  st.write('* **[LinkedIn](https://www.linkedin.com/in/muhammadnanda/)**')
  st.write('* **[Email](mailto:m.nanda98@hotmail.com)**')

placeholder = st.empty()
new_input = placeholder.text_area('Enter the article here', key=1, height=300)
predict_text = st.button('Predict')  

if predict_text:
  text_input = str(new_input)
  if text_input.isspace() or len(text_input)==0:
   st.warning('Please fill in the input text correctly...')
  else: 
    lang = langdetect.detect(text_input)
    if lang!='en':
      text_input = Translator().translate(text_input).text
    text_input = [text_input]	
    text_input_to_seq = tokenizer.texts_to_sequences(text_input)
    pad_text_input_to_seq = pad_sequences(text_input_to_seq, 
										  padding=training_setting['padding_type'], 
										  truncating=training_setting['trunc_type'], 
										  maxlen=training_setting['max_length'])
	
    with st.expander('See Preprocessing'):
      st.info('**1. Initial Input:**')
      st.write(text_input)
      st.info('**2. Convert to Sequence of Number:**')
      st.write('Length of Sequence: **{}**'.format(len(text_input_to_seq[0])))
      st.write(text_input_to_seq[0])
      st.info('**3. Sequence Adjustment for Input:**')
      st.write('Length of Input for Model: **{}**'.format(pad_text_input_to_seq.shape[1]))
      st.write('**Sequence adjustment for input (in numeric form):**')
      st.write(pad_text_input_to_seq[0].tolist())
      st.write('**Sequence adjustment for input (in sentence form):**')
      st.write(decode_article(pad_text_input_to_seq[0]))

    news_pred = model.predict(pad_text_input_to_seq)
    idx = np.argmax(news_pred)-1
    pred_lbl = news_categories[idx].title()
    image = Image.open(dir+news_categories_imgs[idx])
	
	
    st.markdown('#### Category:')    
    col1, col2 = st.columns(2)
    with col1:
      st.image(image, caption=pred_lbl, width=600)
    with col2:
      res_prob = pd.DataFrame({'Category':news_categories, 'Prob':news_pred.tolist()[0][1:]})
      fig = px.bar(res_prob, x='Category', y='Prob', title='Probability of Each Category')
      st.plotly_chart(fig, use_container_width=True)
    
    reset = st.button('Clear Results')	
    if reset:      
      predict_text=False