from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()

simple_prompt = PromptTemplate(
    template="""
You are a helpful assistant.

Question:
{question}

Answer: 
""",
    input_variables=["question"]
)

model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    google_api_key=os.getenv("gemini"),
    max_output_tokens=500,
    temperature=0.4
)

parser = StrOutputParser()

simple_chain = simple_prompt | model | parser

res = simple_chain.invoke({"question": "hello how its going"})
print(res)
