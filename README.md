# Lotus

A self-hosted web app to manage your Magic: The Gathering collection and decks. Written in Python using Flask and SQLAlchemy.

## Running

### Development

Flask has a built in development server you can run. Make sure to rename the `.env.example` file to `.env` and fill it out appropriately.

```bash
flask run --debug
```

### Production

A `Dockerfile` is included to run the app in Docker. The following will run the app on port 5000. You'll need to place your SQLite database in that folder named `collection.db`.

**Note:** This is not a truly production-ready server. It should be fine for a local application but to truly deploy this application you should consider using [Gunicorn](https://gunicorn.org). There is also no account suppport for the application so anyone on the network can access your application instance. Consider using something like [Nginx Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) to lock down the app with a username and password.

```bash
docker build --tag lotus .
docker run --name lotus -v /path/to/your/sqlite/database:/database -p 5000:5000 -d lotus
```

## Importing Data

### Database Creation

There is a SQL script called `schema.sql` which creates the database tables.

### Import from MTG Goldfish

There is a utility script provided at `utilities/mtggoldfish2lotus.py` which can help migrate your MTG Goldfish CSV data to a Lotus database.
