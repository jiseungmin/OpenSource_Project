import os
import torch
import requests
import skimage
import open_clip
import numpy as np
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from open_clip import tokenizer

def Similarity_Image_and_Text(wise_new_full_content, image_urls):
    images = []
    original_images = []
    valid_image_urls = []

    # Pre-trained model 불러오기
    open_clip.list_pretrained()
    model, _, preprocess = open_clip.create_model_and_transforms('convnext_base_w', pretrained='laion2b_s13b_b82k_augreg')

    # 이미지 URL로부터 이미지 다운로드 및 전처리
    for url in image_urls:
        if url.lower() == "이미지 없음":
            continue
        try:
            response = requests.get(url)
            image = Image.open(BytesIO(response.content)).convert("RGB")
            original_images.append(image)
            images.append(preprocess(image))
            valid_image_urls.append(url)
        except Exception as e:
            print(f"Failed to process image from URL {url}: {e}")
            continue

    if not images:
        print("No valid images found.")
        return None

    # 이미지 텐서화
    image_input = torch.tensor(np.stack(images))

    # 텍스트 토큰화
    text_tokens = tokenizer.tokenize([wise_new_full_content])

    with torch.no_grad():
        # 모델 인코딩
        image_features = model.encode_image(image_input).float()
        text_features = model.encode_text(text_tokens).float()

    # 특성 벡터 정규화
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # 코사인 유사도 계산
    similarity = (text_features.cpu().numpy() @ image_features.cpu().numpy().T)

    # 가장 유사한 이미지 찾기
    most_similar_idx = similarity.argmax()
    most_similar_image_url = valid_image_urls[most_similar_idx]

    return most_similar_image_url
