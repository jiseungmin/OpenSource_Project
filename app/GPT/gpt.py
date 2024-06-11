import os
import openai

# API 키 설정
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI API 클라이언트 초기화
openai.api_key = api_key

def summarize_article(article):
    # 단일 기사를 요약하는 함수
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 뉴스 기사를 요약해주는 어시스턴트입니다."},
            {"role": "user", "content": f"다음 기사를 요약해줘: {article}"}
        ]
    )
    summary = response.choices[0].message["content"]
    print("summary: ", summary)
    return summary

def combine_summaries(summaries, max_tokens):
    combined_summary = ""
    for summary in summaries:
        if len(combined_summary) + len(summary) <= max_tokens:
            combined_summary += summary + " "
        else:
            break
    return combined_summary.strip()

def GptapiResult(articles):
    # 개별 기사들을 요약한 후 결합
    summaries = [summarize_article(article) for article in articles]
    combined_summary = " ".join(summaries)
    
    # 그룹 요약을 최종 통합, 최대 토큰 수 제한
    combined_summary = combine_summaries(summaries, max_tokens=4096)
    print("combined_summary: ", combined_summary)
    
    # 결합된 요약 내용을 최종 요약
    final_summary_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 뉴스 기사의 요약된 내용을 통합해주는 어시스턴트입니다."},
            {"role": "user", "content": f"다음 요약된 기사들을 장소, 시간, 내용, 인물들을 포함한 통합 본문내용으로 더 자세하고 길게 정리해서 써줘 \n 출력 형식: 장소: [장소] \n 내용: [내용]: {combined_summary}"}
        ]
    )
    
    final_summary = final_summary_response.choices[0].message["content"]
    return final_summary