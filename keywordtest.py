from konlpy.tag import Hannanum
from sklearn.feature_extraction.text import TfidfVectorizer

# 한글 불용어 목록
korean_stopwords = set([
    '의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '를', '으로', '자', '에', '와', '한', '하다'
])

def extract_korean_keywords(text, num_keywords=10):
    hannanum = Hannanum()
    
    # 형태소 분석 및 명사 추출
    tokens = hannanum.nouns(text)
    
    # 불용어 제거
    filtered_tokens = [word for word in tokens if word not in korean_stopwords and len(word) > 1]
    
    # 단어 빈도수 계산 및 TF-IDF 계산
    vectorizer = TfidfVectorizer(max_df=0.85, stop_words=korean_stopwords)
    tfidf_matrix = vectorizer.fit_transform([' '.join(filtered_tokens)])
    
    # 단어와 TF-IDF 점수 매핑
    tfidf_scores = zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0])
    
    # TF-IDF 점수가 높은 상위 num_keywords개 단어 추출
    sorted_keywords = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)[:num_keywords]
    
    return [keyword for keyword, score in sorted_keywords]

# 테스트 본문
text = """
애플의 새로운 아이폰 12는 최고의 아이폰입니다. 5G 연결, 개선된 카메라, 강력한 A14 바이오닉 칩을 탑재하여 
전작에 비해 상당한 업그레이드를 제공하지만, 높은 가격은 일부 고객에게 부담이 될 수 있습니다.
"""

keywords = extract_korean_keywords(text)
print(keywords)
