#!/usr/bin/env python3
"""
SPIRIT HATCH - A Tamagotchi-style Spirit Animal Game
Raise your spirit animal through evolution stages by maintaining its stats!
ENHANCED VERSION with image display, improved stat decay, and day tracking
"""

import time
import random
import os
from datetime import datetime, timedelta

class SpiritAnimal:
    """Represents the player's spirit animal pet"""
    
    EVOLUTION_STAGES = [
        {"name": "Egg", "days_required": 0, "emoji": "🥚"},
        {"name": "Hatchling", "days_required": 1, "emoji": "🐣"},
        {"name": "Young Spirit", "days_required": 3, "emoji": "🦊"},
        {"name": "Mature Spirit", "days_required": 5, "emoji": "🦅"},
        {"name": "Ancient Spirit", "days_required": 8, "emoji": "🐉"}
    ]
    
    def __init__(self, name="Spirit"):
        self.name = name
        self.hunger = 100  # 0-100
        self.happiness = 100  # 0-100
        self.health = 100  # 0-100
        self.age_days = 0
        self.evolution_stage = 0
        self.last_update = datetime.now()
        self.is_alive = True
        self.interactions = 0
        self.total_time_alive = timedelta(0)
        
        # Track stat changes for display
        self.last_hunger = 100
        self.last_happiness = 100
        self.last_health = 100
        
    def get_stage_name(self):
        """Get current evolution stage name"""
        return self.EVOLUTION_STAGES[self.evolution_stage]["name"]
    
    def get_stage_emoji(self):
        """Get current evolution stage emoji"""
        return self.EVOLUTION_STAGES[self.evolution_stage]["emoji"]
    
    def update_stats(self):
        """Update stats based on time passed since last update"""
        if not self.is_alive:
            return
        
        now = datetime.now()
        time_diff = (now - self.last_update).total_seconds()
        
        # Store old values for comparison
        self.last_hunger = self.hunger
        self.last_happiness = self.happiness
        self.last_health = self.health
        
        self.last_update = now
        self.total_time_alive += timedelta(seconds=time_diff)
        
        # Decay rates (per minute) - set to -1 every 10 seconds = -6 per minute
        hunger_decay = 6.0
        happiness_decay = 6.0
        
        # Calculate decay based on actual time passed
        minutes_passed = time_diff / 60
        
        self.hunger = max(0, self.hunger - (hunger_decay * minutes_passed))
        self.happiness = max(0, self.happiness - (happiness_decay * minutes_passed))
        
        # Health is affected by hunger and happiness
        if self.hunger < 30 or self.happiness < 30:
            self.health = max(0, self.health - (0.5 * minutes_passed))
        elif self.hunger > 70 and self.happiness > 70:
            # Slowly recover health when well-fed and happy
            self.health = min(100, self.health + (0.25 * minutes_passed))
        
        # Check if pet dies
        if self.hunger <= 0 or self.happiness <= 0 or self.health <= 0:
            self.is_alive = False
            
    def get_stat_change_indicator(self, current, previous):
        """Get an indicator showing if stat increased, decreased, or stayed same"""
        diff = current - previous
        if abs(diff) < 1:
            return "─"
        elif diff > 0:
            return f"↑{diff:+.1f}"
        else:
            return f"↓{diff:.1f}"
    
    def feed(self):
        """Feed the spirit animal"""
        if not self.is_alive:
            return "Your spirit has already faded..."
        
        self.update_stats()
        
        if self.hunger >= 95:
            return f"{self.name} is already full! 🍽️"
        
        hunger_increase = random.randint(15, 25)
        health_increase = random.randint(5, 10)
        
        self.hunger = min(100, self.hunger + hunger_increase)
        self.health = min(100, self.health + health_increase)
        self.interactions += 1
        
        messages = [
            f"{self.name} happily munches on spiritual energy! ✨",
            f"{self.name} glows brighter as it feeds! 🌟",
            f"{self.name} feels nourished and content! 💫"
        ]
        return random.choice(messages)
    
    def play(self):
        """Play with the spirit animal"""
        if not self.is_alive:
            return "Your spirit has already faded..."
        
        self.update_stats()
        
        if self.happiness >= 95:
            return f"{self.name} is already very happy! 😊"
        
        happiness_increase = random.randint(15, 25)
        hunger_decrease = random.randint(5, 10)
        
        self.happiness = min(100, self.happiness + happiness_increase)
        self.hunger = max(0, self.hunger - hunger_decrease)
        self.interactions += 1
        
        messages = [
            f"{self.name} playfully dances around you! 💃",
            f"{self.name} sparkles with joy! ✨😊",
            f"{self.name} does a happy spin! 🌀",
            f"You share a magical moment with {self.name}! 🎭"
        ]
        return random.choice(messages)
    
    def rest(self):
        """Let the spirit animal rest"""
        if not self.is_alive:
            return "Your spirit has already faded..."
        
        self.update_stats()
        
        if self.health >= 95:
            return f"{self.name} is already well-rested! 😴"
        
        health_increase = random.randint(20, 30)
        happiness_increase = random.randint(5, 10)
        
        self.health = min(100, self.health + health_increase)
        self.happiness = min(100, self.happiness + happiness_increase)
        self.interactions += 1
        
        messages = [
            f"{self.name} curls up and rests peacefully... 😴",
            f"{self.name} takes a rejuvenating nap! 💤",
            f"{self.name} meditates and restores energy! 🧘"
        ]
        return random.choice(messages)
    
    def can_evolve(self):
        """Check if spirit animal can evolve"""
        if self.evolution_stage >= len(self.EVOLUTION_STAGES) - 1:
            return False
        
        next_stage = self.EVOLUTION_STAGES[self.evolution_stage + 1]
        return self.age_days >= next_stage["days_required"]
    
    def evolve(self):
        """Evolve the spirit animal to next stage"""
        if not self.is_alive:
            return "Your spirit has already faded..."
        
        if not self.can_evolve():
            next_stage = self.EVOLUTION_STAGES[self.evolution_stage + 1]
            days_needed = next_stage["days_required"] - self.age_days
            return f"❌ {self.name} needs {days_needed} more day(s) of care to evolve!"
        
        if self.evolution_stage >= len(self.EVOLUTION_STAGES) - 1:
            return f"🌟 {self.name} is already at maximum evolution!"
        
        # Check if stats are good enough for evolution
        if self.hunger < 50 or self.happiness < 50 or self.health < 50:
            return f"❌ {self.name} needs better care to evolve! (All stats must be above 50)"
        
        old_stage = self.get_stage_name()
        self.evolution_stage += 1
        new_stage = self.get_stage_name()
        
        # Boost stats on evolution
        self.hunger = min(100, self.hunger + 20)
        self.happiness = min(100, self.happiness + 20)
        self.health = min(100, self.health + 20)
        
        return f"✨ EVOLUTION! ✨\n{old_stage} → {new_stage}!\n{self.get_stage_emoji()} {self.name} has evolved!"
    
    def get_status_bar(self, value, show_change=False, previous=None):
        """Create a visual status bar"""
        bar_length = 20
        filled = int((value / 100) * bar_length)
        empty = bar_length - filled
        
        if value > 70:
            color = "🟢"
        elif value > 30:
            color = "🟡"
        else:
            color = "🔴"
        
        bar = f"{color} [{'█' * filled}{'░' * empty}] {value:.0f}%"
        
        if show_change and previous is not None:
            change = self.get_stat_change_indicator(value, previous)
            bar += f" {change}"
        
        return bar
    
    def get_time_alive_str(self):
        """Get formatted string of time alive"""
        total_seconds = int(self.total_time_alive.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_status(self):
        """Get detailed status of the spirit animal"""
        self.update_stats()
        
        if not self.is_alive:
            return f"""
╔════════════════════════════════════════╗
║           💀 GAME OVER 💀              ║
╚════════════════════════════════════════╝
Your spirit animal has faded away...
It lived for {self.age_days} day(s).
Time alive: {self.get_time_alive_str()}
Final stage: {self.get_stage_name()}

Thank you for caring for {self.name}. 🕊️
"""
        
        status = f"""
╔════════════════════════════════════════╗
║         SPIRIT HATCH STATUS            ║
╚════════════════════════════════════════╝

{self.get_stage_emoji()} Name: {self.name}
📊 Stage: {self.get_stage_name()} (Stage {self.evolution_stage + 1}/{len(self.EVOLUTION_STAGES)})
📅 Age: {self.age_days} day(s)
⏱️  Time Alive: {self.get_time_alive_str()}
🎮 Interactions: {self.interactions}

╭────────────────────────────────────────╮
│ STATS (auto-decay active)              │
├────────────────────────────────────────┤
│ Hunger:    {self.get_status_bar(self.hunger, True, self.last_hunger)}
│ Happiness: {self.get_status_bar(self.happiness, True, self.last_happiness)}
│ Health:    {self.get_status_bar(self.health, True, self.last_health)}
╰────────────────────────────────────────╯

⏳ Decay Rate: -1 every 10 seconds for hunger & happiness
"""
        
        # Evolution info
        if self.evolution_stage < len(self.EVOLUTION_STAGES) - 1:
            next_stage = self.EVOLUTION_STAGES[self.evolution_stage + 1]
            days_until = max(0, next_stage["days_required"] - self.age_days)
            if days_until > 0:
                status += f"\n⏳ Next evolution in: {days_until} day(s)"
            else:
                status += f"\n✨ Ready to evolve! Use 'evolve' command!"
        else:
            status += f"\n🌟 Maximum evolution reached!"
        
        # Warnings
        if self.hunger < 30:
            status += f"\n⚠️  {self.name} is very hungry!"
        if self.happiness < 30:
            status += f"\n⚠️  {self.name} is feeling sad!"
        if self.health < 30:
            status += f"\n⚠️  {self.name}'s health is critical!"
        
        return status


class Game:
    """Main game controller"""
    
    def __init__(self):
        self.spirit = None
        self.running = True
        self.game_start = datetime.now()
        self.last_day_update = datetime.now()
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Print game header"""
        print("""
╔══════════════════════════════════════════════╗
║                                              ║
║           ✨ SPIRIT HATCH ✨                 ║
║      Raise Your Mystical Spirit Animal      ║
║                                              ║
╚══════════════════════════════════════════════╝
""")
    
    def update_game_days(self):
        """Update in-game days (accelerated time for testing)"""
        # 30 real seconds = 1 game day for faster gameplay
        now = datetime.now()
        time_diff = (now - self.last_day_update).total_seconds()
        
        if time_diff >= 30:  # Every 30 seconds = 1 day
            days_passed = int(time_diff / 30)
            self.spirit.age_days += days_passed
            self.last_day_update = now
            return days_passed
        return 0
    
    def show_help(self):
        """Display help information"""
        return """
╔════════════════════════════════════════╗
║            COMMANDS                    ║
╚════════════════════════════════════════╝

feed    - Feed your spirit animal 🍖
play    - Play with your spirit animal 🎮
rest    - Let your spirit rest 😴
status  - View detailed stats 📊
evolve  - Evolve to next stage ✨
help    - Show this help menu 📖
quit    - Exit the game 👋

╔════════════════════════════════════════╗
║       STAT DECAY SYSTEM                ║
╚════════════════════════════════════════╝

⚠️  Stats automatically decay over time:
   • Hunger: -1 every 10 seconds
   • Happiness: -1 every 10 seconds
   • Health: Affected by hunger/happiness

💡 The longer you wait between actions,
   the more your stats will decrease!

╔════════════════════════════════════════╗
║          DAY SYSTEM                    ║
╚════════════════════════════════════════╝

⏰ Time passes in real-time!
   • 30 real seconds = 1 game day
   • Check 'status' to see time alive
   • Days determine evolution eligibility

╔════════════════════════════════════════╗
║          HOW TO WIN                    ║
╚════════════════════════════════════════╝

Keep your spirit's hunger, happiness, and
health above critical levels. Evolve through
all 5 stages to achieve ultimate victory!

Stage 1: Egg 🥚 (0 days)
Stage 2: Hatchling 🐣 (1 day)
Stage 3: Young Spirit 🦊 (3 days)
Stage 4: Mature Spirit 🦅 (5 days)
Stage 5: Ancient Spirit 🐉 (8 days - WIN!)

⚠️  If any stat reaches 0, your spirit fades!
"""
    
    def start_game(self):
        """Initialize and start the game"""
        self.clear_screen()
        self.print_header()
        
        print("Welcome, Spirit Keeper!")
        name = input("What will you name your spirit animal? (Press Enter for 'Spirit'): ").strip()
        
        if not name:
            name = "Spirit"
        
        self.spirit = SpiritAnimal(name)
        
        print(f"\n✨ {name} has been born! ✨")
        print(f"\nYour journey begins with a mysterious egg... 🥚")
        print(f"\n⚠️  Remember: Stats decay over time!")
        print(f"   • Hunger: -1 every 10 seconds")
        print(f"   • Happiness: -1 every 10 seconds")
        print(f"\n⏰ Time System: 30 real seconds = 1 game day")
        print(f"\nTip: Check on {name} regularly to keep stats healthy!")
        input("\nPress Enter to begin your journey...")
    
    def process_command(self, command):
        """Process user commands"""
        command = command.lower().strip()
        
        if not command:
            return "Please enter a command. Type 'help' for available commands."
        
        # Update game days
        days_passed = self.update_game_days()
        if days_passed > 0 and self.spirit.is_alive:
            print(f"\n⏰ {days_passed} day(s) have passed! Total age: {self.spirit.age_days} days")
        
        if command == "feed":
            return self.spirit.feed()
        
        elif command == "play":
            return self.spirit.play()
        
        elif command == "rest":
            return self.spirit.rest()
        
        elif command == "status":
            return self.spirit.get_status()
        
        elif command == "evolve":
            return self.spirit.evolve()
        
        elif command == "help":
            return self.show_help()
        
        elif command == "quit":
            self.running = False
            return f"\n👋 Goodbye! You cared for {self.spirit.name} for {self.spirit.age_days} day(s) ({self.spirit.get_time_alive_str()}).\n"
        
        else:
            return f"❌ Unknown command: '{command}'. Type 'help' for available commands."
    
    def check_win_condition(self):
        """Check if player has won the game"""
        if self.spirit.evolution_stage >= len(SpiritAnimal.EVOLUTION_STAGES) - 1:
            if self.spirit.hunger > 50 and self.spirit.happiness > 50 and self.spirit.health > 50:
                return True
        return False
    
    def run(self):
        """Main game loop"""
        self.start_game()
        
        while self.running and self.spirit.is_alive:
            print("\n" + "─" * 46)
            print("\nAvailable commands: feed, play, rest, status, evolve, help, quit")
            command = input(f"\n{self.spirit.get_stage_emoji()} What would you like to do? > ").strip()
            
            result = self.process_command(command)
            print(f"\n{result}")
            
            # Check win condition
            if self.check_win_condition():
                self.clear_screen()
                    
                print(f"""
╔══════════════════════════════════════════════╗
║                                              ║
║              🎉 VICTORY! 🎉                  ║
║                                              ║
║     You've raised an Ancient Spirit!        ║
║                                              ║
╚══════════════════════════════════════════════╝

{self.spirit.get_stage_emoji()} {self.spirit.name} has reached its ultimate form!

📊 Final Stats:
   • Age: {self.spirit.age_days} days
   • Time Alive: {self.spirit.get_time_alive_str()}
   • Interactions: {self.spirit.interactions}
   • Hunger: {self.spirit.hunger:.0f}%
   • Happiness: {self.spirit.happiness:.0f}%
   • Health: {self.spirit.health:.0f}%

You are a true Spirit Keeper! 🏆
Thank you for playing SPIRIT HATCH! ✨
""")
                self.running = False
        
        # Game over check
        if not self.spirit.is_alive:
            print(self.spirit.get_status())


def main():
    """Entry point for the game"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
