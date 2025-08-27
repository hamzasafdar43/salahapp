from models.story import Story, StoryReward
import re
import uuid

def generate_story_code():
    last_story = Story.query.order_by(Story.id_story.desc()).first()
    next_id = (last_story.id_story + 1) if last_story else 1
    return f"STR{str(next_id).zfill(3)}"

def generate_content_code():
    return f"CONTENT-{uuid.uuid4().hex[:8]}"

def generate_reward_code():
    last_reward = StoryReward.query.order_by(StoryReward.id_story_reward.desc()).first()
    if not last_reward:
        return "REW001"
    last_code = last_reward.reward_code
    number = int(re.findall(r'\d+', last_code)[0])
    new_number = number + 1
    return f"REW{new_number:03d}"

def generate_code(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

def generate_code(prefix):
    return prefix + uuid.uuid4().hex[:6].upper()