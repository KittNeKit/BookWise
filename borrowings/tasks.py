from datetime import date, timedelta

from celery import shared_task

from borrowings.models import Borrowing
from borrowings.notification import send_notification


@shared_task
def check_overdue_borrowings():
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True,
        expected_return_date__lte=date.today() + timedelta(days=1),
    )

    if overdue_borrowings:
        send_notification("Here some overdue borrowings!!")

        for borrowing in overdue_borrowings:
            message = (
                "Overdue borrowing: \n"
                f"Id: {borrowing.id},\n"
                f"Email: {borrowing.user_id.email},\n"
                f"Book: {borrowing.book_id.title}\n"
                f"Expected return date: {borrowing.expected_return_date}\n"
            )
            send_notification(message)
    else:
        send_notification("No borrowings overdue today!")
