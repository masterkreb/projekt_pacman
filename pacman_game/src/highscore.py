"""
Highscore Management System
Handles loading, saving, and updating highscores
"""

import os
import json
from typing import List, Tuple


class HighscoreManager:
    """Manages the game's highscore system"""

    def __init__(self, max_scores: int = 5):
        self.max_scores = max_scores
        self.highscore_dir = "assets/highscore"
        self.highscore_file = os.path.join(self.highscore_dir, "highscores.txt")
        self.scores = []

        # Create directory if it doesn't exist
        self.ensure_directory()

        # Load existing scores
        self.load_scores()

    def ensure_directory(self):
        """Create the highscore directory if it doesn't exist"""
        if not os.path.exists(self.highscore_dir):
            try:
                os.makedirs(self.highscore_dir)
                print(f"Created highscore directory: {self.highscore_dir}")
            except Exception as e:
                print(f"Error creating highscore directory: {e}")

    def load_scores(self):
        """Load highscores from file"""
        if os.path.exists(self.highscore_file):
            try:
                with open(self.highscore_file, 'r') as f:
                    # Read scores line by line
                    self.scores = []
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                score = int(line)
                                self.scores.append(score)
                            except ValueError:
                                print(f"Invalid score in file: {line}")

                    # Ensure scores are sorted and limited
                    self.scores.sort(reverse=True)
                    self.scores = self.scores[:self.max_scores]
                    print(f"Loaded {len(self.scores)} highscores")

            except Exception as e:
                print(f"Error loading highscores: {e}")
                self.scores = []
        else:
            print("No highscore file found, starting fresh")
            self.scores = []

    def save_scores(self):
        """Save highscores to file"""
        try:
            with open(self.highscore_file, 'w') as f:
                for score in self.scores:
                    f.write(f"{score}\n")
            print(f"Saved {len(self.scores)} highscores")
        except Exception as e:
            print(f"Error saving highscores: {e}")

    def is_highscore(self, score: int) -> bool:
        """Check if a score qualifies as a highscore"""
        if len(self.scores) < self.max_scores:
            return score > 0
        return score > self.scores[-1]

    def add_score(self, score: int) -> int:
        """
        Add a new score to the highscore list
        Returns the position (1-based) if it's a highscore, or 0 if not
        """
        if score <= 0:
            return 0

        # Add the score
        self.scores.append(score)
        self.scores.sort(reverse=True)

        # Find position of the new score
        position = self.scores.index(score) + 1

        # Keep only top scores
        self.scores = self.scores[:self.max_scores]

        # Save if the score made it to the list
        if position <= self.max_scores:
            self.save_scores()
            return position

        return 0

    def get_scores(self) -> List[int]:
        """Get the current highscore list"""
        return self.scores.copy()

    def get_formatted_scores(self) -> List[str]:
        """Get formatted highscore strings for display"""
        formatted = []
        for i, score in enumerate(self.scores):
            formatted.append(f"{i + 1}. {score:,} Points")

        # Fill empty slots
        for i in range(len(self.scores), self.max_scores):
            formatted.append(f"{i + 1}. ----- Points")

        return formatted

    def reset_scores(self):
        """Reset all highscores (for testing/admin purposes)"""
        self.scores = []
        self.save_scores()
        print("Highscores reset!")

    def get_rank(self, score: int) -> int:
        """Get the rank a score would achieve (0 if not a highscore)"""
        if score <= 0:
            return 0

        # Check where this score would rank
        temp_scores = self.scores.copy()
        temp_scores.append(score)
        temp_scores.sort(reverse=True)

        position = temp_scores.index(score) + 1

        if position <= self.max_scores:
            return position
        return 0