# Lotus

A self-hosted web app to manage your Magic: The Gathering collection and decks. Written in Python using Flask and SQLAlchemy.

## Screenshots

![Deck Page](images/deck.jpeg)
![Search Page](images/search.jpeg)
![Results Page](images/results.jpeg)
![Card Page](images/card.jpeg)

## Running

**Note:** This application is not production-ready and is in an early-alpha state. Breaking changes may come down the road and security issues may arise. Run at your own risk.

### Database

For development or production, you'll need to have a MySQL database set up for the app. The following will set up a MySQL database using Docker and secure the host ports. Tested on Fedora 38. It's recommended to use a separate database for development and production if you're going to do development.

```bash
# Create a separate network for Lotus and MySQL to communicate over
docker network create --driver=bridge --attachable database

# Run the MySQL Docker container, filling in 'password' with a secure one
docker run --name lotus-mysql -e MYSQL_ROOT_PASSWORD=password -v /path/to/where/you/want/your/database:/var/lib/mysql -p 3306:3306 --network database -d mysql:8.3.0

# Block the MySQL port in the firewall for Docker containers
iptables -I DOCKER-USER -i eth0 -p tcp -m conntrack --ctorigdstport 3306 -j REJECT
```

You'll then need to create a database in your MySQL instance named "lotus" or whatever you'd like. You'll also need to set up a user named "lotus" or whatever you'd like so long as they have SELECT, INSERT, UPDATE, DELETE, REFERENCES, and CREATE permissions for that database. Update the connection string in the `.env` file accordingly. See `.env.example` for an example. The first time the application is run, the required tables and relationships will be created automatically.

```env
DATABASE_URI_DEV="mysql+pymysql://user:password@127.0.0.1:3306/database"
DATABASE_URI_PROD="mysql+pymysql://user:password@127.0.0.1:3306/database"
```

### Development

Flask has a built in development server you can run using the following command:

```bash
flask run --debug
```

### Production

A `Dockerfile` is included to run the app in Docker. The following will run the app on port 5000 using [Gunicorn](https://gunicorn.org) with 4 worker threads. Tested on Fedora 38.

**Note:** There is no account suppport for the application. This means that anyone on the network can access your application instance. Consider using something like [Nginx Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) to protect your app instance with a username and password.

```bash
# Build the Docker image
docker build --tag lotus .

# Run the Lotus Docker container
docker run --name lotus -p 5000:5000 --network database -d lotus

# Block the Lotus port for incoming, allow for outgoing
iptables -I DOCKER-USER -i eth0 -p tcp -m conntrack --ctorigdstport 5000 -j REJECT
iptables -I DOCKER-USER -o eth0 -p tcp -m conntrack --ctorigdstport 5000 -j ACCEPT
```

Since this configuration blocks the application ports, it's recommended to use [Nginx](https://www.nginx.com) as a reverse proxy to the application. Doing that also allows you to use [Certbot](https://certbot.eff.org) to protect the application with SSL.
