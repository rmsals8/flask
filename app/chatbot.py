from sentence_transformers import SentenceTransformer, util
import torch
from app.models import FAQ, db
import random

# BERT 모델 로드
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

def get_chatbot_response(query):
    try:
        faqs = FAQ.query.all()
        if not faqs:
            return "죄송합니다. 아직 등록된 FAQ가 없습니다."

        # 쿼리 임베딩
        query_embedding = model.encode(query, convert_to_tensor=True)

        # FAQ 임베딩
        faq_embeddings = model.encode([faq.question for faq in faqs], convert_to_tensor=True)

        # 코사인 유사도 계산
        cos_scores = util.pytorch_cos_sim(query_embedding, faq_embeddings)[0]
        best_match_idx = torch.argmax(cos_scores)
        best_match = faqs[best_match_idx]
        
        similarity_score = cos_scores[best_match_idx].item()

        if similarity_score > 0.5:  # 유사도 임계값 낮춤
            answer = best_match.answer
            return generate_response(answer, best_match.category)
        else:
            return "죄송합니다. 질문을 이해하지 못했습니다. 다른 방식으로 질문해 주시겠어요?"

    except Exception as e:
        print(f"챗봇 응답 생성 중 오류 발생: {str(e)}")
        return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."

def generate_response(answer, category):
    templates = {
        "개인정보": [
            "제 {answer}",
            "{answer}입니다.",
            "저는 {answer}라고 합니다.",
            "{answer}라고 해요."
        ],
        "요리": [
            "요리 팁을 알려드릴게요. {answer}",
            "맛있는 음식을 만드는 방법은 이렇습니다: {answer}",
            "쉽게 따라할 수 있는 레시피예요. {answer}",
            "요리의 핵심은 이거예요. {answer}"
        ],
        "뉴스": [
            "오늘의 주요 소식입니다. {answer}",
            "최신 뉴스를 알려드릴게요. {answer}",
            "방금 들어온 소식이에요. {answer}",
            "중요한 뉴스를 공유합니다. {answer}"
        ]
    }
    
    default_templates = [
        "알려드리자면, {answer}",
        "제가 알기로는 {answer}",
        "이렇게 설명할 수 있어요. {answer}",
        "간단히 말씀드리면, {answer}"
    ]
    
    template = random.choice(templates.get(category, default_templates))
    return template.format(answer=answer)

def update_chatbot_knowledge(question, answer, category):
    new_faq = FAQ(question=question, answer=answer, category=category)
    db.session.add(new_faq)
    db.session.commit()

# 초기 FAQ 데이터 설정
def initialize_faq():
    faqs = [
        FAQ(question="이름이 뭐니", answer="김철수", category="개인정보"),
        FAQ(question="너의 이름은", answer="김철수", category="개인정보"),
        FAQ(question="이름이 무엇인가요", answer="김철수", category="개인정보"),
        # 더 많은 FAQ 추가...
    ]
    
    db.session.bulk_save_objects(faqs)
    db.session.commit()