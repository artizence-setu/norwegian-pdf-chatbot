import os
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from openai import OpenAI
from langchain.schema import Document
import checkbox
import chatbot

THRES = 0.1

os.environ["OPENAI_API_KEY"] = "sk-proj-Qjb8HmX7anyLgGATenZaT3BlbkFJ2rxn0QXqk1ldzQmjjSiG"

pdf_ch = input("What PDF do you want to select: ")
pdf_ch = pdf_ch + '.pdf'
filename = os.path.join('files', pdf_ch) 

qu = input("Please ask your Question: ")

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

docs = [Document(page_content=t) for t in checkbox_questions]

embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(docs, embeddings)
# print(f"Total documents in FAISS index: {db.index.ntotal}")

# Perform a similarity search on the query
docs_and_scores = db.similarity_search_with_score(qu)

text = docs_and_scores[0][0].page_content

score = float(docs_and_scores[0][1])

if score<THRES:
    print("Checkbox_question")
    checkbox.box_check(filename,qu)
else:
    print("context_question")
    chatbot.bot_chat(filename,qu)