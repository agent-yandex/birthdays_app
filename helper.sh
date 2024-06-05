#!/bin/bash

if [[ -z $1 ]]
then
    echo "Usage:"
    echo " - $0 docker - run docker container"
    echo " - $0 install - generate venv and install packages"
    echo " - $0 database - run alembic migration"
    echo " - $0 run - run application"
    echo " - $0 all - all installation"
    echo " - $0 clean - delete docker container"
elif [[ $1 == "docker" ]]
then
    docker run -d --name birthday_db -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -p 6233:5432 postgres:15.5
elif [[ $1 == "install" ]]
then
    python3 -m venv venv
    source venv/bin/activate

    pip install poetry
    poetry install --no-root
elif [[ $1 == "database" ]]
then
    source venv/bin/activate
    alembic upgrade head
elif [[ $1 == "run" ]]
then
    source venv/bin/activate
    uvicorn app.main:app --reload --port 5100
elif [[ $1 == "all" ]]
then
    docker run -d --name birthday_db -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -p 6233:5432 postgres:15.5
    python3 -m venv venv
    source venv/bin/activate
    pip install poetry
    poetry install --no-root
    alembic upgrade head
    uvicorn app.main:app --reload --port 5100
elif [[ $1 == "clean" ]]
then
    docker stop birthday_db
    docker rm birthday_db
fi