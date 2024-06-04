from fastapi import APIRouter
from app.news.newsapi import fetch_news
from app.GPT.gpt import GptapiResult
from app.Image_Similarity.Similarity import Similarity_Image_and_Text
from app.Crawling.crawling import Crawling


router = APIRouter()

@router.get("/news")
def read_news():
    # 뉴스 TOP 10 기사 데이터 요청 및 각 신문사별로 10개의 데이터 요청
    # news_data = fetch_news() # 각 신문 기사별 publishedAt, urlToImage, url author title description name 데이터들이 들어있음
    # print(news_data)

    # # TODO 각 신문사별 URL를 전달받아 뉴스 본문 긁어오기
    # url_list = [item["url"] for item in news_data]
    # description_list = [item["description"] for item in news_data]
    # print(url_list)
    ##new_full_content = Crawling(url_list) # 각 신문사별 본문내용 10개 리스트 각 신문사의 제목을 통해 각 10개의 기사 제공

    # TODO GPT 이용하여 각 본문 내용 요약 및 전체 본문 내용 뽑아내기
    wise_new_full_content = GptapiResult(new_full_content)

    # # TODO 본문내용에 의해 이미지 텍스트 유사도 검증으로 썸네일 이미지
    #urltoimage = [item["urltoimage"] for item in news_data] # 기사 10개의 썸네일 이미지
    #Thumbnail_image = Similarity_Image_and_Text(wise_new_full_content,urltoimage) # 기사 본문과 제일 유사한 이미지 뽑아내기

    # TODO 정보 파싱후 DB 저장 (newsid, category, name, source(author, title, description, url, urltoimage, publishedAt), url_main, urlToImage, content)


    return news_data

