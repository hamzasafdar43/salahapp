from flask import Blueprint, request, jsonify
from db import db
from models.story import Story , StoryContent , StoryQuiz
from datetime import datetime

story_bp = Blueprint('story', __name__)

@story_bp.route('/add-stories', methods=['POST'])
def save_story():
    data = request.get_json()

    # Generate story_code automatically
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = 1 if not last_story else last_story.id_story + 1
    story_code = f"story{str(next_id).zfill(4)}"

    story = Story(
        story_code=story_code,
        title=data['title'],
        sub_title=data.get('sub_title')
    )

    db.session.add(story)
    db.session.commit()

    return jsonify({
        'message': 'Story saved successfully',
        'story_code': story_code
    }), 201

@story_bp.route('/add-story-content', methods=['POST'])
def save_story_content():
    data = request.get_json()

    story_id = data.get('story_id')
    page_content = data.get('page_content') 

    # Validate story_id exists
    story = Story.query.get(story_id)
    if not story:
        return jsonify({'error': 'Story not found'}), 404

    last_content = StoryContent.query.order_by(StoryContent.id_story_content.desc()).first()
    next_id = 1 if not last_content else last_content.id_story_content + 1
    content_code = f"content{str(next_id).zfill(4)}"

    story_content = StoryContent(
        content_code=content_code,
        page_content=page_content,
        story_id=story_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.session.add(story_content)
    db.session.commit()

    return jsonify({'message': 'Story content saved successfully', 'content_code': content_code}), 201



@story_bp.route('/add-story-quiz', methods=['POST'])
def save_story_quiz():
    data = request.get_json()

    # Validate required field
    story_content_id = data.get('story_content_id')
    if not story_content_id:
        return jsonify({'error': 'story_content_id is required'}), 400

    # Check if StoryContent exists
    story_content = StoryContent.query.get(story_content_id)
    if not story_content:
        return jsonify({'error': 'Invalid story_content_id'}), 404

    # Auto-generate quiz_code
    last_quiz = StoryQuiz.query.order_by(StoryQuiz.id_story_quiz.desc()).first()
    next_id = 1 if not last_quiz else last_quiz.id_story_quiz + 1
    quiz_code = f"quiz{str(next_id).zfill(4)}"

    # Create and save quiz
    new_quiz = StoryQuiz(
        quiz_code=quiz_code,
        story_content_id=story_content_id
    )
    db.session.add(new_quiz)
    db.session.commit()

    return jsonify({
        'message': 'Story Quiz saved successfully',
        'quiz_code': quiz_code,
        'id_story_quiz': new_quiz.id_story_quiz
    }), 201
