from flask import Blueprint, request, jsonify
from db import db
from models.story import Story, StoryContent, StoryQuiz , QuizQuestion , QuestionOption
from datetime import datetime

story_bp = Blueprint("story", __name__)


@story_bp.route("/add-stories", methods=["POST"])
def save_story():
    data = request.get_json()

    # Generate story_code automatically
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = 1 if not last_story else last_story.id_story + 1
    story_code = f"story{str(next_id).zfill(4)}"

    story = Story(
        story_code=story_code, title=data["title"], sub_title=data.get("sub_title")
    )

    db.session.add(story)
    db.session.commit()

    return (
        jsonify({"message": "Story saved successfully", "story_code": story_code}),
        201,
    )


@story_bp.route("/add-story-content", methods=["POST"])
def save_story_content():
    data = request.get_json()
    story_code = data.get("story_code")
    page_content = data.get("page_content")

    story = Story.query.filter_by(story_code=story_code).first()
    if not story:
        return jsonify({"error": "Story not found"}), 404

    last_content = StoryContent.query.order_by(
        StoryContent.id_story_content.desc()
    ).first()
    next_id = 1 if not last_content else last_content.id_story_content + 1
    content_code = f"content{str(next_id).zfill(4)}"

    story_content = StoryContent(
        content_code=content_code, page_content=page_content, story_code=story_code
    )

    db.session.add(story_content)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Story content saved successfully",
                "content_code": content_code,
            }
        ),
        201,
    )


@story_bp.route("/add-story-quiz", methods=["POST"])
def save_story_quiz():
    data = request.get_json()
    content_code = data.get("content_code")

    story_content = StoryContent.query.filter_by(content_code=content_code).first()
    if not story_content:
        return jsonify({"error": "StoryContent not found"}), 404

    last_quiz = StoryQuiz.query.order_by(StoryQuiz.id_story_quiz.desc()).first()
    next_id = 1 if not last_quiz else last_quiz.id_story_quiz + 1
    quiz_code = f"quiz{str(next_id).zfill(4)}"

    new_quiz = StoryQuiz(quiz_code=quiz_code, story_content_code=content_code)

    db.session.add(new_quiz)
    db.session.commit()

    return jsonify({"message": "Quiz saved successfully", "quiz_code": quiz_code}), 201


@story_bp.route("/add-quiz_question", methods=["POST"])
def add_question():
    data = request.get_json()
    quiz_code = data.get("quiz_code")
    content = data.get("content")

    if not quiz_code or not content:
        return jsonify({"error": "quiz_code and content are required"}), 400

    last_question = QuizQuestion.query.order_by(QuizQuestion.id_question.desc()).first()
    next_id = 1 if not last_question else last_question.id_question + 1
    question_code = f"q{str(next_id).zfill(4)}"

    question = QuizQuestion(
        question_code=question_code,
        content=content,
        quiz_code=quiz_code
    )
    db.session.add(question)
    db.session.commit()

    return jsonify({
        "message": "Quiz question saved successfully",
        "question_code": question_code
    }), 201


@story_bp.route("/add-question_option", methods=["POST"])
def add_options_and_correct_answer():
    data = request.get_json()
    question_code = data.get("question_code")
    options = data.get("content")  # list of strings
    correct_answer = data.get("correct_option")  # key fixed to match your request

    if not question_code or not options or not correct_answer:
        return jsonify({
            "error": "question_code, content (options), and correct_option are required"
        }), 400

    if not isinstance(options, list):
        return jsonify({"error": "content must be a list"}), 400

    question = QuizQuestion.query.filter_by(question_code=question_code).first()
    if not question:
        return jsonify({"error": "Question not found"}), 404

    correct_option_code = None
    option_code_list = []

    for option_text in options:
        last_option = QuestionOption.query.order_by(QuestionOption.id_option.desc()).first()
        next_id = 1 if not last_option else last_option.id_option + 1
        option_code = f"opt{str(next_id).zfill(4)}"

        option = QuestionOption(
            option_code=option_code,
            content=option_text,
            question_code=question_code
        )
        db.session.add(option)
        db.session.flush()

        option_code_list.append(option_code)

        if option_text == correct_answer:
            correct_option_code = option_code

    if not correct_option_code:
        return jsonify({"error": "Correct answer not found in options"}), 400

    question.correct_option_code = correct_option_code
    db.session.commit()

    return jsonify({
        "message": "Options added and correct answer set successfully",
        "options": options,
        "correct_answer": correct_answer,
        "question_code": question_code,
        "option_code": correct_option_code
    }), 201
