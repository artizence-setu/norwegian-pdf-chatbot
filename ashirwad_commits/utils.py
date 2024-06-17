from io import StringIO
from nltk import word_tokenize , sent_tokenize
import re
import numpy as np
import nltk
nltk.download('punkt')


def number_finder_preprocess(text):
  if text.isdigit():
    return np.nan
  else:
    return text

def if_only_yes_or_no_preprocess(text):
  if 'nei' == text.strip().lower():
    return np.nan
  elif 'ja' == text.strip().lower():
    return np.nan
  return text

def if_blank(text):
  if text.strip() == '':
    return np.nan
  return text

def clean_html(text):  
  html = re.compile('<.*?>')#regex
  return html.sub(r'',text)

def remove_special_characters(text):
    # define the pattern to keep
    pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]' 
    return re.sub(pat, ' ', text)

def punct(text):
    # define punctuation
    text = re.sub(pattern = "\W",
        repl = " ",
        string = text)
    return str(text)

def remove_multiple_spaces(text):
  '''
  remove multiple white space in string
  '''
  text=  re.sub(' +', ' ',text)
  return text

def preprocess(text):
    text =  clean_html(text)
    text =  remove_multiple_spaces(text)
    text = remove_special_characters(text)
    text = punct(text)
    return text

