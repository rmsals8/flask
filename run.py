from app import create_app, db
from app.models import User, FAQ

app = create_app()

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized.")

@app.cli.command("create-admin")
def create_admin():
    with app.app_context():
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        admin = User(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user {username} created successfully.")

if __name__ == '__main__':
    app.run(debug=True)