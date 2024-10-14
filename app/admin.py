from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user
from app import db
from app.models import User, FAQ

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@login_required
def index():
    faqs = FAQ.query.all()
    return render_template('admin.html', faqs=faqs)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('admin.index'))
        flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@bp.route('/add_faq', methods=['POST'])
@login_required
def add_faq():
    new_faq = FAQ(
        question=request.form['question'],
        answer=request.form['answer'],
        category=request.form['category']
    )
    db.session.add(new_faq)
    db.session.commit()
    flash('FAQ가 성공적으로 추가되었습니다.')
    return redirect(url_for('admin.index'))

@bp.route('/edit_faq/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_faq(id):
    faq = FAQ.query.get_or_404(id)
    if request.method == 'POST':
        faq.question = request.form['question']
        faq.answer = request.form['answer']
        faq.category = request.form['category']
        db.session.commit()
        flash('FAQ가 성공적으로 수정되었습니다.')
        return redirect(url_for('admin.index'))
    return render_template('edit_faq.html', faq=faq)

@bp.route('/delete_faq/<int:id>', methods=['POST'])
@login_required
def delete_faq(id):
    faq = FAQ.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ가 성공적으로 삭제되었습니다.')
    return redirect(url_for('admin.index'))