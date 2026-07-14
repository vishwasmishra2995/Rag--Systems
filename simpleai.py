from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()

simple_prompt = PromptTemplate(
    template="""
You are a helpful assistant.

Answer the user's question clearly, fully, and in a readable format.
Answer in the SAME language as the user's question.
If you do not know the answer, say:
"I don't have enough information to answer that." (in the user's language)
Use short paragraphs or bullets if they improve readability.
Use chat history to understand follow-up questions.

Chat History:
{chat_history}

Question:
{question}

Answer: 
""",
    input_variables=["question", "chat_history"]
)


model = ChatGoogleGenerativeAI(
    model="models/gemini-3.1-flash-lite",
    google_api_key=os.getenv("gemini"),
    max_output_tokens=800,
    temperature=0.4
)

parser = StrOutputParser()


simple_chain = simple_prompt | model | parser
