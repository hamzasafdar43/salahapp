
from flask import Blueprint, request, jsonify
from db import db
from models.story import Story, StoryContent, StoryQuiz, QuizQuestion, QuestionOption
from datetime import datetime
import uuid

story_bp = Blueprint("story_bp", __name__, url_prefix="/api/stories")

def generate_story_code():
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = (last_story.id_story + 1) if last_story else 1
    return f"STR{str(next_id).zfill(3)}"

def generate_content_code():
    return f"CONTENT-{uuid.uuid4().hex[:8]}"

@story_bp.route("/bulk", methods=["POST"])
def save_stories_bulk():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"message": "Invalid request format, expected a list"}), 400

    saved_story_codes = []

    for item in data:
        story_code = generate_story_code()
        story = Story(
            story_code=story_code,
            title=item.get("title"),
            sub_title=item.get("sub_title")
        )
        db.session.add(story)
        saved_story_codes.append(story_code)

        for page in item.get("pages_content", []):
            content = StoryContent(
                content_code=generate_content_code(),
                page_content=page,
                story_code=story_code
            )
            db.session.add(content)

    db.session.commit()

    return jsonify({
        "message": "Stories saved successfully",
        "saved_stories": saved_story_codes
    }), 201

@story_bp.route("/specific-story", methods=["POST"])
def save_story():
    data = request.get_json()
    story_code = generate_story_code()

    story = Story(
        story_code=story_code,
        title=data["title"],
        sub_title=data["sub_title"]
    )
    db.session.add(story)

    pages = data.get("pages_content", [])
    for page in pages:
        content = StoryContent(
            content_code=generate_content_code(),
            page_content=page,
            story_code=story_code
        )
        db.session.add(content)

    db.session.commit()

    return jsonify({
        "message": "Story saved successfully",
        "story_code": story_code
    }), 201

def generate_code(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

@story_bp.route("/<story_code>/quiz", methods=["POST"])
def save_quiz(story_code):
    data = request.get_json()
    questions = data.get("questions", [])

    if not questions:
        return jsonify({"message": "Questions are required"}), 400

    quiz_code = generate_code("QUIZ")
    quiz = StoryQuiz(
        quiz_code=quiz_code,
        story_code=story_code
    )
    db.session.add(quiz)

    for q in questions:
        question_code = generate_code("Q")
        option_texts = q.get("options", [])
        correct_ans = q["correct_option"]

        question = QuizQuestion(
            question_code=question_code,
            content=q["content"],
            coins=q.get("coins", 1),
            quiz_code=quiz_code,
            correct_option_content=correct_ans
        )
        db.session.add(question)

        for opt_text in option_texts:
            option_code = generate_code("OPT")
            option = QuestionOption(
                option_code=option_code,
                content=opt_text,
                question_code=question_code
            )
            db.session.add(option)

    db.session.commit()

    return jsonify({
        "message": "Quiz saved successfully",
        "quiz_code": quiz_code
    }), 201

@story_bp.route("/stories", methods=["GET"])
def get_all_stories():
    stories = Story.query.all()
    response = []

    for story in stories:
        pages = []
        for content in story.contents:
            if isinstance(content.page_content, list):
                pages.extend(content.page_content)
            else:
                pages.append(content.page_content)

        story_data = {
            "story_code": story.story_code,
            "title": story.title,
            "sub_title": story.sub_title,
            "pages_content": pages
        }
        response.append(story_data)

    return jsonify(response), 200

@story_bp.route("/quizzes", methods=["GET"])
def get_all_quizzes():
    quizzes = StoryQuiz.query.all()
    story_map = {}

    for quiz in quizzes:
        story_code = quiz.story_code
        questions = QuizQuestion.query.filter_by(quiz_code=quiz.quiz_code).all()

        for question in questions:
            options = QuestionOption.query.filter_by(question_code=question.question_code).all()
            option_texts = [opt.content for opt in options]

            question_data = {
                "question_code": question.question_code,
                "content": question.content,
                "options": option_texts,
                "correct_answer": question.correct_option_content
            }

            if story_code not in story_map:
                story_map[story_code] = {
                    "story_code": story_code,
                    "questions": []
                }

            story_map[story_code]["questions"].append(question_data)

    response = list(story_map.values())
    return jsonify(response), 200

