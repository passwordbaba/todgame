from app import app, db, Question

questions = [
    {"question": "What is your biggest fear?", "category": "truth"},
    {"question": "Sing a song loudly.", "category": "dare"},
    {"question": "What is your most embarrassing moment?", "category": "truth"},
    {"question": "Do 20 pushups.", "category": "dare"},
    # Add more questions here
]

with app.app_context():
    for q in questions:
        new_question = Question(question=q['question'], category=q['category'])
        db.session.add(new_question)
    db.session.commit()
    print("Database populated with questions!")
