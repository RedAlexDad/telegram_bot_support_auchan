import json
import os

class json_for_logs():
    LOCAL_DIRECTORY_LOGS = f'{os.getcwd()}/Llama2/file_json/logs'

    def write_data(self, data, title=LOCAL_DIRECTORY_LOGS):
        with open(f"{title}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def load_data_all(self, title=LOCAL_DIRECTORY_LOGS):
        with open(f"{title}.json", "r") as file:
            data = json.load(file)
        return data

    def merge_data(self, data_json, id_user='id_user', title=LOCAL_DIRECTORY_LOGS):
        # Если файл существует и не пустой
        try:
            with open(f"{title}.json", encoding="utf-8") as file:
                data = json.load(file)
                temp = data[id_user]
                for info_data in data_json[id_user]:
                    y = {
                        'prompt': info_data['prompt'],
                        'answer': info_data['answer'],
                        'time': info_data['time'],
                        'id_text': info_data['id_text'],
                        'text': info_data['text']
                    }
                temp.append(y)
            self.write_data(data)
        # Если файл не существует
        except:
            self.write_data(data_json)

    def load_data_for_id_user(self, id_user, title=LOCAL_DIRECTORY_LOGS):
        try:
            with open(f"{title}.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                # temp = data[id_user]
                temp = []
                for info_data in data[id_user]:
                    y = {
                        'prompt': info_data['prompt'],
                        'answer': info_data['answer'],
                        'time': info_data['time'],
                        'id_text': info_data['id_text'],
                        'text': info_data['text']
                    }
                    temp.append(y)
            return temp
        except:
            return 'Error! There is no such identifier'


    def delete_data_for_id_user(self, id_user, title=LOCAL_DIRECTORY_LOGS):
        try:
            with open(f"{title}.json", encoding="utf-8") as file:
                data = json.load(file)
                new_data = {}
                for id_user_data in data:
                    if (id_user != id_user_data):
                        temp = data[id_user_data]
                        new_data = {
                            id_user_data: []
                        }
                        for j in temp:
                            y = {
                                'prompt': j['prompt'],
                                'answer': j['answer'],
                                'time': j['time'],
                                'id_text': j['id_text'],
                                'text': j['text']
                            }
                            new_data[id_user_data].append(y)
                        temp.append(new_data)
            self.write_data(new_data)
        except:
            # return 'Error! There is no such identifier'
            pass