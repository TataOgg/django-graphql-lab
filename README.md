# django-graphql-lab

Installation guide

* Install docker: https://docs.docker.com/engine/install/
* Install docker-compose: https://docs.docker.com/compose/install/
* Build images: 
`docker-compose build`
* Run as daemon: 
`docker-compose up -d`
* Alternativelly you can run only the postgres instance, removing the comment in the docker-compose file and running: 
`docker-compose up -d db`
* You can also run the web and connect it to other ddbb: 
`docker-compose up -d web`
or
`python manage.py runserver`

Only the local dev setting is offered as an example.

Then run 127.0.0.1:8000 and check if it's working.
