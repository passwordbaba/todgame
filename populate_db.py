from app import db, Question

questions = [
    {"question": "What is your biggest fear?", "category": "truth"},
    {"question": "Sing a song loudly.", "category": "dare"},
    # Add more questions here
]

for q in questions:
    new_question = Question(question=q['question'], category=q['category'])
    db.session.add(new_question)

db.session.commit()
print("Database populated with questions!")