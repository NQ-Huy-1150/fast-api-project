from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2", temperature=0.8)
messages = [
    (
        "system",
        "You are a helpful assistant, Answer the user question wisely",
    ),
    ("human", "hi llama3.2"),
]
ai_answer = llm.invoke(messages)

print(ai_answer.content)