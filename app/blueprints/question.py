from flask import Blueprint, render_template,session
# from .preview import extract_text
from ..model.llama import exam_generate_questions
from langchain_community.llms import Ollama
from docx import Document

from .. import db
from ..schema import QuestionSet, Question


question = Blueprint('question', __name__)

@question.route('/question')
def question_page():

    questions = session.get('questions', [])
    text = session.get('text', '')
    filename = session.get('filename', 'No file selected')
    # Debugging output
    print(f"Filename: {filename}")
    print(f"Text: {text}")
    # For debugging purpose, making sure correct values are being passed
    for question in questions:
        question_type = question.get('type')
        num_questions = question.get('quantity')
        question_difficulty = question.get('difficulty')
        print(f"Preparing to generate {num_questions} {question_difficulty} {question_type} questions.")

    generated_questions = exam_generate_questions(questions, text)

    new_set = QuestionSet(title=filename)
    db.session.add(new_set)
    db.session.flush()

    for item in generated_questions:
        question_type = item["type"]
        for q in item["questions"]:
            new_question = Question(
                type=question_type,
                question_text=q["question"],
                options=q["options"],  
                answer=q["answer"],
                question_set_id=new_set.id
            )
            db.session.add(new_question)
    db.session.commit()

    return render_template('question.html', filename=filename, generated_questions=generated_questions)