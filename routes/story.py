
from flask import Blueprint, request, jsonify , current_app
from db import db
from models.story import Story, StoryContent, StoryQuiz, QuizQuestion, QuestionOption , StoryQuizAttempt , StoryReward , PurchasedReward
from models.user import Student
from datetime import datetime
import uuid
from heplers.generate_code import generate_reward_code , generate_story_code , generate_content_code , generate_code
from heplers.image_upload_code import save_uploaded_file


story_bp = Blueprint("story_bp", __name__, url_prefix="/api/stories")


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


@story_bp.route("/<string:story_code>/quizzes", methods=["GET"])
def get_all_quizzes_by_story_code(story_code):
    story = Story.query.filter_by(story_code=story_code).first()

    if not story:
        return jsonify({"error": "Story not found"}), 404

    quizzes = StoryQuiz.query.filter_by(story_id=story.id_story).all()

    if not quizzes:
        return jsonify({"error": "No quizzes found for this story"}), 404

    quizzes_data = []

    for quiz in quizzes:
        questions_data = []

        for question in quiz.questions:
            options = []
            correct_option_text = None
            correct_option_code = None

            for option in question.options:
                options.append({
                    "option_code": option.option_code,
                    "content": option.content
                })

                # Match by option code or content, depending on what's saved
                if (
                    option.option_code == question.correct_option_content or 
                    option.content == question.correct_option_content
                ):
                    correct_option_code = option.option_code
                    correct_option_text = option.content

            question_data = {
                "question_code": question.question_code,
                "content": question.content,
                "coins": question.coins,
                "correct_option_code": correct_option_code,
                "correct_option": correct_option_text,
                "options": options
            }

            questions_data.append(question_data)

        quiz_data = {
            "quiz_code": quiz.quiz_code,
            "questions": questions_data
        }

        quizzes_data.append(quiz_data)

    return jsonify(quizzes_data), 200


@story_bp.route("/quiz-attempt/<string:story_code>/<string:quiz_code>/<string:student_code>", methods=["POST"])
def create_quiz_attempts(story_code, quiz_code, student_code):
    try:
        data = request.get_json()

        if not isinstance(data, list) or not data:
            return jsonify({"message": "Request body must be a non-empty list of attempts"}), 400

        student = Student.query.filter_by(student_code=student_code).first()
        if not student:
            return jsonify({"message": "Student not found"}), 404

        saved_attempts = []

        for attempt in data:
            question_code = attempt.get("question_code")
            selected_option_code = attempt.get("selected_option_code")

            if not question_code or not selected_option_code:
                return jsonify({"message": "Each attempt must have 'question_code' and 'selected_option_code'"}), 400

            question = QuizQuestion.query.filter_by(question_code=question_code, quiz_code=quiz_code).first()
            if not question:
                return jsonify({"message": f"Question not found for code: {question_code}"}), 404

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
        student = Student.query.filter_by(student_code=student_code).first()
        if not student:
            return jsonify({"message": "Student not found"}), 404

        attempts = StoryQuizAttempt.query.filter_by(id_student=student.id_student).all()
        result = []
        grouped = {}

        for attempt in attempts:
            question = attempt.question
            selected_option = attempt.selected_option

            if not question or not selected_option:
                continue

            quiz_code = question.quiz_code
            story = Story.query.filter_by(id_story=question.quiz.story_id).first() if question.quiz else None
            story_code = story.story_code if story else "UNKNOWN"
            story_updated_at = story.updated_at.strftime('%Y-%m-%d %H:%M:%S') if story and story.updated_at else None

            # ✅ FIX: get correct_option_code from QuestionOption instances
            correct_option_code = None
            if hasattr(question, 'options') and question.options:
                for opt in question.options:
                    if opt.content == question.correct_option_content:
                        correct_option_code = opt.option_code
                        break

            is_correct = question.correct_option_content == selected_option.content
            coins_earned = question.coins if is_correct else 0

            key = (story_code, quiz_code, story_updated_at)

            attempt_data = {
                "attempt_code": attempt.attempt_code,
                "question_code": question.question_code,
                "question_content": question.content,
                "selected_option_code": selected_option.option_code,
                "selected_option_content": selected_option.content,
                "correct_option_code": correct_option_code,
                "correct_option_content": question.correct_option_content,
                "is_correct": is_correct,
                "coins_earned": coins_earned,
                "created_at": attempt.created_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.created_at else None,
                "updated_at": attempt.updated_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.updated_at else None
            }

            if key not in grouped:
                grouped[key] = [ [] ]
            placed = False
            for attempt_group in grouped[key]:
                question_codes = {a["question_code"] for a in attempt_group}
                if attempt_data["question_code"] not in question_codes:
                    attempt_group.append(attempt_data)
                    placed = True
                    break

            if not placed:
                grouped[key].append([attempt_data])

        for (story_code, quiz_code, story_updated_at), attempt_groups in grouped.items():
            for attempts_list in attempt_groups:
                result.append({
                    "story_code": story_code,
                    "quiz_code": quiz_code,
                    "story_updated_at": story_updated_at,
                    "attempts": attempts_list
                })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@story_bp.route("/reward/<string:story_code>", methods=["POST"])
def create_reward(story_code):
    story = Story.query.filter_by(story_code=story_code).first()
    if not story:
        return jsonify({"error": "Story not found"}), 404

    coins = request.form.get('coins')
    if coins is None:
        return jsonify({"error": "Coins field is required"}), 400

    image_file = request.files.get('image')
    if not image_file:
        return jsonify({"error": "Image file is required"}), 400

    try:
        image_path = save_uploaded_file(image_file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    reward_code = generate_reward_code()

    new_reward = StoryReward(
        reward_code=reward_code,
        id_story=story.id_story,
        coins_required=coins,
        reward_image=image_path,
        is_locked=True
    )
    db.session.add(new_reward)
    db.session.commit()

    return jsonify({
        "message": "Reward created",
        "reward_code": reward_code,
        "story_code": story_code,
        "coins": coins,
        "reward_image": image_path,
        "status": "isLocked"
    }), 201


@story_bp.route('/rewards', methods=['GET'])
def get_all_rewards():
    rewards = StoryReward.query.all()
    result = []
    for r in rewards:
        result.append({
            "reward_code": r.reward_code,
            "coins_required": r.coins_required,
            "is_locked": r.is_locked,
            "story_code": r.story.story_code,
            "title": r.story.title,
            "sub_title": r.story.sub_title,
            "reward_image":r.reward_image
        })
    return jsonify(result)


@story_bp.route('/buyreward/<string:reward_code>/<string:student_code>', methods=['POST'])
def buy_reward(reward_code, student_code):
    data = request.get_json()
    coins = data.get('coins')

    reward = StoryReward.query.filter_by(reward_code=reward_code).first()
    if not reward:
        return jsonify({"error": "Reward not found"}), 404

    if coins is None:
        return jsonify({"error": "Coins value is required"}), 400

    if coins < reward.coins_required:
        return jsonify({"message": "Your coins are less for buying this reward"}), 400

    
    purchased = PurchasedReward.query.filter_by(
        student_code=student_code, reward_code=reward_code
    ).first()
    if purchased:
        return jsonify({"message": "Reward already unlocked for this student"}), 200

    
    purchased = PurchasedReward(
        student_code=student_code,
        reward_code=reward.reward_code,
        id_story=reward.id_story,
        coins_required=reward.coins_required,
        reward_image=reward.reward_image
    )
    db.session.add(purchased)
    db.session.commit()

    return jsonify({"message": f"Reward {reward_code} unlocked successfully for this student"}), 200


@story_bp.route('/studentrewards/<string:student_code>', methods=['GET'])
def student_rewards(student_code):
    all_rewards = StoryReward.query.all()
    purchased = PurchasedReward.query.filter_by(student_code=student_code).all()
    purchased_codes = [r.reward_code for r in purchased]

    result = []
    for reward in all_rewards:
        reward_status = "unlocked" if reward.reward_code in purchased_codes else "locked"
        result.append({
            "reward_code": reward.reward_code,
            "coins_required": reward.coins_required,
            "reward_image": reward.reward_image,
            "status": reward_status
        })
    return jsonify(result)

   
