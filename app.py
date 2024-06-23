from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///truth_or_dare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(80), unique=True, nullable=False)
    pin = db.Column(db.String(6), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    session_id = db.Column(db.String(80), db.ForeignKey('session.session_id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(80), db.ForeignKey('session.session_id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'truth' or 'dare'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    data = request.json
    session_id = data.get('session_id')
    pin = data.get('pin')
    username = data.get('username')
    if Session.query.filter_by(session_id=session_id).first():
        return jsonify({'message': 'Session already exists'}), 400
    new_session = Session(session_id=session_id, pin=pin)
    db.session.add(new_session)
    db.session.commit()
    new_user = User(username=username, session_id=session_id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Session started', 'session_id': session_id})

@app.route('/login_session', methods=['POST'])
def login_session():
    data = request.json
    session_id = data.get('session_id')
    pin = data.get('pin')
    username = data.get('username')
    session = Session.query.filter_by(session_id=session_id, pin=pin).first()
    if session:
        new_user = User(username=username, session_id=session_id)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Login successful', 'session_id': session_id})
    else:
        return jsonify({'message': 'Invalid session ID or pin'}), 401

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    session_id = data.get('session_id')
    session = Session.query.filter_by(session_id=session_id).first()
    if not session:
        return jsonify({'message': 'Session does not exist'}), 404
    user_count = User.query.filter_by(session_id=session_id).count()
    if user_count >= 5:
        return jsonify({'message': 'User limit reached'}), 403
    new_user = User(username=username, session_id=session_id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added', 'username': username})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    session_id = data.get('session_id')
    username = data.get('username')
    message_text = data.get('message')
    new_message = Message(session_id=session_id, username=username, message=message_text)
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': 'Message sent'})

@app.route('/get_question', methods=['POST'])
def get_question():
    data = request.json
    session_id = data.get('session_id')
    category = data.get('category')
    questions = Question.query.filter_by(category=category).all()
    if questions:
        question = random.choice(questions).question
        return jsonify({'question': question})
    else:
        return jsonify({'message': 'No questions available for this category'}), 404

@app.route('/get_messages', methods=['POST'])
def get_messages():
    data = request.json
    session_id = data.get('session_id')
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.asc()).all()
    message_list = [{'username': m.username, 'message': m.message, 'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for m in messages]
    return jsonify({'messages': message_list})

@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.json
    question_text = data.get('question')
    category = data.get('category')
    new_question = Question(question=question_text, category=category)
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
