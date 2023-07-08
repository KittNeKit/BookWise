# Library system API
API service for library management written on DRF

## Features

- JWT authenticated
- CRUD functionality for Books Service 
- CRUD for Users Service
- Telegram notification!
- Notification for admin about new borrowing or new payment paid
- Executes every-day task for monitoring overdue borrowings.
- Return book functionality
- Automatically create fine payment if user returned a book after expected return date.
- Documentation is located at /api/doc/swagger/


## Installing using GitHub:
Install PostgresSQL and create db

1. Clone the repository:

```bash
git clone https://github.com/your-username/library-project
```
2. Change to the project's directory:
```bash
cd library-project
```
3. Сopy .env_sample file with your examples of env variables to your .env
file

don't forget to [create your Stripe account](https://stripe.com/en-gb-us) and get your bot token in [BotFather](https://t.me/botfather)

4. Once you're in the desired directory, run the following command to create a virtual environment:
```bash
python -m venv venv
```
5. Activate the virtual environment:

On macOS and Linux:

```bash
source venv/bin/activate
```
On Windows:
```bash
venv\Scripts\activate
```

4. Install the dependencies

```bash
pip install -r requirements.txt
```

5. Set up the database:

Run the migrations

```bash
python manage.py migrate
```

6. Use the following command to load prepared data from fixture to test:
```bash
python manage.py loaddata fixture_data.json
```

7. Start the development server

```bash
python manage.py runserver
```

8. Access the website locally at http://localhost:8000.

## Run with Docker

Docker should be installed

```
docker-compose build
docker-compose up
```

## Getting access

 
- get access token via /api/user/token/ by 
```
email = user@test.com
password = user123123
```

or register you own user via /api/users/ and get access token
