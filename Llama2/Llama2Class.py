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
# from json_function import *

# print("Текущий рабочий каталог:", os.getcwd())

class Llama2():
    # To disable this warning, you can either:
    # 	- Avoid using `tokenizers` before the fork if possible
    # 	- Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false)

    # Для отключения ошибок токенизации
    # os.environ["TOKENIZERS_PARALLELISM"] = "false"

    def __init__(self, id_user):
        self.id_user = id_user

        self.logs = dict

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

            embeddings = HuggingFaceEmbeddings(
                model_name='sentence-transformers/all-MiniLM-L6-v2',
                # Expected one of cpu, cuda, ipu, xpu, mkldnn, opengl, opencl, ideep, hip, ve, ort, mps, xla, lazy, vulkan, meta, hpu
                model_kwargs={'device': device})

            start_time = time.time()
            # create and save the local database
            db = FAISS.from_documents(texts, embeddings)
            db.save_local("faiss")
            end_time = time.time()
            time_taken = end_time - start_time
            print(f'Время переобучения модели: {time_taken:.3f} в секундах')

        # with TG bot
        except Exception as e:
            print('Ошибка!\n', e)

    def answer(self, question, max_new_tokens=256, temperature=0.01, device='cpu'):
        # Запоминаем текущее время перед выполнением кода
        start_time = time.time()

        # prepare the template we will use when prompting the AI
        template = """Use the following pieces of information to answer the user's question.
        Context: {context}
        Question: {question}
        Return only the answer below in Russian and nothing more.
        Answer:
        """
        # If you don't know the exact answer, just say that you need to contact the operator's help to resolve legal issues.

        # Объединить с относительным путем к папке модели
        # Ссылка на скачивания модельки (7 ГБ):
        # https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q8_0.bin
        # https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML
        model_dir = os.path.join(self.current_file_dir, "llama-2-7b-chat.ggmlv3.q8_0.bin")

        '''
        Config
            `Parameter`                                 Description
            `top_k`                        The top-k value to use for sampling.
            `top_p`                        The top-p value to use for sampling.
            `temperature`                  The temperature to use for sampling.
            `repetition_penalty`           The repetition penalty to use for sampling.
            `last_n_tokens`                The number of last tokens to use for repetition penalty.
            `seed`                         The seed value to use for sampling tokens.
            `max_new_tokens`               The maximum number of new tokens to generate.
            `stop`                         A list of sequences to stop generation when encountered.
            `stream`                       Whether to stream the generated text.
            `reset`                        Whether to reset the model state before generating text.
            `batch_size`                   The batch size to use for evaluating tokens in a single prompt.
            `threads`                      The number of threads to use for evaluating tokens.
            `context_length`               The maximum context length to use.
            `gpu_layers`                   The number of layers to run on GPU.
        '''
        # https: // github.com / marella / ctransformers
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

        end_time = time.time()
        time_taken = end_time - start_time

        print('Ответ:', output["result"])
        print(f"Время выполнения: {time_taken:.6f} секунд")

        self.logs = {
            self.id_user: [
                {
                    'prompt': question,
                    'answer': output['result'],
                    'time': time_taken,
                    'id_text': None,
                    'text': None
                }
            ]
        }

        print('output:', output['result'])

        # Занесение в БД
        DB_logs = json_for_logs()
        logs_dir = self.current_file_dir + '/file_json/logs'
        DB_logs.merge_data(self.logs, id_user=self.id_user, title=logs_dir)
