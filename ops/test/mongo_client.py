from pymongo import MongoClient
client = MongoClient("mongodb://192.168.20.132:27017", username="root", password="123456a@")
print(list(client.list_databases()))
