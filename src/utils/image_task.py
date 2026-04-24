import os
import random

def get_image_task():
    """
    Returns a dictionary containing the path to a visual stimulus and the instruction.
    """
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    
    tasks = [
        {
            "id": "coffee_shop",
            "type": "image",
            "image_path": os.path.join(assets_dir, "scenario_coffee_shop.png"),
            "instruction": "Describe what is happening in this coffee shop. Mention at least three activities and describe the atmosphere.",
            "prompt_for_ai": "A busy modern coffee shop with people working, chatting, and a barista at work."
        },
        {
            "id": "cooking_video",
            "type": "video",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4", # Placeholder stock video
            "instruction": "Narrate the actions in this short video clip in real-time. What do you see happening?",
            "prompt_for_ai": "A short video showing a character in a nature setting performing various actions."
        },
        {
            "id": "debate_remote",
            "type": "debate",
            "instruction": "DEBATE MODE: 'Remote work is much better for productivity than working in an office.'",
            "challenge": "You have 60 seconds to argue AGAINST this statement. Provide at least two strong reasons.",
            "prompt_for_ai": "Debate scenario where the user is arguing that office work is better than remote work."
        },
        {
            "id": "debate_ai",
            "type": "debate",
            "instruction": "DEBATE MODE: 'Artificial Intelligence will eventually replace all human creativity.'",
            "challenge": "Argue FOR this statement. How might AI replace human art, music, and writing?",
            "prompt_for_ai": "Debate scenario where the user argues AI will replace human creativity."
        }
    ]
    
    return random.choice(tasks)
