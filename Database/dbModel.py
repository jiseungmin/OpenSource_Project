from pymongo import MongoClient

def DB_Save_Article():
  client = MongoClient("mongodb+srv://theBuleocean:opensource418@newssun.ts97rhi.mongodb.net/")
  db = client['news_test']
  url_data = db.URLDATA.find()


  for data in url_data:
    print(data)
    
