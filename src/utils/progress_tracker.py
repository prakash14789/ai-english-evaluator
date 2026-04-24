import json
import os
from datetime import datetime, timedelta

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "user_progress.json")

def load_progress():
    if not os.path.exists(os.path.dirname(PROGRESS_FILE)):
        os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {
        "xp": 0,
        "streak": 0,
        "last_active": None,
        "history": [],
        "badges": []
    }

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=4)

def update_xp(amount):
    progress = load_progress()
    progress["xp"] += amount
    save_progress(progress)
    return progress["xp"]

def track_session(score, archetype, duration_sec):
    progress = load_progress()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Update Streak
    if progress["last_active"]:
        last_date = datetime.strptime(progress["last_active"], "%Y-%m-%d")
        delta = datetime.now() - last_date
        if delta.days == 1:
            progress["streak"] += 1
        elif delta.days > 1:
            progress["streak"] = 1
    else:
        progress["streak"] = 1
    
    progress["last_active"] = today
    
    # Add to history
    progress["history"].append({
        "date": today,
        "score": score,
        "archetype": archetype,
        "duration": duration_sec
    })
    
    # XP logic: 10 XP per minute spoken + 50 XP per session + (score * 5)
    session_xp = int((duration_sec / 60) * 10) + 50 + int(score * 5)
    progress["xp"] += session_xp
    
    # Badge logic
    check_badges(progress)
    
    save_progress(progress)
    return session_xp

def check_badges(progress):
    badges = set(progress.get("badges", []))
    
    # 1. Streak badges
    if progress["streak"] >= 3: badges.add("🔥 3-Day Streak")
    if progress["streak"] >= 7: badges.add("👑 Weekly Warrior")
    
    # 2. XP badges
    if progress["xp"] >= 500: badges.add("🌟 Rising Star")
    if progress["xp"] >= 2000: badges.add("🚀 English Pro")
    
    # 3. Score badges
    if any(h["score"] >= 9.0 for h in progress["history"]):
        badges.add("💎 Native-Like Speaker")
        
    progress["badges"] = list(badges)

def get_stats():
    progress = load_progress()
    return progress
