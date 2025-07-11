from flask import Blueprint, request, jsonify
from db import db
from models.story import Story

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
