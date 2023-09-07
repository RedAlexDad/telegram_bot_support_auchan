#!/usr/bin/env python
#-*- coding: utf-8 -*-
import boto3

from config import aws_access_key_id, aws_secret_access_key, region_name

class StorageDB():
    def __init__(self):
        session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.s3 = session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net'
        )

    # Создать новый бакет
    def create_new_bucket(self, bucket_name:str):
        self.s3.create_bucket(Bucket=bucket_name)

    # Загрузить объекты в бакет
    ## Из строки
    def load_object_in_bucket_string(self, bucket_name:str, object_name:str, body_name:str, storage_class:str):
        self.s3.put_object(Bucket=bucket_name, Key=object_name, Body=body_name, StorageClass=storage_class)

    ## Из файла
    def load_object_in_bucket_file(self, file_name:str, bucket_name:str, key:str):
        self.s3.upload_file(Filename=file_name, Bucket=bucket_name, Key=key)


    # Получить список объектов в бакете
    def give_list_objetct_from_bucket(self, bucket_name:str):
        for key in self.s3.list_objects(Bucket=bucket_name)['Contents']:
            print(key['Key'])

    # Удалить несколько объектов
    def delete_any_bucket(self, bucket_name:str, object_name:str, path_directory:str):
        forDeletion = [{'Key':object_name}, {'Key':path_directory}]
        response = self.s3.delete_objects(Bucket=bucket_name, Delete={'Objects': forDeletion})

    # Получить объект
    def give_object(self, bucket_name:str, file_name:str):
        get_object_response = self.s3.get_object(Bucket=bucket_name,Key=file_name)
        # print(get_object_response['Body'].read())
        return get_object_response['Body'].read()
