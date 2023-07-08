import stripe

from borrowings.models import Borrowing
from library_project.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY
FINE_MULTIPLIER = 2


def create_stripe_session(
        borrowing: Borrowing,
        is_fine: bool,
):
    total_price = (
                          borrowing.expected_return_date - borrowing.borrow_date
                  ).days * borrowing.book_id.daily_fee

    text = "Borrowing"

    if is_fine:
        overdue = borrowing.actual_return_date - borrowing.expected_return_date
        total_price = overdue.days * float(borrowing.book_id.daily_fee) * FINE_MULTIPLIER
        text = "Fine "

    url = "http://127.0.0.1:8000/api/borrowings/borrowings/" + str(borrowing.id)
    stripe_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{text} of {borrowing.book_id.title} by {borrowing.user_id}"
                    },
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            },
        ],
        mode="payment",
        success_url=url + "/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=url + "/cancel?session_id={CHECKOUT_SESSION_ID}",
    )

    return stripe_session
