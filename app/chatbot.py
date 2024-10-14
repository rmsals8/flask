import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models import FAQ
from app import db
nlp = spacy.load("ko_core_news_sm")
vectorizer = TfidfVectorizer()

def preprocess(text):
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

def get_chatbot_response(query):
    try:
        faqs = FAQ.query.all()
        if not faqs:
            return "죄송합니다. 아직 등록된 FAQ가 없습니다."

        preprocessed_query = preprocess(query)
        questions = [faq.question for faq in faqs]
        preprocessed_questions = [preprocess(q) for q in questions]

        vectors = vectorizer.fit_transform([preprocessed_query] + preprocessed_questions)
        similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]

        best_match = max(zip(similarities, faqs), key=lambda x: x[0])

        if best_match[0] > 0.5:  # 유사도 임계값
            return best_match[1].answer
        else:
            # 키워드 기반 검색
            query_keywords = set(preprocessed_query.split())
            for faq in faqs:
                faq_keywords = set(preprocess(faq.question).split())
                if query_keywords.intersection(faq_keywords):
                    return f"제가 이해한 바로는: {faq.answer}"

            return "죄송합니다. 질문을 이해하지 못했습니다. 다른 방식으로 질문해 주시겠어요?"

    except Exception as e:
        print(f"챗봇 응답 생성 중 오류 발생: {str(e)}")
        return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."

def update_chatbot_knowledge(question, answer):
    # 새로운 FAQ를 추가하거나 기존 FAQ를 업데이트할 때 호출
    new_faq = FAQ(question=question, answer=answer)
    db.session.add(new_faq)
    db.session.commit()