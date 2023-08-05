"""
This script reads the database of information from local text files
and uses a large language model to answer questions about their content.
"""

from langchain.llms import CTransformers
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain import PromptTemplate
from langchain.chains import RetrievalQA

import time
# Запоминаем текущее время перед выполнением кода
start_time = time.time()

# prepare the template we will use when prompting the AI
template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Context: {context}
Question: {question}
Only return the helpful answer below and nothing else.
Helpful answer:
"""

# load the language model
llm = CTransformers(model='./llama-2-7b-chat.ggmlv3.q8_0.bin',
                    model_type='llama',
                    config={'max_new_tokens': 256, 'temperature': 0.01})

# load the interpreted information from the local database
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'})
db = FAISS.load_local("faiss", embeddings)

# prepare a version of the llm pre-loaded with the local content
retriever = db.as_retriever(search_kwargs={'k': 2})
prompt = PromptTemplate(
    template=template,
    input_variables=['context', 'question'])
qa_llm = RetrievalQA.from_chain_type(llm=llm,
                                     chain_type='stuff',
                                     retriever=retriever,
                                     return_source_documents=True,
                                     chain_type_kwargs={'prompt': prompt})

# ask the AI chat about information in our local files
prompt = "Who is Scott William"
print('Вопрос:', prompt)
output = qa_llm({'query': prompt})

# Запоминаем текущее время после завершения кода
end_time = time.time()

# Вычисляем время выполнения
time_taken = end_time - start_time

print('Ответ:', output["result"])

print(f"Время выполнения: {time_taken:.6f} секунд")
