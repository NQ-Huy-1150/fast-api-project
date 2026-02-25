from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
llm = ChatOllama(model="llama3.2")
chat_history = []
prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system",
        "You are an AI named Llama, a helpful assistant, Answer the user question simple and wisely.",
    ),
    MessagesPlaceholder(variable_name = "chat_history"),
    ("human", "{input}"),
    ]
)
chain = prompt_template | llm

def start_app():
    while True:
        question = input("You: ")
        if question == "done" :
            return
        response = chain.invoke({"input": question, "chat_history": chat_history})
        chat_history.append(HumanMessage(content=question))
        chat_history.append(response)
        print(f"AI: {response.content}")
        print(chat_history)
if __name__ == "__main__":
    start_app()