# django-graphql-lab

## Installation guide

* Install docker: https://docs.docker.com/engine/install/
* Install docker-compose: https://docs.docker.com/compose/install/
* Build images: 
`docker-compose build`
* Run as daemon: 
`docker-compose up -d`
* Alternativelly you can run only the postgres instance, acceding by the 5432 port: 
`docker-compose up -d db`
* You can also run the web and connect it to other ddbb changing the settings: 
`docker-compose up -d web`
or
`python manage.py runserver`
* It is possible that you should run `python manage.py migrate` in order to generate the db tables.

Then run 127.0.0.1:8000 and check if it's working.

The .env.dev setting is offered as a working example for the docker full run.

The .env.local setting is offered as a working example for only the db running on docker.


## Requests compilation 
A Har file with a compilation of the queries and mutation is available in the project.
You could export it to your graphQL client.

## Dummy data in db
You could use `django manage.py seed <app> --number <number of dummy data generated>` 
for populating the database with fake data
 
## Login
The login is made in the tokenAuth mutation. 
The token provided should be set in the headers of the request as:
`Authorization: JWT <token>`
The user must be verified in order to make requests.
You can force the verification directly in your db 
or copy the verification token shown in console. And user the verifyUser mutation.