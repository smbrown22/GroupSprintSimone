#!/usr/bin/env python3
"""
SPIRIT HATCH - Simple Python Web Server
Uses only Python standard library (no external dependencies!)
Works perfectly in VS Code
"""

import http.server
import socketserver
import json
import random
import time
from urllib.parse import parse_qs, urlparse
import os

PORT = 8000

# Game constants
EVOLUTION_STAGES = [
    {"name": "Egg", "days_required": 0, "emoji": "🥚"},
    {"name": "Hatchling", "days_required": 1, "emoji": "🐣"},
    {"name": "Young Spirit", "days_required": 3, "emoji": "🦊"},
    {"name": "Mature Spirit", "days_required": 5, "emoji": "🦅"},
    {"name": "Ancient Spirit", "days_required": 8, "emoji": "🐉"}
]

RANDOM_EVENTS = [
    {
        "name": "Shiny Stone",
        "message": "✨ {name} found a shiny stone and is delighted!",
        "effects": {"happiness": 15, "hunger": -5},
        "emoji": "💎"
    },
    {
        "name": "Gentle Rain",
        "message": "🌧️ A gentle rain falls, refreshing {name}!",
        "effects": {"health": 10, "happiness": 10},
        "emoji": "🌧️"
    },
    {
        "name": "Wild Spirit Visit",
        "message": "👻 A wild spirit visits and plays with {name}!",
        "effects": {"happiness": 20, "hunger": -10},
        "emoji": "👻"
    },
    {
        "name": "Mysterious Berry",
        "message": "🫐 {name} discovers a mysterious berry bush!",
        "effects": {"hunger": 15, "health": 5},
        "emoji": "🫐"
    },
    {
        "name": "Dark Cloud",
        "message": "☁️ A dark cloud passes overhead, making {name} uneasy...",
        "effects": {"happiness": -10, "health": -5},
        "emoji": "☁️"
    },
    {
        "name": "Shooting Star",
        "message": "⭐ {name} sees a shooting star and makes a wish!",
        "effects": {"happiness": 25, "health": 10},
        "emoji": "⭐"
    },
    {
        "name": "Ancient Whisper",
        "message": "🌀 Ancient whispers grant {name} wisdom and energy!",
        "effects": {"health": 15, "happiness": 15, "hunger": 10},
        "emoji": "🌀"
    },
    {
        "name": "Spirit Feast",
        "message": "🍱 {name} stumbles upon a spirit feast!",
        "effects": {"hunger": 25, "happiness": 15},
        "emoji": "🍱"
    },
    {
        "name": "Moonbeam",
        "message": "🌙 A moonbeam illuminates {name}, restoring vitality!",
        "effects": {"health": 20, "happiness": 10},
        "emoji": "🌙"
    }
]

# Simple in-memory game state (one game at a time)
game_state = {
    "name": "Spirit",
    "hunger": 50.0,
    "happiness": 50.0,
    "health": 50.0,
    "age_days": 0,
    "evolution_stage": 0,
    "interactions": 0,
    "events_experienced": 0,
    "is_alive": True,
    "start_time": time.time(),
    "last_update": time.time(),
    "last_day_update": time.time(),
    "last_event_check": time.time()
}

def clamp(value, min_val, max_val):
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))

def update_stats():
    """Update stats based on time passed"""
    global game_state
    
    if not game_state["is_alive"]:
        return
    
    now = time.time()
    time_diff = now - game_state["last_update"]
    game_state["last_update"] = now
    
    # Decay: -3 every 10 seconds = -18 per minute = -0.3 per second
    decay_rate = 0.3
    game_state["hunger"] = max(0, game_state["hunger"] - (decay_rate * time_diff))
    game_state["happiness"] = max(0, game_state["happiness"] - (decay_rate * time_diff))
    
    # Health affected by hunger and happiness
    if game_state["hunger"] < 30 or game_state["happiness"] < 30:
        game_state["health"] = max(0, game_state["health"] - (0.1 * time_diff))
    elif game_state["hunger"] > 70 and game_state["happiness"] > 70:
        game_state["health"] = min(100, game_state["health"] + (0.05 * time_diff))
    
    # Check death
    if game_state["hunger"] <= 0 or game_state["happiness"] <= 0 or game_state["health"] <= 0:
        game_state["is_alive"] = False
    
    # Update days (30 seconds = 1 day)
    if now - game_state["last_day_update"] >= 30:
        game_state["age_days"] += 1
        game_state["last_day_update"] = now

def check_random_event():
    """Check if a random event should occur"""
    global game_state
    
    if not game_state["is_alive"]:
        return None
    
    now = time.time()
    if now - game_state["last_event_check"] >= 60:  # Check every 60 seconds
        game_state["last_event_check"] = now
        
        if random.random() < 0.20:  # 20% chance
            event = random.choice(RANDOM_EVENTS)
            
            # Apply effects
            if "hunger" in event["effects"]:
                game_state["hunger"] = clamp(game_state["hunger"] + event["effects"]["hunger"], 0, 100)
            if "happiness" in event["effects"]:
                game_state["happiness"] = clamp(game_state["happiness"] + event["effects"]["happiness"], 0, 100)
            if "health" in event["effects"]:
                game_state["health"] = clamp(game_state["health"] + event["effects"]["health"], 0, 100)
            
            game_state["events_experienced"] += 1
            return event
    
    return None

def perform_action(action):
    """Perform a game action"""
    global game_state
    
    update_stats()
    
    if not game_state["is_alive"]:
        return {"success": False, "message": "Your spirit has faded..."}
    
    message = ""
    
    if action == "feed":
        if game_state["hunger"] >= 95:
            message = f"{game_state['name']} is already full! 🍽️"
        else:
            game_state["hunger"] = min(100, game_state["hunger"] + random.randint(15, 25))
            game_state["health"] = min(100, game_state["health"] + random.randint(5, 10))
            game_state["interactions"] += 1
            messages = [
                f"{game_state['name']} happily munches on spiritual energy! ✨",
                f"{game_state['name']} glows brighter as it feeds! 🌟",
                f"{game_state['name']} feels nourished and content! 💫"
            ]
            message = random.choice(messages)
    
    elif action == "play":
        if game_state["happiness"] >= 95:
            message = f"{game_state['name']} is already very happy! 😊"
        else:
            game_state["happiness"] = min(100, game_state["happiness"] + random.randint(15, 25))
            game_state["hunger"] = max(0, game_state["hunger"] - random.randint(5, 10))
            game_state["interactions"] += 1
            messages = [
                f"{game_state['name']} playfully dances around you! 💃",
                f"{game_state['name']} sparkles with joy! ✨😊",
                f"{game_state['name']} does a happy spin! 🌀"
            ]
            message = random.choice(messages)
    
    elif action == "rest":
        if game_state["health"] >= 95:
            message = f"{game_state['name']} is already well-rested! 😴"
        else:
            game_state["health"] = min(100, game_state["health"] + random.randint(20, 30))
            game_state["happiness"] = min(100, game_state["happiness"] + random.randint(5, 10))
            game_state["interactions"] += 1
            messages = [
                f"{game_state['name']} curls up and rests peacefully... 😴",
                f"{game_state['name']} takes a rejuvenating nap! 💤",
                f"{game_state['name']} meditates and restores energy! 🧘"
            ]
            message = random.choice(messages)
    
    elif action == "train":
        game_state["health"] = min(100, game_state["health"] + random.randint(12, 18))
        game_state["happiness"] = min(100, game_state["happiness"] + random.randint(10, 15))
        game_state["hunger"] = max(0, game_state["hunger"] - random.randint(15, 20))
        game_state["interactions"] += 1
        messages = [
            f"{game_state['name']} practices spiritual techniques! 🥋",
            f"{game_state['name']} trains diligently! 💪",
            f"{game_state['name']} masters a new skill! 🎯"
        ]
        message = random.choice(messages)
    
    elif action == "explore":
        outcome = random.choice(["great", "good", "neutral", "bad"])
        
        if outcome == "great":
            game_state["happiness"] = min(100, game_state["happiness"] + random.randint(20, 30))
            game_state["hunger"] = min(100, game_state["hunger"] + random.randint(10, 20))
            game_state["health"] = min(100, game_state["health"] + random.randint(5, 15))
            message = f"{game_state['name']} discovers a magical paradise! 🌺✨"
        elif outcome == "good":
            game_state["happiness"] = min(100, game_state["happiness"] + random.randint(15, 20))
            game_state["hunger"] = min(100, game_state["hunger"] + random.randint(5, 10))
            message = f"{game_state['name']} has a pleasant adventure! 🗺️"
        elif outcome == "neutral":
            game_state["happiness"] = min(100, game_state["happiness"] + random.randint(5, 10))
            game_state["hunger"] = max(0, game_state["hunger"] - random.randint(5, 10))
            message = f"{game_state['name']} wanders around safely. 🚶"
        else:
            game_state["happiness"] = max(0, game_state["happiness"] - random.randint(10, 15))
            game_state["health"] = max(0, game_state["health"] - random.randint(10, 15))
            game_state["hunger"] = max(0, game_state["hunger"] - random.randint(5, 10))
            message = f"{game_state['name']} gets lost and returns tired... 😰"
        
        game_state["interactions"] += 1
    
    elif action == "meditate":
        game_state["health"] = min(100, game_state["health"] + random.randint(10, 15))
        game_state["happiness"] = min(100, game_state["happiness"] + random.randint(10, 15))
        game_state["hunger"] = min(100, game_state["hunger"] + random.randint(8, 12))
        game_state["interactions"] += 1
        messages = [
            f"{game_state['name']} enters a meditative state... 🧘‍♀️✨",
            f"{game_state['name']} connects with cosmic energy! 🌌",
            f"{game_state['name']} achieves inner peace! ☯️"
        ]
        message = random.choice(messages)
    
    elif action == "groom":
        if game_state["happiness"] >= 90 and game_state["health"] >= 90:
            message = f"{game_state['name']} is already pristine! ✨"
        else:
            game_state["happiness"] = min(100, game_state["happiness"] + random.randint(12, 18))
            game_state["health"] = min(100, game_state["health"] + random.randint(8, 12))
            game_state["interactions"] += 1
            messages = [
                f"{game_state['name']} enjoys being groomed! ✨🪮",
                f"You tend to {game_state['name']}'s form! 🌟",
                f"{game_state['name']} feels pampered! 💆‍♀️💕"
            ]
            message = random.choice(messages)
    
    elif action == "evolve":
        if game_state["evolution_stage"] >= len(EVOLUTION_STAGES) - 1:
            message = f"🌟 {game_state['name']} is at maximum evolution!"
        else:
            next_stage = EVOLUTION_STAGES[game_state["evolution_stage"] + 1]
            
            if game_state["age_days"] < next_stage["days_required"]:
                days_needed = next_stage["days_required"] - game_state["age_days"]
                message = f"❌ Need {days_needed} more day(s) to evolve!"
            elif game_state["hunger"] < 50 or game_state["happiness"] < 50 or game_state["health"] < 50:
                message = "❌ All stats must be above 50 to evolve!"
            else:
                old_stage = EVOLUTION_STAGES[game_state["evolution_stage"]]
                game_state["evolution_stage"] += 1
                new_stage = EVOLUTION_STAGES[game_state["evolution_stage"]]
                
                game_state["hunger"] = min(100, game_state["hunger"] + 20)
                game_state["happiness"] = min(100, game_state["happiness"] + 20)
                game_state["health"] = min(100, game_state["health"] + 20)
                
                message = f"✨ EVOLUTION! ✨\n{old_stage['name']} → {new_stage['name']}!"
    
    else:
        return {"error": "Invalid action"}
    
    return {
        "success": True,
        "message": message,
        "state": game_state,
        "stage": EVOLUTION_STAGES[game_state["evolution_stage"]]
    }


class GameHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the game"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            # Serve the HTML file
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read and serve the HTML file
            html_file = os.path.join(os.path.dirname(__file__), 'game.html')
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.wfile.write(b"Error: game.html not found!")
        
        elif parsed_path.path == '/api/state':
            # Get game state
            update_stats()
            event = check_random_event()
            
            response = {
                "state": game_state,
                "stage": EVOLUTION_STAGES[game_state["evolution_stage"]]
            }
            
            if event:
                response["event"] = event
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/start':
            # Start new game
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            global game_state
            game_state = {
                "name": data.get('name', 'Spirit'),
                "hunger": 50.0,
                "happiness": 50.0,
                "health": 50.0,
                "age_days": 0,
                "evolution_stage": 0,
                "interactions": 0,
                "events_experienced": 0,
                "is_alive": True,
                "start_time": time.time(),
                "last_update": time.time(),
                "last_day_update": time.time(),
                "last_event_check": time.time()
            }
            
            response = {"success": True, "state": game_state}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        elif parsed_path.path.startswith('/api/action/'):
            # Perform action
            action = parsed_path.path.split('/')[-1]
            result = perform_action(action)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        # Only log important messages
        if '200' not in str(args[1]):
            return
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the web server"""
    print("\n" + "="*60)
    print("✨ SPIRIT HATCH - Simple Python Web Server ✨")
    print("="*60)
    print("\n✅ No external dependencies needed!")
    print("✅ Uses only Python standard library")
    print("✅ Works perfectly in VS Code\n")
    print(f"📡 Server starting on port {PORT}...")
    print(f"🌐 Open your browser to: http://localhost:{PORT}")
    print("\n⚠️  Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    with socketserver.TCPServer(("", PORT), GameHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✨ Server stopped. Thanks for playing Spirit Hatch! ✨\n")


if __name__ == "__main__":
    main()
