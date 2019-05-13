# Dinner Project App

[The Dinner Project](http://dinnerproject.xyz/) was started in 2013 by a Penn grad who wanted to encourage students who didn't know one another to eat meals together. This app is meant to facilitate the logistics of such dinners, so any Penn student can log on and host or attend a dinner with a group of random students. 

The personal goal of the project was to get familiar with production-level Flask strategies and best practices, including robust error handling and email notifications.

This is an independent study (CIS599) for Penn's MCIT program. It was advised by Dr. Swapneel Sheth and Dr. Chris Murphy.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You will need the following software to run this app

```
Python 3.7.0
```
```
Flask 1.0.2
```

### Installing

Once you have Python and Flask installed, run the following commands to bootstrap your environment
```
git clone https://github.com/naomipohl/dinner-project-app.git
cd dinner-project-app
```

Create a virtual environment by installing a third-party tool called [virtualenv](https://virtualenv.pypa.io/en/latest/)
```
virtualenv venv
```

Activate your virtual environment and install requirements
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You will need to create a [Cloudinary](https://cloudinary.com/) account and replace the API variables in config.py, as well as create .env file in the root directory that looks like this (this setup is for GMail; you can use an email server of your choice):

```
SECRET_KEY=<your-secret-key>
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=<your-gmail-username>
MAIL_PASSWORD=<your-gmail-password>
CLOUDINARY_CLOUD_NAME=<your-cloudinary-cloud-name>
CLOUDINARY_API_KEY=<your-cloudinary-api-key>
CLOUDINARY_API_SECRET=<your-cloudinary-api-secret>
```

Run the following commands to create the app's database tables and perform the initial migration
```
flask db init
flask db migrate
flask db upgrade
```

Finally, set the flask app name
```
FLASK_APP=app.py
```

Now you can run the app locally!
```
flask run
```

## Deployment

The [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) makes deployment a piece of cake. Once you have updated your Github repository, simply run

```
git push heroku master
```

See a live version of the app [here](https://dinnerproject2.herokuapp.com/)

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [Heroku](https://www.heroku.com/) - Cloud application platform

## Authors

* **Naomi Pohl**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
* [Dr. Swapneel Sheth](https://www.cis.upenn.edu/~swapneel/)
* [Dr. Chris Murphy](http://www.cis.upenn.edu/~cdmurphy/)
