import requests

from borrowings.models import Borrowing
from library_project.settings import TELEGRAM_TOKEN, CHAT_ID
from user.models import User


def send_notification(message: str) -> None:
    """
    Sends a message to admin
    """
    if CHAT_ID:
        url = (
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
            f"sendMessage?chat_id={CHAT_ID}&text={message}"
        )
        requests.get(url)


def send_borrowing_create_message(
        user: User, borrowing: Borrowing
) -> None:
    """Sends a message while creating a borrowing with detailed info"""
    message = (
        f"New borrowing created by {user.email}: \n"
        f"Book: {borrowing.book_id.title}, \n"
        f"book left: {borrowing.book_id.inventory}, \n"
        f"Expected return date: {borrowing.expected_return_date}."

    )
    send_notification(message)
