from fastapi import FastAPI
from pydantic import BaseModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import os


class Input(BaseModel):
    content: str = None


docs_path = os.path.join(os.path.dirname(__file__), 'data', 'docs.txt')
loader = TextLoader(docs_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
vector = FAISS.from_documents(documents, embeddings)

memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:
#
# <context>
# {context}
# </context>
#
# Question: {input}""")

prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer the user's question based on the context: 
                <context>
                {context}
                </context>
                """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ]
)

llm = ChatOpenAI()
document_chain = create_stuff_documents_chain(llm, prompt)
retriever = vector.as_retriever(search_kwargs={'k': 1})

retriever_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("human",
     "Given the previous conversation, generate a search query to look up so that the information in previous conversation is considered")
])

# retrieval_chain = create_retrieval_chain(retriever, document_chain)
retrieval_chain = create_history_aware_retriever(
    llm=llm,
    retriever=retriever,
    prompt=retriever_prompt
)

chat_history = []

app = FastAPI()


@app.get("")
def read_root():
    return {"message": "This is Artisan ChatBot"}


@app.post("/chat")
def get_answer(input: Input):
    try:
        response = retrieval_chain.invoke(
            {
                "input": input.content,
                "chat_history": chat_history
            }
        )
        chat_history.append(HumanMessage(content=input.content))
        chat_history.append(AIMessage(content=response["answer"]))
        while len(chat_history) > 20:
            chat_history.pop(0)
        return {"answer": response["answer"]}
    except Exception as e:
        return {"answer": str(e)}