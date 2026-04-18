import os
import random

def get_image_task():
    """
    Returns a dictionary containing the path to an image and the instruction for the user.
    """
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    tasks = [
        {
            "id": "coffee_shop",
            "image_path": os.path.join(assets_dir, "scenario_coffee_shop.png"),
            "instruction": "Describe what is happening in this coffee shop. Mention at least three different activities people are doing and describe the atmosphere.",
            "prompt_for_ai": "A busy modern coffee shop with people working, chatting, and a barista at work."
        },
        {
            "id": "nature_park",
            "image_path": os.path.join(assets_dir, "scenario_nature_park.png"),
            "instruction": "Describe this park scene. Mention the environment and at least two different things the people are doing.",
            "prompt_for_ai": "A serene nature park with a pond, people walking dogs, and children playing."
        }
    ]
    
    return random.choice(tasks)
