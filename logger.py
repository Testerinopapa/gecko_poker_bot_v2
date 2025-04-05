"""
GeckoBot Poker - Logging System
This module provides a comprehensive logging system for the GeckoBot poker bot.
It captures all console output and writes it to structured log files for later analysis.
"""

import logging
import os
import sys
import time
import json
import traceback
import psutil
import gc
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from enum import IntEnum
from poker_enums import Street, Action, Position

class DebugLevel(IntEnum):
    """Debug levels for the logger."""
    NONE = 0        # No debugging output
    ERROR = 1       # Only error messages
    INFO = 2        # Basic information
    DEBUG = 3       # Detailed debugging information
    TRACE = 4       # Full trace of all operations

class TeeOutput:
    """
    Class to capture stdout and stderr and redirect to both console and logger
    """
    def __init__(self, logger, stream=sys.stdout):
        self.logger = logger
        self.stream = stream
        self.buffer = ""

    def write(self, message):
        if message.strip():  # Only log non-empty messages
            if message.endswith('\n'):
                self.buffer += message[:-1]
                self.flush()
            else:
                self.buffer += message

        # Always write to the original stream
        self.stream.write(message)

    def flush(self):
        if self.buffer:
            if self.stream == sys.stdout:
                self.logger.info(self.buffer)
            else:
                self.logger.error(self.buffer)
            self.buffer = ""
        self.stream.flush()

class GeckoLogger:
    """
    Custom logger for GeckoBot that captures all output and provides structured logging
    """
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO, debug_level: DebugLevel = DebugLevel.INFO):
        self.log_dir = log_dir
        self.log_level = log_level
        self.debug_level = debug_level
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.hand_counter = 0
        self.current_street = None
        self.current_round = 0

        # Performance metrics
        self.start_time = time.time()
        self.decision_times = []
        self.memory_usage = []
        self.win_loss_record = {"wins": 0, "losses": 0, "ties": 0}

        # Decision tracking
        self.decision_history = []

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Set up file logger
        self.logger = logging.getLogger("geckobot")
        self.logger.setLevel(log_level)

        # Create handlers
        self._setup_handlers()

        # Capture stdout and stderr
        self._capture_output()

        # Game state tracking
        self.game_state = {
            "hands": [],
            "current_hand": None
        }

        self.logger.info(f"=== GeckoBot Logging Session {self.session_id} Started ===")

    def _setup_handlers(self):
        """Set up logging handlers for file and console output"""
        # Clear any existing handlers
        self.logger.handlers = []

        # File handler for complete logs
        file_handler = logging.FileHandler(
            os.path.join(self.log_dir, f"geckobot_{self.session_id}.log")
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # JSON handler for structured logging
        self.json_file_path = os.path.join(self.log_dir, f"geckobot_{self.session_id}_structured.log")
        with open(self.json_file_path, 'w') as f:
            f.write('[]')  # Initialize with empty array

    def _capture_output(self):
        """Capture stdout and stderr to log all output"""
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = TeeOutput(self.logger, sys.stdout)
        sys.stderr = TeeOutput(self.logger, sys.stderr)

        # Register cleanup function to restore stdout/stderr
        import atexit
        atexit.register(self._restore_output)

    def _restore_output(self):
        """Restore original stdout and stderr"""
        if hasattr(self, 'original_stdout'):
            sys.stdout = self.original_stdout
        if hasattr(self, 'original_stderr'):
            sys.stderr = self.original_stderr

    def start_round(self, round_num: int):
        """Log the start of a new round"""
        self.current_round = round_num
        self.logger.info(f"=== Round {round_num} Started ===")

    def start_hand(self, hand_id: int):
        """Log the start of a new hand"""
        self.hand_counter = hand_id
        self.logger.info(f"=== Hand {hand_id} Started ===")
        self.game_state["current_hand"] = {
            "hand_id": hand_id,
            "hole_cards": None,
            "community_cards": [],
            "actions": [],
            "pot_size": 0,
            "start_time": time.time(),
            "streets": {}
        }

    def end_hand(self, final_pot: float, hero_stack: float, result: float = 0):
        """Log the end of a hand"""
        self.logger.info(f"=== Hand {self.hand_counter} Complete ===")
        self.logger.info(f"Final pot: {final_pot}")
        self.logger.info(f"Hero stack: {hero_stack}")

        # Update win/loss record
        self.update_win_loss_record(result)

        if self.game_state["current_hand"]:
            self.game_state["current_hand"]["end_time"] = time.time()
            self.game_state["current_hand"]["final_pot"] = final_pot
            self.game_state["current_hand"]["hero_stack"] = hero_stack
            self.game_state["current_hand"]["result"] = result
            self.game_state["hands"].append(self.game_state["current_hand"])
            self.game_state["current_hand"] = None

        # Log performance metrics if in debug mode
        if self.debug_level >= DebugLevel.DEBUG:
            metrics = self.get_performance_metrics()
            self.debug(f"Performance metrics: {metrics}", DebugLevel.DEBUG)

    def log_hole_cards(self, cards: tuple):
        """Log the player's hole cards"""
        self.logger.info(f"Hole cards: {cards[0]} {cards[1]}")
        if self.game_state["current_hand"]:
            self.game_state["current_hand"]["hole_cards"] = cards

    def log_community_cards(self, street: str, cards: List[str]):
        """Log community cards for a specific street"""
        self.logger.info(f"{street} cards: {' '.join(cards)}")
        if self.game_state["current_hand"]:
            self.game_state["current_hand"]["community_cards"] = cards
            self.game_state["current_hand"]["streets"][street] = {
                "cards": cards,
                "actions": []
            }

    def log_win_probability(self, street: str, probability: float):
        """Log win probability calculation"""
        self.logger.info(f"{street} win probability: {probability:.2%}")
        if self.game_state["current_hand"] and street in self.game_state["current_hand"]["streets"]:
            self.game_state["current_hand"]["streets"][street]["win_probability"] = probability

    def log_outs_information(self, street: str, outs_count: float, outs_description: str, equity_from_outs: float):
        """Log outs information"""
        self.logger.info(f"{street} outs: {outs_count:.1f} ({outs_description})")
        self.logger.info(f"{street} equity from outs: {equity_from_outs:.2%}")
        if self.game_state["current_hand"] and street in self.game_state["current_hand"]["streets"]:
            self.game_state["current_hand"]["streets"][street]["outs_count"] = outs_count
            self.game_state["current_hand"]["streets"][street]["outs_description"] = outs_description
            self.game_state["current_hand"]["streets"][street]["equity_from_outs"] = equity_from_outs

    def log_action(self, player: str, action: str, amount: Optional[float] = None):
        """Log a player action"""
        if amount is not None:
            self.logger.info(f"{player} {action} {amount}")
        else:
            self.logger.info(f"{player} {action}")

        if self.game_state["current_hand"] and self.current_street in self.game_state["current_hand"]["streets"]:
            action_data = {
                "player": player,
                "action": action,
                "amount": amount,
                "time": time.time()
            }
            self.game_state["current_hand"]["streets"][self.current_street]["actions"].append(action_data)
            self.game_state["current_hand"]["actions"].append(action_data)

            # Log to structured JSON file
            self._log_structured_data({
                "type": "action",
                "data": action_data,
                "hand_id": self.hand_counter,
                "street": self.current_street,
                "timestamp": time.time()
            })

    def log_pot_update(self, pot_size: float):
        """Log pot size update"""
        self.logger.info(f"Pot size: {pot_size}")
        if self.game_state["current_hand"]:
            self.game_state["current_hand"]["pot_size"] = pot_size

    def start_street(self, street: str):
        """Log the start of a betting street"""
        self.current_street = street
        self.logger.info(f"=== {street} Betting Round ===")
        if self.game_state["current_hand"] and street not in self.game_state["current_hand"]["streets"]:
            self.game_state["current_hand"]["streets"][street] = {
                "actions": []
            }

    def log_blinds(self, small_blind: float, big_blind: float):
        """Log blind information"""
        self.logger.info(f"Small Blind: {small_blind}")
        self.logger.info(f"Big Blind: {big_blind}")
        if self.game_state["current_hand"]:
            self.game_state["current_hand"]["small_blind"] = small_blind
            self.game_state["current_hand"]["big_blind"] = big_blind

    def info(self, message: str):
        """Log an info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message"""
        self.logger.error(message)

    def debug(self, message: str):
        """Log a debug message"""
        self.logger.debug(message)

    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session"""
        hands_played = len(self.game_state["hands"])
        if hands_played == 0:
            return {"hands_played": 0}

        first_stack = self.game_state["hands"][0].get("hero_stack", 0)
        last_stack = self.game_state["hands"][-1].get("hero_stack", 0)

        return {
            "session_id": self.session_id,
            "hands_played": hands_played,
            "starting_stack": first_stack,
            "ending_stack": last_stack,
            "profit_loss": last_stack - first_stack,
            "duration": time.time() - self.game_state["hands"][0].get("start_time", time.time())
        }

    def _log_structured_data(self, data: Dict[str, Any]):
        """Log structured data to JSON file"""
        import json

        try:
            # Read existing data
            with open(self.json_file_path, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []

            # Append new data
            existing_data.append(data)

            # Write back to file
            with open(self.json_file_path, 'w') as f:
                json.dump(existing_data, f)
        except Exception as e:
            self.logger.error(f"Error logging structured data: {e}")

    def save_session_data(self):
        """Save structured session data to a file"""
        summary = self.get_session_summary()
        summary["hands"] = self.game_state["hands"]
        summary["performance"] = self.get_performance_metrics()
        summary["decisions"] = self.decision_history

        with open(os.path.join(self.log_dir, f"geckobot_{self.session_id}_data.json"), 'w') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Session data saved to {os.path.join(self.log_dir, f'geckobot_{self.session_id}_data.json')}")

    def debug(self, message: str, level: DebugLevel = DebugLevel.DEBUG):
        """Log a debug message at the specified level"""
        if level <= self.debug_level:
            if level == DebugLevel.ERROR:
                self.logger.error(f"DEBUG: {message}")
            elif level == DebugLevel.INFO:
                self.logger.info(f"DEBUG: {message}")
            elif level == DebugLevel.DEBUG:
                self.logger.debug(f"DEBUG: {message}")
            elif level == DebugLevel.TRACE:
                self.logger.debug(f"TRACE: {message}")

    def log_decision(self, decision_data: Dict[str, Any]):
        """Log a decision"""
        self.decision_history.append(decision_data)

        if self.debug_level >= DebugLevel.DEBUG:
            self.logger.debug(f"Decision: {decision_data['name']} - Result: {decision_data['result']}")

        # Track decision time
        if 'execution_time' in decision_data:
            self.decision_times.append(decision_data['execution_time'])

        # Track memory usage
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            self.memory_usage.append(memory_info.rss / 1024 / 1024)  # Convert to MB
        except:
            pass  # Ignore if psutil is not available

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        metrics = {
            "elapsed_time": elapsed_time,
            "hands_played": self.hand_counter,
            "hands_per_second": self.hand_counter / elapsed_time if elapsed_time > 0 else 0,
            "win_loss_record": self.win_loss_record,
            "win_rate": self.win_loss_record["wins"] / self.hand_counter if self.hand_counter > 0 else 0
        }

        # Add decision time metrics if available
        if self.decision_times:
            metrics["decision_times"] = {
                "min": min(self.decision_times),
                "max": max(self.decision_times),
                "avg": sum(self.decision_times) / len(self.decision_times),
                "total": sum(self.decision_times)
            }

        # Add memory usage metrics if available
        if self.memory_usage:
            metrics["memory_usage"] = {
                "min": min(self.memory_usage),
                "max": max(self.memory_usage),
                "avg": sum(self.memory_usage) / len(self.memory_usage),
                "current": self.memory_usage[-1] if self.memory_usage else 0
            }

        return metrics

    def set_debug_level(self, level: DebugLevel):
        """Set the debug level"""
        self.debug_level = level

        # Update log level based on debug level
        if level == DebugLevel.NONE:
            self.log_level = logging.CRITICAL
        elif level == DebugLevel.ERROR:
            self.log_level = logging.ERROR
        elif level == DebugLevel.INFO:
            self.log_level = logging.INFO
        elif level >= DebugLevel.DEBUG:
            self.log_level = logging.DEBUG

        # Update logger level
        self.logger.setLevel(self.log_level)

    def update_win_loss_record(self, result: float):
        """Update the win/loss record"""
        if result > 0:
            self.win_loss_record["wins"] += 1
        elif result < 0:
            self.win_loss_record["losses"] += 1
        else:
            self.win_loss_record["ties"] += 1

# Global logger instance
gecko_logger = None

def get_logger(log_dir: str = "logs", log_level: int = logging.INFO, debug_level: DebugLevel = DebugLevel.INFO) -> GeckoLogger:
    """Get or create the global logger instance"""
    global gecko_logger
    if gecko_logger is None:
        gecko_logger = GeckoLogger(log_dir, log_level, debug_level)
    return gecko_logger
