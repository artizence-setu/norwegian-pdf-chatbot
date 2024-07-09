import os
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from openai import OpenAI
from langchain.schema import Document

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "sk-proj-Qjb8HmX7anyLgGATenZaT3BlbkFJ2rxn0QXqk1ldzQmjjSiG"

def bot_chat(filename,query):

    # Load and process the PDF file
    documents = PdfReader(filename)
    # Extract text from the PDF
    text = ''
    for i in documents.pages:
        text += i.extract_text()

    # Split the text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4",
        chunk_size=200,
        chunk_overlap=20,
    )

    texts = text_splitter.split_text(text)

    # Create Document objects from the split texts
    docs = [Document(page_content=t) for t in texts]

    # Create embeddings and FAISS index
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)
    # print(f"Total documents in FAISS index: {db.index.ntotal}")

    # Perform a similarity search on the query
    docs = db.similarity_search(query)

    # Prepare the prompt template
    PROMPT_TEMPLATE = """
    Answer the question based only on the following context:

    {context}

    ---

    Answer the question based on the above context only in norwegian.
    Please make sure to give full answer.
    Mention details in points.
    : {question}
    """

    context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query)
    # print(prompt)

    # Set up OpenAI client
    openai_api_key = "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"
    client = OpenAI(api_key=openai_api_key)

    # Create the chat completion request
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.2,
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0.19,
        presence_penalty=0.42
    )

    # Extract and print the response content
    content = response.choices[0].message.content
    # print("Answer: ",content)
    return content




















# # Input prompts for the PDF file and the user's question
# pdf_ch = input("What PDF do you want to select: ")
# pdf_ch = pdf_ch + '.pdf'
# filename = os.path.join('files', pdf_ch) 

# query = input("Please Enter Your Question: ")

# # Load and process the PDF file
# documents = PdfReader(filename)
# # Extract text from the PDF
# text = ''
# for i in documents.pages:
#     text += i.extract_text()

# # Split the text into smaller chunks
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#     model_name="gpt-4",
#     chunk_size=200,
#     chunk_overlap=20,
# )

# texts = text_splitter.split_text(text)

# # Create Document objects from the split texts
# docs = [Document(page_content=t) for t in texts]

# # Create embeddings and FAISS index
# embeddings = OpenAIEmbeddings()
# db = FAISS.from_documents(docs, embeddings)
# # print(f"Total documents in FAISS index: {db.index.ntotal}")

# # Perform a similarity search on the query
# docs = db.similarity_search(query)

# # Prepare the prompt template
# PROMPT_TEMPLATE = """
# Answer the question based only on the following context:

# {context}

# ---

# Answer the question based on the above context only in norwegian: {question}
# """

# context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
# prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
# prompt = prompt_template.format(context=context_text, question=query)
# # print(prompt)

# # Set up OpenAI client
# openai_api_key = "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"
# client = OpenAI(api_key=openai_api_key)

# # Create the chat completion request
# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[{'role': 'user', 'content': prompt}],
#     temperature=0.2,
#     max_tokens=4096,
#     top_p=1,
#     frequency_penalty=0.19,
#     presence_penalty=0.42
# )

# # Extract and print the response content
# content = response.choices[0].message.content
# print(content)