
from flask import Blueprint, request, jsonify
from db import db
from models.story import Story, StoryContent, StoryQuiz, QuizQuestion, QuestionOption , StoryQuizAttempt 
from models.user import Student
from datetime import datetime
import uuid

story_bp = Blueprint("story_bp", __name__, url_prefix="/api/stories")

def generate_story_code():
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = (last_story.id_story + 1) if last_story else 1
    return f"STR{str(next_id).zfill(3)}"

def generate_question_code():
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = (last_story.id_story + 1) if last_story else 1
    return f"Q{str(next_id).zfill(3)}"

def generate_correct_option_code():
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = (last_story.id_story + 1) if last_story else 1
    return f"COPT{str(next_id).zfill(3)}"


def generate_options_code():
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = (last_story.id_story + 1) if last_story else 1
    return f"OPT{str(next_id).zfill(3)}"



def generate_content_code():
    return f"CONTENT-{uuid.uuid4().hex[:8]}"

@story_bp.route("/bulk", methods=["POST"])
def save_stories_bulk():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"message": "Invalid request format, expected a list of stories"}), 400

    saved_story_codes = []

    try:
        for item in data:
            story_code = generate_story_code()

            # Create story
            story = Story(
                story_code=story_code,
                title=item.get("title"),
                sub_title=item.get("sub_title")
            )
            db.session.add(story)
            db.session.commit()  # Commit early to get `story.id_story`

            saved_story_codes.append(story_code)

            # Add content pages
            for page in item.get("pages_content", []):
                content = StoryContent(
                    content_code=generate_content_code(),
                    page_content=page,
                    story_id=story.id_story
                )
                db.session.add(content)

        db.session.commit()

        return jsonify({
            "message": "Stories and content saved successfully.",
            "saved_stories": saved_story_codes
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "An error occurred while saving stories.",
            "error": str(e)
        }), 500


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


def generate_code(prefix):
    return prefix + uuid.uuid4().hex[:6].upper()

@story_bp.route("/<story_code>/quiz", methods=["POST"])
def save_quiz(story_code):
    data = request.get_json()
    questions = data.get("questions", [])

    if not questions:
        return jsonify({"message": "Questions are required"}), 400

    story = Story.query.filter_by(story_code=story_code).first()
    if not story:
        return jsonify({"message": "Story not found"}), 404

    quiz_code = generate_code("QUIZ")
    quiz = StoryQuiz(
        quiz_code=quiz_code,
        story_id=story.id_story
    )
    db.session.add(quiz)

    for q in questions:
        question_code = generate_code("Q")
        content = q.get("content")
        coins = q.get("coins", 1)
        correct_option_content = q.get("correct_option")
        options = q.get("options", [])

        if not content or not correct_option_content or not options:
            return jsonify({
                "message": "Each question must include 'content', 'correct_option', and 'options'"
            }), 400

        question = QuizQuestion(
            question_code=question_code,
            content=content,
            coins=coins,
            quiz_code=quiz_code,
            correct_option_content=correct_option_content
        )
        db.session.add(question)
        db.session.flush()  # Required to get question.id_question

        for opt_content in options:
            option_code = generate_code("OPT")
            option = QuestionOption(
                option_code=option_code,
                content=opt_content,
                id_question=question.id_question
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


@story_bp.route("/<string:story_code>/quiz", methods=["GET"])
def get_quiz_by_story_code(story_code):
    story = Story.query.filter_by(story_code=story_code).first()

    if not story:
        return jsonify({"error": "Story not found"}), 404

    quiz = StoryQuiz.query.filter_by(story_id=story.id_story).first()

    if not quiz:
        return jsonify({"error": "Quiz not found for this story"}), 404

    questions_data = []
    for question in quiz.questions:
        options = []
        for option in question.options:
            options.append({
                "option_code": option.option_code,
                "content": option.content
            })

        question_data = {
            "question_code": question.question_code,
            "content": question.content,
            "coins": question.coins,
            "correct_option_code": question.correct_option_content,
            "options": options
        }

        questions_data.append(question_data)

    return jsonify({
        "quiz_code": quiz.quiz_code,
        "questions": questions_data
    }), 200




@story_bp.route("/quiz-attempt/<string:story_code>/<string:quiz_code>/<string:student_code>", methods=["POST"])
def create_quiz_attempts(story_code, quiz_code, student_code):
    try:
        data = request.get_json()

        if not isinstance(data, list) or not data:
            return jsonify({"message": "Request body must be a non-empty list of attempts"}), 400

        # Lookup student by student_code (you must have this model and relation)
        student = Student.query.filter_by(student_code=student_code).first()
        if not student:
            return jsonify({"message": "Student not found"}), 404

        saved_attempts = []

        for attempt in data:
            question_code = attempt.get("question_code")
            selected_option_code = attempt.get("selected_option_code")

            if not question_code or not selected_option_code:
                return jsonify({"message": "Each attempt must have 'question_code' and 'selected_option_code'"}), 400

            # Get question by question_code
            question = QuizQuestion.query.filter_by(question_code=question_code, quiz_code=quiz_code).first()
            if not question:
                return jsonify({"message": f"Question not found for code: {question_code}"}), 404

            # Get option by option_code and question_id
            option = QuestionOption.query.filter_by(option_code=selected_option_code, id_question=question.id_question).first()
            if not option:
                return jsonify({"message": f"Option not found for code: {selected_option_code}"}), 404

            attempt_code = "ATT" + uuid.uuid4().hex[:6].upper()

            new_attempt = StoryQuizAttempt(
                attempt_code=attempt_code,
                id_question=question.id_question,
                id_option_selected=option.id_option,
                id_student=student.id_student,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.session.add(new_attempt)
            saved_attempts.append(attempt_code)

        db.session.commit()

        return jsonify({
            "message": "Quiz attempts saved",
            "saved_attempts": saved_attempts
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@story_bp.route("/students/<student_code>/quiz-attempts", methods=["GET"])
def get_student_quiz_attempts(student_code):
    try:
        # Get student by code
        student = Student.query.filter_by(student_code=student_code).first()
        if not student:
            return jsonify({"message": "Student not found"}), 404

        # Get all attempts by student
        attempts = StoryQuizAttempt.query.filter_by(id_student=student.id_student).all()

        grouped = {}

        for attempt in attempts:
            question = attempt.question
            selected_option = attempt.selected_option

            if not question or not selected_option:
                continue

            quiz_code = question.quiz_code
            story = Story.query.filter_by(id_story=question.quiz.story_id).first() if question.quiz else None
            story_code = story.story_code if story else "UNKNOWN"

            is_correct = question.correct_option_content == selected_option.option_code
            coins_earned = question.coins if is_correct else 0

            key = (story_code, quiz_code)

            if key not in grouped:
                grouped[key] = []

            grouped[key].append({
                "attempt_code": attempt.attempt_code,
                "question_code": question.question_code,
                "question_content": question.content,
                "selected_option_code": selected_option.option_code,
                "selected_option_content": selected_option.content,
                "is_correct": is_correct,
                "coins_earned": coins_earned
            })

        result = []
        for (story_code, quiz_code), attempts_list in grouped.items():
            result.append({
                "story_code": story_code,
                "quiz_code": quiz_code,
                "attempts": attempts_list
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


