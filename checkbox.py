import pandas as pd
import re
import string
# import utils
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import fitz
from openai import OpenAI
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from scrapper import scraper_func
# import os

norwegian_stopwords = stopwords.words('norwegian')
stopwords = []
for x in norwegian_stopwords:
    if x =='ja':
        pass
    else:
        stopwords.append(x)

def sub_main(filename):
    text,information_text = read_the_pdf_and_checkbox_text(filename)

    question_answeres_checkboxs,information_text = checkbox_values(filename)

    for i in information_text:
        question_answeres_checkboxs.append(i)

    df = pd.DataFrame(question_answeres_checkboxs,columns=['questions','answere'])

    return df

def puntuation_preprocess(text):
  p = re.compile("[" + re.escape(string.punctuation) + "]")
  return re.sub(' +',' ',p.sub("", text).lower())

def remove_stop_words(text):

    text_tokens = word_tokenize(text)
    text_tokens = [word for word in text_tokens if not word in stopwords]

    return ' '.join(text_tokens)

def preprocess(text):
  text = remove_stop_words(puntuation_preprocess(text))
  return text


def gpt_embedding(text):
  client = OpenAI(api_key ='sk-proj-Qjb8HmX7anyLgGATenZaT3BlbkFJ2rxn0QXqk1ldzQmjjSiG')
  response = client.embeddings.create(
    input=text,
    model="text-embedding-3-large"
  )

  return response.data[0].embedding

def pymypdf_reader(filename):

    doc = fitz.open(filename)
    text = ""
    for page in doc:
        text  =  text +page.get_text()
    return text

def read_the_pdf_and_checkbox_text(filename):
  text = pymypdf_reader(filename)
  lines = text.splitlines()
  a_count = 0
  j = 0

  checkbox_state = False
  information_text = []

  for i in range(len(lines)):
    if lines[i] == "Dette skjema vil være en del av salgsoppgaven" or  lines[i] == "Til orientering vil dette skjema være en del av salgsoppgaven":
        checkbox_state = True
    if checkbox_state == True:
        ##information
        if lines[i] =='Meglerfirma':
            information_text.append(
            [lines[i],lines[i+1]]
            )
        elif lines[i] =='Oppdragsnr':
            information_text.append(
            [lines[i],lines[i+1]]
            )
        elif lines[i] =='Selger 1 navn':
            information_text.append(
            [lines[i],lines[i+1]]
            )
        elif lines[i] =='I hvilket forsikringsselskap har du tegnet villa/husforsikring?':

            information_text.append(
            [
                lines[i],lines[i+1] + ' ' + lines[i+2] + ' ' + lines[i+3]  #+ ' ' + lines[1+4]  not able to detect the policy number
            ]
            )

        elif lines[i]=='Hjemmelshavers navn':
            information_text.append(
               [ lines[i] , lines[i+1]    ]
            )
        elif lines[i] == 'Hvor lenge har du eid boligen?':
            information_text.append(
               [ lines[i] , lines[i+1] +' '+lines[i+2]+' '+lines[i+3]+' '+lines[i+4]    ]
            )

        elif lines[i] =='Når kjøpte du boligen?':
            information_text.append(
                [lines[i], lines[i+1] +' '+lines[i+2] ]
            )
        #Beskrivelse
        elif lines[i] =='Kjenner du til om det er/har vært utført arbeid på el-anlegget eller andre installasjoner (f.eks. oljetank, sentralfyr, ventilasjon)?':
            information_text.append(
                [lines[i],  lines[i+1] + ' ' + lines[i+2]  + ' ' + lines[i+3] + ' ' + lines[i+4] + ' ' + lines[i+5] + ' ' + lines[i+6] + ' '  ]
            )

        elif lines[i] =='Kjenner du til om det er utført arbeid på bad/våtrom?':

            information_text.append(
                [lines[i], lines[i+1] +' '+lines[i+2] ]
            )
        elif lines[i] =='Kjenner du til feil eller om har vært utført arbeid/kontroll på vann/avløp?':

            information_text.append(
                [lines[i], lines[i+1] +' '+lines[i+2] ]
            )
        elif lines[i] =='Kjenner du til om det har vært utført arbeid på terrasse/garasje/tak/fasade?':

            information_text.append(
                [lines[i], lines[i+1] +' '+lines[i+2] ]
            )
        else:
            pass

  return text,information_text


def preprocess_with_namespace_token(text):
  text = text.strip()
  return text.replace('\n',' ')

def checkbox_detector(filename):
    checked_values = []
    pdf = fitz.open(filename)
    checked_values = []
    for page in pdf:
            paths = page.get_drawings()
            text = page.get_text()
            words = [w for w in page.get_text(
                "words") if w[4] in ("Nei", "Ja")]

            for w in words:
                r = fitz.Rect(w[:4]) + (-2, -2, 2, 2)  # rect a bit larger
                r.x0 -= 2*r.width  # enlarge to the left to catch checkbox
                l = len([p for p in paths if p["rect"] in r])

                if l >= 6:
                    checked_values.append((w[4]))

    return checked_values

def checkbox_values(filename):
    checkbox_questions_answere_text = []
    
    checkbox_questions=[
        'Er det dødsbo?',
        'Er det salg ved fullmakt?',
        'Har du kjennskap til eiendommen?',
        'Har du bodd i boligen siste 12 måneder?',
        'Kjenner du til om det er/har vært feil tilknyttet våtrommene, f.eks. sprekker, lekkasje, råte, lukt eller soppskader?',
        'Ble tettesjikt/membran/sluk oppgradert/fornyet?',
        'Er arbeidet byggemeldt?',
        'Kjenner du til om det er/har vært tilbakeslag av avløpsvann i sluk eller lignende?',
        'Kjenner du til feil eller om har vært utført arbeid/kontroll på vann/avløp?',
        'Kjenner du til om det er/har vært utettheter i terrasse/garasje/tak/fasade?',
        'Kjenner du til om det er/har vært problemer med ildsted/skorstein/pipe f.eks. dårlig trekk, sprekker, pålegg, fyringsforbud eller lignende?',
        'Kjenner du til om det er/har vært f.eks. sprekker i mur, skjeve gulv eller lignende?',
        'Kjenner du til om det er/har vært sopp/råteskader/insekter/skadedyr på eiendommen som rotter, mus, maur eller lignende?',
        'Kjenner du til om det er/har vært skjeggkre i boligen?',
        'Foreligger det samsvarserklæring (i henhold til forskrift om elektriske lavspenningsanlegg)?',
        'Kjenner du til om det er utført kontroll av el-anlegget og/eller andre installasjoner (f.eks. oljetank, sentralfyr, ventilasjon)?',
        'Har du ladeanlegg/ladeboks for elbil i dag?',
        'Kjenner du til om ufaglærte har utført arbeid som normalt bør utføres av faglærte, utover det som er nevnt tidligere (f.eks. drenering,murerarbeid, tømrerarbeid etc)?',
        'Er det nedgravd oljetank på eiendommen?',
        'Selges eiendommen med utleiedel, leilighet, hybel eller tilsvarende?',
        'Kjenner du til om det er innredet/bruksendret/bygget ut i kjeller eller loft eller andre deler av boligen?',
        'Kjenner du til forslag eller vedtatte reguleringsplaner, andre planer, nabovarsel eller offentlige vedtak som kan medføre endringer i bruken av eiendommen eller av dens omgivelser?',
        'Kjenner du til om det foreligger påbud/heftelser/krav/manglende tillatelser vedrørende eiendommen?',
        'Er det foretatt radonmåling?',
        'Kjenner du til manglende brukstillatelse eller ferdigattest?',
        'Kjenner du til om det foreligger skaderapporter/ tilstandsvurderinger eller utførte målinger?',
        'Er det andre forhold av betydning ved eiendommen som kan være relevant for kjøper å vite om (f.eks. rasfare, tinglyste forhold eller private avtaler)?',
        'Kjenner du til om sameiet/laget/selskapet er involvert i tvister av noe slag?',
        'Kjenner du til vedtak/forslag til vedtak om forhold vedr. eiendommen som kan medføre økte felleskostnader/økt fellesgjeld?',
        'Kjenner du til om det er/har vært sopp/råteskader/insekter/skadedyr i sameiet/laget/selskapet (fellesareal eller i andre boliger) som rotter, mus, maur eller lignende?',
        'Kjenner du til om det er/har vært skjeggkre i sameiet/laget/selskapet (fellesareal eller i andre boliger)?',
    ]

    ##getting the checkboxvalue
    checkbox_values = checkbox_detector(filename)

    ##combining the checkbox values
    text,information_text = read_the_pdf_and_checkbox_text(filename)

    for i,_ in enumerate(checkbox_values):
        checkbox_questions_answere_text.append([preprocess(checkbox_questions[i]),checkbox_values[i]])
    
    return checkbox_questions_answere_text,information_text 

def generating_pdf_questions_embedding(pdf_questions):
    question_embeddings = []
    vector_dict = []
    for x in pdf_questions:
      vector_dict.append([
      gpt_embedding(preprocess(x)),
      preprocess(x),
      ])
    return vector_dict

def predict(filename,question_ask):

    df = sub_main(filename)
    # Compute embedding for the input question
    vector = gpt_embedding(preprocess(question_ask))
    
    # Compute embeddings for all questions in the dataframe
    df['embeddings'] = df['questions'].apply(lambda x: gpt_embedding(preprocess(x)))
    
    # Calculate cosine similarities between the input question and all questions in the dataframe
    df['score'] = df['embeddings'].apply(lambda x: cosine_similarity(np.array(vector).reshape(1, -1), np.array(x).reshape(1, -1))[0][0])
    
    # Find the index of the question with the highest similarity score
    best_index = df['score'].idxmax()
    
    # Retrieve the corresponding question and answer
    best_question = df.loc[best_index, 'questions']
    best_answer = df.loc[best_index, 'answere']
    
    return best_question, best_answer

def box_check(filename,question):
    question,answere = predict(filename,question)
    # print("Answer: ",answere)

    return answere


















# if __name__=="__main__":

#     # url="https://www.finn.no/realestate/homes/ad.html?finnkode=357249489"

#     # filename = url.split("finnkode=")[-1] +".pdf"
#     # status = scraper_func(url,filename)
#     # print(filename,status)

#     pdf_ch = input("What PDF do you want to select: ")
#     pdf_ch = pdf_ch + '.pdf'
#     filename = os.path.join('files', pdf_ch) 

#     norwegian_stopwords = stopwords.words('norwegian')
#     stopwords = []
#     for x in norwegian_stopwords:
#         if x =='ja':
#             pass
#         else:
#             stopwords.append(x)

#     text,information_text = read_the_pdf_and_checkbox_text(filename)

#     question_answeres_checkboxs,information_text = checkbox_values(filename)

#     for i in information_text:
#         question_answeres_checkboxs.append(i)

#     df = pd.DataFrame(question_answeres_checkboxs,columns=['questions','answere'])

#     questions = df['questions'].values.tolist()

#     questions_embedding = generating_pdf_questions_embedding(questions)

    # user_questions = [
    #     'Kjenner du til om det er utført arbeid på bad/våtrom?',
    #     "ble det lagt ny membran?",
    #     "Foreligger det samsvarserklæring?",
    #     "er det foretatt radon måling?",
    #     "er det automat eller skrusikringer?",
    #     "Ble tettesjikt/membran/sluk oppgradert/fornyet?",
    #     "Kjenner du til om det er utført arbeid på bad/våtrom?",
    #     "Kjenner du til feil eller om har vært utført arbeid/kontroll på vann/avløp?",
    #     "Kjenner du til om det er/har vært utført arbeid på el-anlegget eller andre installasjoner (f.eks. oljetank, sentralfyr, ventilasjon)?",
    #     "Kjenner du til om det er utført kontroll av el-anlegget og/eller andre installasjoner (f.eks. oljetank, sentralfyr, ventilasjon)?",
    #     "Kjenner du til om det har vært utført arbeid på terrasse/garasje/tak/fasade?",
    #     "Er det foretatt radonmåling?",
    #     "Kjenner du til om det er/har vært sopp/råteskader/insekter/skadedyr i sameiet/laget/selskapet (fellesareal eller i andre boliger) som rotter, mus, maur eller lignende?",
    #     "Hva er eiers navn?",
    #     "Er det skrusikringer eller automatsikringer?",
    #     "Fortell meg om sluket"
    # ]

    # for i in user_questions:
    #     question,answere = predict(i)
    #     print("question: ",i)
    #     print("*"*20)
    #     print("answer: ",answere)
    #     print("*"*20)

    # temp = True

    # while temp == True:

    #     user_question = input("Please Enter Your Question: ")

    #     question,answere = predict(user_question)
    #     print("*"*20)
    #     print("answer",answere)
    #     print("*"*20)
    #     print("Do you want to continue: "," 1:Yes", " 0:No")
    #     temp = bool(input())
    #     print("*"*20)