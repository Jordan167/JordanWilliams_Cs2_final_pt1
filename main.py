"""
main.py
Main logic for voting system with 4-digit user ID.
Stores votes in a CSV file as user ID and vote choice (1 = John, 2 = Jane)
"""

import sys
import csv
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
from Lab1_gui import Ui_MainWindow


class VoteManager:

    def __init__(self, filename: str = "votes.csv") -> None:
        """Initilize"""
        self._filename = filename
        self._votes = {}  # key: user_id, value: 1 or 2
        self._load_votes()

    def _load_votes(self) -> None:
        """Load votes from CSV, if exists"""
        try:
            with open(self._filename, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    user_id = row.get("UserID")
                    choice = row.get("Vote")
                    if user_id and choice:
                        self._votes[user_id] = int(choice)

        except FileNotFoundError:
            self._save_votes()

        except Exception as e:
            print(f"Error loading votes: {e}")

    def _save_votes(self) -> None:
        """Save votes to CSV"""
        try:
            with open(self._filename, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["UserID", "Vote"])
                writer.writeheader()
                for user_id, choice in self._votes.items():
                    writer.writerow({"UserID": user_id, "Vote": choice})

        except Exception as e:
            print(f"Error saving votes: {e}")

    def add_vote(self, user_id: str, choice: int) -> bool:
        """Add vote if the user hasn't voted yet. Returns True if added."""
        if user_id in self._votes:
            return False
        self._votes[user_id] = choice
        self._save_votes()
        return True

    def has_voted(self, user_id: str) -> bool:
        """Check if user has already voted."""
        return user_id in self._votes

    def get_results(self) -> dict:
        """Return totals for each candidate and total votes."""
        john_votes = sum(1 for vote in self._votes.values() if vote == 1)
        jane_votes = sum(1 for vote in self._votes.values() if vote == 2)

        return {
            "John": john_votes,
            "Jane": jane_votes,
            "Total": john_votes + jane_votes
        }


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        """Initialize and start at Vote Menu page"""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.vote_manager = VoteManager()
        self.current_user_id = ""
        self.ui.stackedWidget.setCurrentIndex(0)

        # Vote menu buttons
        self.ui.vot_vote.clicked.connect(self._handle_vote_button)
        self.ui.vot_exit.clicked.connect(self._handle_exit_button)

        # Candidate menu buttons
        self.ui.can_confirm.clicked.connect(self._handle_candidate_confirm)

        # Auto-return timer (5 seconds)
        self.return_timer = QTimer()
        self.return_timer.setInterval(5000)  # 5 seconds
        self.return_timer.timeout.connect(self.return_to_vote_menu)

    def reset_radio_buttons(self) -> None:
        self.ui.can_john.setChecked(False)
        self.ui.can_jane.setChecked(False)
        self.ui.can_error_box.setText("")

    # Return after timer expires
    def return_to_vote_menu(self):
        self.return_timer.stop()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.vot_id_enter.setText("Enter User ID (Ex. 0000)")
        self.ui.vot_error_box.setText("")  
        self.current_user_id = ""

    # Vote menu
    def _handle_vote_button(self) -> None:
        user_id = self.ui.vot_id_enter.text().strip()

        # Check for 4-digit user ID
        if not (user_id.isdigit() and len(user_id) == 4):
            self.ui.vot_error_box.setText("Error: Enter a 4-digit User ID.")
            return

        if self.vote_manager.has_voted(user_id):
            self.ui.vot_error_box.setText("This User ID has already voted.")
            return

        # Go to candidate menu
        self.current_user_id = user_id
        # Cancel is automatically selected
        self.ui.can_cancel.setChecked(True)
        self.ui.can_welcome_box.setText(f"Welcome, User {user_id}! Choose your candidate or cancel.")
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.vot_error_box.setText("")

    def _handle_exit_button(self) -> None:
        self.show_results()
        self.ui.stackedWidget.setCurrentIndex(2)

    # Candidate menu
    def _handle_candidate_confirm(self) -> None:
        if self.ui.can_cancel.isChecked():
            self.ui.stackedWidget.setCurrentIndex(0)
            return
        
        # Vote choice
        choice = 1 if self.ui.can_john.isChecked() else 2

        self.vote_manager.add_vote(self.current_user_id, choice)

        self.show_results()
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.vot_id_enter.clear()

    # Results page
    def show_results(self) -> None:
        results = self.vote_manager.get_results()
        self.ui.res_john.setText(f"John - {results['John']}")
        self.ui.res_jane.setText(f"Jane - {results['Jane']}")
        self.ui.res_total.setText(f"Total - {results['Total']}")
        self.ui.res_id_box.setText(f"User ID: {self.current_user_id}")

        # Start 5 seconds and return to vote menu
        self.return_timer.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
