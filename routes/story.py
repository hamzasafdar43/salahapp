from flask import Blueprint, request, jsonify
from db import db
from models.story import Story , StoriesData 
from models.story import StoryQuiz

story_bp = Blueprint('story', __name__)

@story_bp.route('/add-stories', methods=['POST'])
def create_story():
    data = request.get_json()

    storyName = data.get('storyName')
    quize = data.get('quize')
    getcoin = data.get('getcoin')

    if not storyName or not quize or getcoin is None:
        return jsonify({'error': 'storyName, quize, and getcoin are required'}), 400

    story = Story(
        storyName=storyName,
        quize=quize,
        getcoin=getcoin
    )

    db.session.add(story)
    db.session.commit()

    return jsonify({
        'id': story.id,
        'storyName': story.storyName,
        'quize': story.quize,
        'getcoin': story.getcoin
    }), 201

@story_bp.route('/stories', methods=['GET'])
def get_all_stories():
    stories = Story.query.all()
    return jsonify([
        {
            'id': s.id,
            'storyName': s.storyName,
            'quize': s.quize,
            'getcoin': s.getcoin
        } for s in stories
    ]), 200

@story_bp.route('/save-stories-data', methods=['POST'])
def add_storiesData():
    data = request.get_json()

    # Single story ko list banado for consistent loop
    if isinstance(data, dict):
        data = [data]

    for item in data:
        # Check by title
        existing = StoriesData.query.filter_by(title=item['title']).first()
        if existing:
            return jsonify({"message": f"Story with title '{item['title']}' already exists."}), 400

        story = StoriesData(
            title=item['title'],
            key=item['key'],
            subtitle=item['subtitle'],
            pages=item['pages'],
            audio_files=item['audioFiles']
        )
        db.session.add(story)

    db.session.commit()
    return jsonify({"message": "Story saved successfully."})

@story_bp.route('/storiesData', methods=['GET'])
def get_all_storiesData():
    storiesData = StoriesData.query.all()
    return jsonify([{
            "id": sd.id,
            "title": sd.title,
            "key": sd.key,
            "subtitle": sd.subtitle,
            "pages": sd.pages,
            "audioFiles": sd.audio_files

    } for sd in storiesData])


@story_bp.route('/save-story-quizzes', methods=['POST'])
def save_story_quizzes():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of story quiz data"}), 400

    response = []

    for story_entry in data:
        for key, quiz_sets in story_entry.items():
            existing_quiz = StoryQuiz.query.filter_by(story_key=key).first()

            if existing_quiz:
                existing_quiz.quiz_data = quiz_sets
                message = "Quiz updated successfully"
            else:
                new_quiz = StoryQuiz(
                    story_key=key,
                    quiz_data=quiz_sets
                )
                db.session.add(new_quiz)
                message = "Quiz saved successfully"

            response.append({
                "story_key": key,
                "message": message
            })

    db.session.commit()

    return jsonify(response), 201


@story_bp.route('/get-story-quizzes', methods=['GET'])
def get_story_quizzes():
    try:
        quizzes = StoryQuiz.query.all()
        response = []

        for quiz in quizzes:
            response.append({
                "story_key": quiz.story_key,
                "quiz_data": quiz.quiz_data  
            })

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
