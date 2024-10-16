import string
import random
from app.models import FAQ, db
from sentence_transformers import SentenceTransformer, util
import torch

# BERT 모델 로드
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

def preprocess_text(text):
    # 소문자 변환 및 구두점 제거
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def get_chatbot_response(query):
    try:
        faqs = FAQ.query.all()
        if not faqs:
            return "죄송합니다. 아직 등록된 FAQ가 없습니다."

        # 쿼리 전처리 및 임베딩
        processed_query = preprocess_text(query)
        query_embedding = model.encode(processed_query, convert_to_tensor=True)

        # FAQ 전처리 및 임베딩
        processed_faqs = [preprocess_text(faq.question) for faq in faqs]
        faq_embeddings = model.encode(processed_faqs, convert_to_tensor=True)

        # 코사인 유사도 계산
        cos_scores = util.pytorch_cos_sim(query_embedding, faq_embeddings)[0]
        best_match_idx = torch.argmax(cos_scores)
        best_match = faqs[best_match_idx]
        
        similarity_score = cos_scores[best_match_idx].item()

        if similarity_score > 0.3:  # 유사도 임계값
            answer = best_match.answer
            return generate_response(query, answer)
        else:
            return generate_creative_response(query)

    except Exception as e:
        print(f"챗봇 응답 생성 중 오류 발생: {str(e)}")
        return f"죄송합니다. 오류가 발생했습니다: {str(e)}"

def generate_response(query, answer):
    templates = [
        f"{answer}",
        f"답변드리자면, {answer}",
        f"제가 알기로는 {answer}",
        f"'{query}'에 대해 말씀드리면, {answer}",
        f"그 질문에 대한 답변은 {answer}입니다.",
        f"간단히 말씀드리면, {answer}",
        f"질문하신 내용에 대해 {answer}라고 답변드릴 수 있습니다."
    ]
    
    return random.choice(templates)

def generate_creative_response(query):
    templates = [
        f"'{query}'에 대해 정확한 정보를 드리기 어렵습니다. 더 자세히 설명해 주시겠어요?",
        f"흥미로운 질문이네요. '{query}'에 대해 더 알고 싶습니다. 구체적으로 어떤 점이 궁금하신가요?",
        f"죄송합니다. '{query}'에 대한 정보가 부족합니다. 다른 방식으로 질문해 주시면 도움이 될 것 같아요.",
        f"'{query}'에 대해 생각해 볼 만한 질문이네요. 제가 알고 있는 정보는 제한적이지만, 무엇을 알고 싶으신지 더 말씀해 주시겠어요?",
        f"흠, '{query}'라... 제가 잘 모르는 분야인 것 같습니다. 좀 더 쉽게 설명해 주실 수 있나요?"
    ]
    return random.choice(templates)

def update_chatbot_knowledge(question, answer):
    new_faq = FAQ(question=question, answer=answer)
    db.session.add(new_faq)
    db.session.commit()

# 초기 FAQ 데이터 설정
def initialize_faq():
    faqs = [
        FAQ(question="이름이 뭐니", answer="제 이름은 AI 어시스턴트입니다."),
        FAQ(question="너의 이름은", answer="저는 AI 어시스턴트라고 합니다."),
        FAQ(question="오늘의 날씨는 어때", answer="죄송합니다. 실시간 날씨 정보를 제공하지 못합니다. 날씨 앱이나 웹사이트를 확인해보시는 것이 좋을 것 같아요."),
        FAQ(question="인공지능이 뭐야", answer="인공지능은 인간의 학습능력, 추론능력, 지각능력을 인공적으로 구현한 컴퓨터 프로그램 또는 이를 포함한 컴퓨터 시스템을 말합니다."),
        FAQ(question="Python 언어의 특징은", answer="Python은 읽기 쉽고 간결한 문법, 동적 타이핑, 객체 지향성, 인터프리터 언어, 풍부한 라이브러리 등의 특징을 가지고 있습니다."),
    ]
    
    db.session.bulk_save_objects(faqs)
    db.session.commit()