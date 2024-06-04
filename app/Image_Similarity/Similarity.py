import os
import torch
import skimage
import open_clip
import numpy as np
from PIL import Image
from open_clip import tokenizer
import matplotlib.pyplot as plt

def Similarity_Image_and_Text():

    images = []
    original_images = []

    open_clip.list_pretrained()
    model, _, preprocess = open_clip.create_model_and_transforms('convnext_base_w', pretrained='laion2b_s13b_b82k_augreg')

    for filename in [filename for filename in os.listdir(skimage.data_dir) if filename.endswith(".png") or filename.endswith(".jpg")]:
        image = Image.open(os.path.join(skimage.data_dir, filename)).convert("RGB")
        original_images.append(image)
        images.append(preprocess(image))

    # 이미지 텐서화
    image_input = torch.tensor(np.stack(images))

    # 텍스트 토큰화
    text_tokens = tokenizer.tokenize(["a rocket standing on a launchpad"])

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
    most_similar_image = original_images[most_similar_idx]
    plt.imshow(most_similar_image)
    plt.title(f"Most similar image, index: {most_similar_idx}")
    plt.show()

    return most_similar_image