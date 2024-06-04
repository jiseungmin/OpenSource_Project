import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 예제 제목 리스트
titles = [
    "북한의 정찰위성 발사",
    "한미일 외교차관 협의회 개최",
    "북한 미사일 도발",
    "미중 외교 회담",
    "한미일 군사 협력",
    "북러 군사 협력 강화",
    "북한 핵 문제 논의",
    "중국의 대북 영향력",
    "한미일 정상 회담 결과",
    "북한 비핵화 논의"
]

# TF-IDF 벡터라이저를 사용하여 제목을 벡터로 변환
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(titles)

# K-평균 클러스터링을 사용하여 제목 분류
num_clusters = 5  # 원하는 클러스터 수 설정
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(X)

# 각 제목에 대한 클러스터 할당 결과 출력
for i, title in enumerate(titles):
    print(f"Title: {title} => Cluster: {kmeans.labels_[i]}")
