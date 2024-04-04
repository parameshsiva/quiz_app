from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
db = SQLAlchemy(app)


class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    options = db.relationship('QuizOption', backref='question', lazy=True)


class QuizOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        question_text = request.form['question-text']
        category = request.form['category']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = int(request.form['correct-answer'])

        if 'question_id' in request.form:  # If editing an existing question
            question_id = int(request.form['question_id'])
            question = QuizQuestion.query.get_or_404(question_id)
            question.question_text = question_text
            question.category = category
            db.session.commit()

            options = QuizOption.query.filter_by(question_id=question_id).all()
            options[0].option_text = option1
            options[0].is_correct = correct_answer == 1
            options[1].option_text = option2
            options[1].is_correct = correct_answer == 2
            options[2].option_text = option3
            options[2].is_correct = correct_answer == 3
            options[3].option_text = option4
            options[3].is_correct = correct_answer == 4
            db.session.commit()
            
            return redirect(url_for('admin'))

        else:  
            question = QuizQuestion(question_text=question_text, category=category)
            db.session.add(question)
            db.session.commit()

            options = [
                QuizOption(question_id=question.id, option_text=option1, is_correct=correct_answer == 1),
                QuizOption(question_id=question.id, option_text=option2, is_correct=correct_answer == 2),
                QuizOption(question_id=question.id, option_text=option3, is_correct=correct_answer == 3),
                QuizOption(question_id=question.id, option_text=option4, is_correct=correct_answer == 4)
            ]
            db.session.add_all(options)
            db.session.commit()

            return redirect(url_for('admin'))

    elif request.method == 'GET' and 'edit_id' in request.args:
        edit_id = int(request.args['edit_id'])
        question = QuizQuestion.query.get_or_404(edit_id)
        options = QuizOption.query.filter_by(question_id=edit_id).all()
        return render_template('admin.html', edit_question=question, edit_options=options)

    else:  
        return render_template('admin.html')


@app.route('/quiz')
def quiz():
    questions = QuizQuestion.query.all()
    
    formatted_questions = []
    for question in questions:
        formatted_question = {
            'id': question.id,
            'question_text': question.question_text,
            'options': [{
                'id': option.id,
                'option_text': option.option_text,
                'is_correct': option.is_correct
            } for option in question.options]
        }
        formatted_questions.append(formatted_question)

    return render_template('quiz.html', questions=formatted_questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
