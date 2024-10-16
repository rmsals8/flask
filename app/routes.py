from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from flask_login import login_required, login_user, logout_user, current_user
from app import db
from app.models import User, FAQ
from app.chatbot import get_chatbot_response
from app.kakao_utils import verify_kakao_signature
from flask_cors import cross_origin
import logging
logging.basicConfig(level=logging.DEBUG)
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return redirect(url_for('main.login'))

@bp.route('/keyboard', methods=['GET'])
def keyboard():
    return jsonify({"type": "text"})

@bp.route('/message', methods=['POST'])
@cross_origin()
def message():
    logger.info(f"Received POST request")
    logger.debug(f"Headers: {request.headers}")
    logger.debug(f"Data: {request.get_data(as_text=True)}")

    if not verify_kakao_signature(request):
        logger.warning("Invalid Kakao signature")
        return jsonify({"error": "Invalid signature"}), 401

    try:
        data = request.get_json()
        logger.info(f"Parsed JSON data: {data}")
        
        utterance = data['userRequest']['utterance']
        logger.info(f"Extracted utterance: {utterance}")
        
        response_text = get_chatbot_response(utterance)
        logger.info(f"Generated response: {response_text}")
        
        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response_text
                        }
                    }
                ]
            }
        }
        logger.info(f"Sending response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
                        }
                    }
                ]
            }
        }), 500

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.admin'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('main.admin'))
        flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/admin')
@login_required
def admin():
    faqs = FAQ.query.all()
    return render_template('admin.html', faqs=faqs)
from app.chatbot import update_chatbot_knowledge

@bp.route('/admin/add_faq', methods=['POST'])
@login_required
def add_faq():
    new_faq = FAQ(
        question=request.form['question'],
        answer=request.form['answer'],
        category=request.form['category']
    )
    db.session.add(new_faq)
    db.session.commit()
    update_chatbot_knowledge(request.form['question'], request.form['answer'])
    flash('FAQ가 성공적으로 추가되었습니다.')
    return redirect(url_for('main.admin'))
@bp.route('/admin/edit_faq/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_faq(id):
    faq = FAQ.query.get_or_404(id)
    if request.method == 'POST':
        faq.question = request.form['question']
        faq.answer = request.form['answer']
        faq.category = request.form['category']
        db.session.commit()
        flash('FAQ가 성공적으로 수정되었습니다.')
        return redirect(url_for('main.admin'))
    return render_template('edit_faq.html', faq=faq)

@bp.route('/admin/delete_faq/<int:id>', methods=['POST'])
@login_required
def delete_faq(id):
    faq = FAQ.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ가 성공적으로 삭제되었습니다.')
    return redirect(url_for('main.admin'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

