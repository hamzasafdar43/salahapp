
from flask import Blueprint, request, jsonify
from db import db
from models.story import Story, StoryContent, StoryQuiz, QuizQuestion, QuestionOption , StoryQuizAttempt
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

@story_bp.route("/<story_code>/quiz", methods=["POST"])
def save_quiz(story_code):
    data = request.get_json()
    questions = data.get("quiz", [])

    if not questions:
        return jsonify({"message": "Questions are required"}), 400

    # Lookup story by story_code to get story_id (integer)
    story = Story.query.filter_by(story_code=story_code).first()
    if not story:
        return jsonify({"message": "Story not found"}), 404

    quiz_code = generate_code("QUIZ")
    quiz = StoryQuiz(
        quiz_code=quiz_code,
        story_id=story.id_story  # Use the integer id here
    )
    db.session.add(quiz)

    for q in questions:
        if not q.get("content") or not q.get("correct_option"):
            return jsonify({"message": "Each question must have 'content' and 'correct_option'"}), 400

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
        db.session.flush()

        for opt_text in option_texts:
            option_code = generate_code("OPT")
            option = QuestionOption(
                option_code=option_code,
                content=opt_text,
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


@story_bp.route("/quizzes", methods=["GET"])
def get_all_quizzes():
    quizzes = StoryQuiz.query.all()
    response = []

    for quiz in quizzes:
        story = Story.query.get(quiz.story_id)

        questions_data = []
        for question in quiz.questions:
            options = [option.content for option in question.options]
            
            question_data = {
                "question_code": question.question_code,
                "content": question.content,
                "options": options,
                "correct_answer": question.correct_option_content  # <-- fixed line
            }

            questions_data.append(question_data)

        response.append({
            "story_code": story.story_code,
            "questions": questions_data
        })

    return jsonify(response), 200


@story_bp.route("/quiz-attempts", methods=["POST"])
def create_quiz_attempt():
    try:
        data = request.get_json()

        # Generate a unique attempt_code
        attempt_code = "ATTEMPT-" + uuid.uuid4().hex[:6].upper()

        new_attempt = StoryQuizAttempt(
            attempt_code=attempt_code,
            id_question=data['id_question'],
            id_option_selected=data['id_option_selected'],
            id_student=data['id_student'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(new_attempt)
        db.session.commit()

        return jsonify({
            "message": "Quiz attempt created successfully",
            "attempt_code": attempt_code
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@story_bp.route("/all-quiz-attempts", methods=["GET"])
def get_quiz_attempt():
    try:
        attempts = StoryQuizAttempt.query.all()
        result = []
        for attempt in attempts:
            result.append({
                "id_quiz_attempt": attempt.id_quiz_attempt,
                "attempt_code": attempt.attempt_code,
                "question_content": attempt.question.content if attempt.question else None,
                "option_content": attempt.selected_option.content if attempt.selected_option else None,
                "student_name": attempt.student.name if attempt.student else None,
                "created_at": attempt.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({"quiz_attempts": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
