import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import pairwise_distances

# 예제 제목 리스트
titles = [
    """'목회자 영적 재충전' 한신교회 제17회 신학심포지엄 개최""",
    """국립고궁박물관 수장고 언론 첫 공개""",
    "국립고궁박물관 지하에 위치한 수장고",
    "언론에 공개되는 고궁박물관 수장고",
    "목회자 영적 재충전' 한신교회 제17회 신학심포지엄 개최",
    "국립고궁박물관 수장고 언론 첫 공개",
    "조선시대 유물이 가득한 수장고",
    "두꺼운 문 지나 8중 잠금 해제…조선 왕실의 '보물 창고' 열리다",
    """독립운동하는 마음으로 준비"…뮤지컬 '영웅' 15주년 공연""",
    "북한 비핵화 논의"
]

# TF-IDF 벡터라이저를 사용하여 제목을 벡터로 변환
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(titles)
print(X)

# 코사인 거리를 거리 행렬로 변환
distance_matrix = pairwise_distances(X, metric='cosine')
print(distance_matrix)

# DBSCAN 클러스터링 모델 설정
dbscan = DBSCAN(eps=0.9, min_samples=2, metric='precomputed')

# DBSCAN을 사용하여 클러스터링 수행
dbscan.fit(distance_matrix)

# 각 제목에 대한 클러스터 할당 결과 출력
for i, title in enumerate(titles):
    print(f"Title: {title} => Cluster: {dbscan.labels_[i]}")
