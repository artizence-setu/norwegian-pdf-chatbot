import fitz
import os
import pandas as pd
import cassio
from api import prompter
from langchain_community.vectorstores import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.llms import OpenAI
#from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from uuid import uuid4



ASTRA_DB_APPLICATION_TOKEN = "AstraCS:MoqawguiPvzJWNcgyYYybyIU:29e01c400d23005bce3cbe1e26a032fc26334949c4454ec9ff44ec9c2ff7dd31" # enter the "AstraCS:..." string found in in your Token JSON file
ASTRA_DB_ID = "c8fe1576-468d-4a1a-b803-f2129cf49112" # enter your Database ID

OPENAI_API_KEY = "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" # enter your OpenAI key

cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


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

def preprocess(text):
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



def setting_up_vector_db_with_questions(text,checkbox_questions,questions):
    
    table_name = str(uuid4())
    print(table_name)
    astra_vector_store = Cassandra(
    embedding=embedding,
    table_name=table_name,
    session=None,
    keyspace=None,
    )

    # We need to split the text using Character Text Split such that it sshould not increse token size
    text_splitter = CharacterTextSplitter(
        separator = " ",
        chunk_size = 200,
        chunk_overlap  = 0,
        length_function = len,
    )

    texts = text_splitter.split_text(text)


    for x in checkbox_questions:
        texts.append(preprocess(' '.join(x)))

    astra_vector_store.add_texts(texts)
    astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)    

    qa=[]
    gpt_generated_answere = []
    for x in questions:
        query_text = x
        answer = astra_vector_index.query(query_text, llm=llm).strip()

        for doc, score in astra_vector_store.similarity_search_with_score(query_text, k=1):
            qa.append([x,doc,score])
            ##caling the ai for questions and answere generation
            answere = prompter(x[1].page_content,x[0])
            gpt_generated_answere.append(
                [
                 x,
                 answere   
                ]
            )

    return gpt_generated_answere

def chatbot(filename):
##checkbox questions
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

    for x in information_text:
        checkbox_questions.append(x[0])
        checkbox_values.append(x[1])

    #setting_up_vector_db_with_questions()
    checkbox_questions_answere_text = []

    for i,_ in enumerate(information_text):
        temp_text = checkbox_questions[i] + 'answere:- '+ checkbox_values[i]
        checkbox_questions_answere_text.append(temp_text)

    user_questions = ['Kjenner du til om det er/har vært sopp/råteskader/insekter/skadedyr i sameiet/laget/selskapet (fellesareal eller i andre boliger) som rotter, mus, maur eller lignende?'
                      'Kjenner du til om det har vært utført arbeid på terrasse/garasje/tak/fasade?',
                      'er det automat eller skrusikringer?',
                      'er det foretatt radon måling?',
                      'Foreligger det samsvarserklæring?',
                      'ble det lagt ny membran?',
                      'Kjenner du til om det er utført arbeid på bad/våtrom?'                  
    ]
    ##setting up the vector db and questions

    qa = setting_up_vector_db_with_questions(text,checkbox_questions_answere_text,user_questions)
    print(qa)

chatbot("data/outpu1.pdf")
