import unittest

# from json_function import load_data_all, write_data, merge_data, load_data_for_id_user, delete_data_for_id_user
from ..json_function import json_for_logs


data_json = {
    "id_user": [
        {
            "prompt": "Who AlexDad?",
            "answer": "AlexDad is DataScience",
            "time": "60",
            "id_text": 1,
            "text": "Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet."
        }
    ]
}

data_json1 = {
    "id_user": [
        {
            "prompt": "Who Pavel Durov?",
            "answer": "Pavel Durov created Telegram",
            "time": "30",
            "id_text": 2,
            "text": "“JupyterGoBoom” is the name of a Python package for creating unmaintainable Jupyter notebooks. It is no longer actively developed and is now considered obsolete because modern software developers have come to realize that Jupyter notebooks grow to become unmaintainable all by themselves."
        }
    ]
}


data_json_with_id = {
    "369350471": [
        {
            "prompt": "Who Keanu Reeves?",
            "answer": "Kiany Rivs is pretty boy",
            "time": "60",
            "id_text": 1,
            "text": "Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet."
        }
    ]
}

data_json_with_id_1 = {
    "369350471": [
        {
            "prompt": "Who James Bond?",
            "answer": "James Bond is Military Special Forces",
            "time": "100",
            "id_text": 1,
            "text": "Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet."
        }
    ]
}

data_json_two_users = {
  "369350478": [
      {
        "prompt": "Who Keanu Reeves?",
        "answer": "Kiany Rivs is pretty boy",
        "time": "1",
        "id_text": 1,
        "text": "Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet."
      }
  ],
  "198498415": [
    {
        "prompt": "Who James Bond?",
        "answer": "James Bond is Military Special Forces",
        "time": "100",
        "id_text": 1,
        "text": "Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet."
    },
    {
        "prompt": "Who Elon Musk?",
        "answer": "Elon Musk is American entrepreneur",
        "time": "50",
        "id_text": 1,
        "text": "Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet."
    },
    {
        "prompt": "What is a computer like?",
        "answer": "a device or system capable of automatically performing a given",
        "time": "70",
        "id_text": 1,
        "text": "Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet."
    }
  ]
}

class test_json(unittest.TestCase):
    # Проверка на присутствия файла
    def test_write_and_read_file(self):
        JS_class = json_for_logs()

        # Создаем файл с данным
        JS_class.write_data(data=data_json)

        # Проверяем на наличие и сходимости
        self.assertEqual(
            JS_class.load_data_all(),
            {'id_user': [
                {'prompt': 'Who AlexDad?',
                 'answer': 'AlexDad is DataScience',
                 'time': '60',
                 'id_text': 1,
                 'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'}
            ]}
        )

    # Проверка на добавлении json дата
    def test_append_json_in_json(self):
        JS_class = json_for_logs()

        # Создаем файл с данным
        JS_class.write_data(data_json)

        # Изменяем файл - добавление новые данных
        JS_class.merge_data(data_json1)

        # Проверяем на наличие и сходимости
        self.assertEqual(
            JS_class.load_data_all(),
            {'id_user': [
                {'prompt': 'Who AlexDad?',
                 'answer': 'AlexDad is DataScience',
                 'time': '60',
                 'id_text': 1,
                 'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
                },
                {'prompt': 'Who Pavel Durov?',
                 'answer': 'Pavel Durov created Telegram',
                 'time': '30',
                 'id_text': 2,
                 'text': '“JupyterGoBoom” is the name of a Python package for creating unmaintainable Jupyter notebooks. It is no longer actively developed and is now considered obsolete because modern software developers have come to realize that Jupyter notebooks grow to become unmaintainable all by themselves.'
                 }
            ]})

    # Проверка на добавлении json дата с идентификатором пользователя
    def test_and_read_file_with_id(self):
        JS_class = json_for_logs()

        # Создаем файл с данным
        JS_class.write_data(data_json_with_id)

        # Проверяем на наличие и сходимости
        self.assertEqual(
            JS_class.load_data_all(),
            {'369350471': [
                {'prompt': 'Who Keanu Reeves?',
                 'answer': 'Kiany Rivs is pretty boy',
                 'time': '60',
                 'id_text': 1,
                 'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
                 }
            ]})


    # Проверка на добавлении json дата с идентификатором пользователя
    def test_append_json_in_json_with_id(self):
        JS_class = json_for_logs()

        # Создаем файл с данным
        JS_class.write_data(data_json_with_id)

        # Изменяем файл - добавление новые данных
        JS_class.merge_data(data_json_with_id_1, str(369350471))

        # Проверяем на наличие и сходимости
        self.assertEqual(
            JS_class.load_data_all(),
            {'369350471': [
                {'prompt': 'Who Keanu Reeves?',
                 'answer': 'Kiany Rivs is pretty boy',
                 'time': '60',
                 'id_text': 1,
                 'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
                 },
                {'prompt': 'Who James Bond?',
                 'answer': 'James Bond is Military Special Forces',
                 'time': '100',
                 'id_text': 1,
                 'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
                 }
            ]})

    def test_search_id_user_and_get_info(self):
        JS_class = json_for_logs()

        # Создаем файл с данным
        JS_class.write_data(data_json_two_users)

        # Проверяем на наличие и сходимости
        self.assertEqual(
            JS_class.load_data_for_id_user('198498415'),
            [{'prompt': 'Who James Bond?',
             'answer': 'James Bond is Military Special Forces',
             'time': '100',
             'id_text': 1,
             'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
             },
             {'prompt': 'Who Elon Musk?',
              'answer': 'Elon Musk is American entrepreneur',
              'time': '50',
              'id_text': 1,
              'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
              },
             {'prompt': 'What is a computer like?',
              'answer': 'a device or system capable of automatically performing a given',
              'time': '70',
              'id_text': 1,
              'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
              }
        ])


    def test_delete_data_of_id_user(self):
        JS_class = json_for_logs()

        # Создаем файл с данным
        JS_class.write_data(data_json_two_users)

        # Удаляем данные по id пользователя
        JS_class.delete_data_for_id_user('369350478')

        # Проверяем на наличие и сходимости
        self.assertEqual(
            JS_class.load_data_for_id_user('198498415'),
            [{'prompt': 'Who James Bond?',
              'answer': 'James Bond is Military Special Forces',
              'time': '100',
              'id_text': 1,
              'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
              },
             {'prompt': 'Who Elon Musk?',
              'answer': 'Elon Musk is American entrepreneur',
              'time': '50',
              'id_text': 1,
              'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
              },
             {'prompt': 'What is a computer like?',
              'answer': 'a device or system capable of automatically performing a given',
              'time': '70',
              'id_text': 1,
              'text': 'Scott William Harden is an open-source software developer. He is the primary author of ScottPlot, pyabf, FftSharp, Spectrogram, and several other open-source packages. Scott’s favorite color is dark blue despite the fact that he is colorblind. Scott’s advocacy for those with color vision deficiency (CVD) leads him to recommend perceptually uniform color maps like Viridis instead of traditional color maps like Spectrum and Jet.'
              }
             ])