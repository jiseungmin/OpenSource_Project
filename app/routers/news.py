import numpy as np
from bson import ObjectId
from fastapi import APIRouter
from pymongo import MongoClient
from sklearn.cluster import DBSCAN
from app.GPT.gpt import GptapiResult
from app.models import ClustertRequest
from app.models import IntegretionNews
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from app.Image_Similarity.Similarity import Similarity_Image_and_Text

router = APIRouter()

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://theBuleocean:opensource418@newssun.ts97rhi.mongodb.net/?retryWrites=true&w=majority')

def parse_date(date_str):
    date_str = date_str.replace("오전", "AM").replace("오후", "PM")
    return datetime.strptime(date_str, "%Y.%m.%d. %p %I:%M")

def convert_object_id(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: convert_object_id(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_object_id(i) for i in obj]
    return obj

# 뉴스 통합 API
@router.get("/Integrated_news")
def read_news(request: IntegretionNews):
    db = client['Top_Today_News']
    collection = db[request.category]
    
    image_urls = {}
    news_lists = {}
    response_data = {}
    thumbnail_images = []
    all_full_contents = []
    
    # TodayDB에서 데이터 제목, 본문내용, 썸네일 가져오기 
    news_items = list(collection.find({}, {'news_content': 1}))
    
    # _id 필드를 문자열로 변환
    news_items = [convert_object_id(item) for item in news_items]
    
    # 각 ObjectId별로 데이터를 추출하여 JSON 응답 생성
    for idx, item in enumerate(news_items):
        if 'news_content' in item:
            response_data[idx + 1] = [content['content'] for content in item['news_content']]
            image_urls[idx + 1] = [content['image'] for content in item['news_content']]
            news_lists[idx + 1] = [content['url'] for content in item['news_content']]
    
    for i in range(1, len(response_data) + 1):
        # GPT를 이용하여 전체 본문 내용 뽑아내기
        wise_new_full_content = GptapiResult(response_data[i])  # 여기서 wise_new_full_content 정의
        all_full_contents.append(wise_new_full_content)
        print(wise_new_full_content)
        print(image_urls[i])
        
        # 기사 본문과 제일 유사한 이미지 뽑아내기
        Thumbnail_image = Similarity_Image_and_Text(wise_new_full_content, image_urls[i])
        thumbnail_images.append(Thumbnail_image)
    
    # 정보 파싱 후 DB 저장 (title, newsurlList, full_contents, Thumbnail_image, category)
    db = client['Integrated_news']
    save_collection = db['Society']
    for i in range(1, len(response_data) + 1):
        title = news_items[i - 1]['news_content'][0]['title']  # 마지막 데이터 저장할 때 title 설정
        news_data = {
            "title": title,  # 첫 번째 news_content의 title 사용
            "newsurlList": news_lists[i],
            "full_contents": all_full_contents[i - 1],
            "Thumbnail_image": thumbnail_images[i - 1],
        }
        save_collection.insert_one(news_data)
    
    return {
        "wise_new_full_content": all_full_contents,
        "thumbnail_images": thumbnail_images,
    }

            

## 뉴스 클러스터링 API
@router.post("/newscluster")
def newscluster(request: ClustertRequest):
    collection_name = request.collection_name
    date_str = request.date_str
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    
    # 1. MongoDB에서 데이터 가져오기
    db = client['news_database']
    collection = db[collection_name]
    news_items = list(collection.find({}, {'title': 1, 'publishedAt': 1, 'url': 1, 'urlToImage': 1, 'content': 1}))
    
    filtered_news_items = [
        item for item in news_items 
        if parse_date(item['publishedAt']).date() == date_obj.date()
    ]
    
    titles = [item['title'] for item in filtered_news_items]
    urls = [item['url'] for item in filtered_news_items]
    images = [item['urlToImage'] for item in filtered_news_items]
    contents = [item['content'] for item in filtered_news_items]
    
    # 2. TF-IDF 벡터라이저를 사용하여 제목을 벡터로 변환
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(titles)

    # 3. 코사인 거리를 거리 행렬로 변환
    distance_matrix = pairwise_distances(X, metric='cosine')

    # 4. DBSCAN 클러스터링 모델 설정
    dbscan = DBSCAN(eps=0.7, min_samples=2, metric='precomputed')

    # 5. DBSCAN을 사용하여 클러스터링 수행
    dbscan.fit(distance_matrix)

    # 6. 각 제목에 대한 클러스터 할당 결과를 딕셔너리에 저장
    clusters = {}
    for i, (title, url, image, content) in enumerate(zip(titles, urls, images, contents)):
        cluster_id = int(dbscan.labels_[i])
        if cluster_id != -1:
            if cluster_id not in clusters:
                clusters[cluster_id] = set()
            clusters[cluster_id].add((title, url, image, content))

    # 7. 리스트 변환 후 내림차순 sorting
    clusters = {k: list(v) for k, v in clusters.items() if len(v) > 1}
    sorted_clusters = sorted(clusters.items(), key=lambda item: len(item[1]), reverse=True)

    # 8. cluster_id 내림차순으로 재정의
    redefined_clusters = {}
    for new_id, (old_id, titles_urls_images_contents) in enumerate(sorted_clusters, start=1):
        redefined_clusters[new_id] = titles_urls_images_contents
        
    # 9. Top_Today_NewsDB category 컬렉션에 데이터 다 지우기
    top_today_news_db = client['Top_Today_News']
    category_collection = top_today_news_db[collection_name]
    category_collection.delete_many({})

    # 10. Top_Today_NewsDB category 컬렉션에 데이터 저장
    for cluster_id, titles_urls_images_contents in redefined_clusters.items():
        formatted_content = [{
                'title': item[0],
                'url': item[1],
                'image': item[2],
                'content': item[3]
            }
            for item in titles_urls_images_contents
        ]

        category_collection.insert_one({
            'cluster_id': cluster_id,
            'news_content': formatted_content,
            'date': date_str
        })
        
    return redefined_clusters