from langchain_ollama import ChatOllama, OllamaEmbeddings

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import get_buffer_string

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.document_loaders import PDFMinerLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_postgres.vectorstores import PGVector

from langchain_classic.chains import create_retrieval_chain

from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from dotenv import load_dotenv

import os

load_dotenv()

llm = ChatOllama(model="llama3.2")

chat_history = []

prompt_template = ChatPromptTemplate.from_messages(
    [

    (

        "system",

        "Use the given context to answer the question. If you don't know the answer, say you don't know about it and do nothing.\n\nContext: {context}",

    ),

    MessagesPlaceholder(variable_name = "chat_history"),

    ("human", "{input}"),

    ]

)

file_path ="./src/resources/dia_danh.pdf"

# loader = PDFMinerLoader(file_path)

# documents = loader.load()

# splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

# document_chunks = splitter.split_documents(documents)



embedding = OllamaEmbeddings(model="llama3.2")

# vector_store = PGVector.from_documents(

#     document_chunks, embedding, connection=os.getenv("DATABASE_URL"))

vector = PGVector(embedding, connection=os.getenv("DATABASE_URL"),collection_name="dia_danh.pdf")

retriever = vector.as_retriever(

    search_type="similarity",

    search_kwargs={"k": 5}

)

question_answer_chain = create_stuff_documents_chain(llm, prompt_template)

chain = create_retrieval_chain(retriever, question_answer_chain)

def start_app():

    while True:

        question = input("You: ")

        if question == "done" :

            return

        response = chain.invoke({"input": question, "chat_history": chat_history})

        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(response["answer"]))
        print(type(response["answer"]))
        print(f"AI: {response['answer']}")

if __name__ == "__main__":

    start_app()