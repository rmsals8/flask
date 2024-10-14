# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    
    # 관리자 계정 생성
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('your_secure_password')
        db.session.add(admin)
        db.session.commit()
        print("관리자 계정이 생성되었습니다.")
    else:
        print("관리자 계정이 이미 존재합니다.")

print("데이터베이스 초기화가 완료되었습니다.")