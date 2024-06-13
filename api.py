from openai import OpenAI
#from langchain_openai import OpenAI
import pandas as pd
import json 
from utils import preprocess
openapi_key = "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"

client = OpenAI(api_key=openapi_key)

def api_call(text): 

    #context  = [{'role': 'user', 'content': ""},{'role':'','content':}]

    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[ 
              {'role': 'user', 'content': text}],
    
    temperature=0.79,
    max_tokens=2048*2,  
    top_p=1,
    frequency_penalty=0.19,
    presence_penalty=0.42
    #response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    
    return content

def prompter(context,question):
    prompt  = preprocess(context) + preprocess(question)

    resp = api_call(prompt)
    
    return resp

if __name__ == "__main__":
    results = []
    df = pd.read_csv("index_1.csv")
    for x in df.iterrows():
        #print(x[0])
        answere = prompter(x[1]['answere'],x[1]['question'])
        results.append([x[1]['question'],x[1]['answere'],answere])

    df = pd.DataFrame(results,columns=['question','context','answere'])
    df.to_csv("answere.csv")
    #print(prompter(context,question))