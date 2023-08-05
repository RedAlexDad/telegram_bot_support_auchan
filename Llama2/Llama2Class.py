from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.llms import CTransformers
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain import PromptTemplate
from langchain.chains import RetrievalQA

import time
import os

from .json_function import json_for_logs

# print("Текущий рабочий каталог:", os.getcwd())

class Llama2():


    # To disable this warning, you can either:
    # 	- Avoid using `tokenizers` before the fork if possible
    # 	- Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false)

    # Для отключения ошибок токенизации
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    def __init__(self, id_user):
        self.id_user = id_user

        self.logs = {
            'id_user': id_user,
            'prompt': None,
            'answer': None,
            'time': None,
            'id_text': None,
            'text': None
        }

        # Объединить с относительным путем к папке
        self.current_file_dir = os.path.dirname(os.path.abspath(__file__))

        self.database = {
            'id_text': None,
            'text': None
        }

    """
    Этот скрипт создает базу данных информации, собранной из локальных текстовых файлов.
    """
    def readfile(self, directory_file='*', chunk_size=500, chunk_overlap=50, device='cpu'):
        # define what documents to load
        # without TG bot
        try:
            # Объединить с относительным путем к папке "file_txt"
            file_txt_dir = os.path.join(self.current_file_dir, "file_txt")

            # print("Текущий рабочий каталог:", os.getcwd())
            loader = DirectoryLoader(file_txt_dir, glob=f"{directory_file}.txt", loader_cls=TextLoader)
            # loader = DirectoryLoader(f"./file_txt/", glob="*.txt", loader_cls=TextLoader)
            # loader = DirectoryLoader(f"./file_json/", glob="*.json", loader_cls=TextLoader)
            # loader = DirectoryLoader(f"./", glob="*.txt", loader_cls=TextLoader)
            # loader = DirectoryLoader(f"{os.getcwd()}/file_txt/", glob="*.txt", loader_cls=TextLoader)
            # loader = DirectoryLoader(f"{os.getcwd()}/", glob="*.txt", loader_cls=TextLoader)

            # interpret information in the documents
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

            texts = splitter.split_documents(documents)

            self.database = {
                'id_text': None,
                'text': texts
            }

        # with TG bot
        except:
            return "Unable to find the database"


        embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            # Expected one of cpu, cuda, ipu, xpu, mkldnn, opengl, opencl, ideep, hip, ve, ort, mps, xla, lazy, vulkan, meta, hpu
            model_kwargs={'device': device})

        # create and save the local database
        db = FAISS.from_documents(texts, embeddings)
        db.save_local("faiss")

    def answer(self, question, max_new_tokens=256, temperature=0.01, device='cpu'):
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

        # Объединить с относительным путем к папке модели
        # Ссылка на скачивания модельки (7 ГБ):
        # https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q8_0.bin
        # https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML
        model_dir = os.path.join(self.current_file_dir, "llama-2-7b-chat.ggmlv3.q8_0.bin")

        # load the language model
        llm = CTransformers(model=model_dir,
                            model_type='llama',
                            config={'max_new_tokens': max_new_tokens,
                                    'temperature': temperature})

        # load the interpreted information from the local database
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': device})

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
        # prompt = "Who is Scott William"
        # print('Вопрос:', question)

        output = qa_llm({'query': question})

        # Запоминаем текущее время после завершения кода
        end_time = time.time()
        # Вычисляем время выполнения
        time_taken = end_time - start_time

        # print('Ответ:', output["result"])
        # print(f"Время выполнения: {time_taken:.6f} секунд")

        self.logs = {
            'id_user': self.id_user,
            'prompt': question,
            'answer': output['result'],
            'time': time_taken
        }

        print('output:', output['result'])

        # Занесение в БД
        DB_logs = json_for_logs()
        logs_dir = self.current_file_dir + '/file_json/logs'
        DB_logs.merge_data(self.logs, id_user=self.id_user, title=logs_dir)
