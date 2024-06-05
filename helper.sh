if [[ -z $1 ]]
then
    echo "Usage:"
    echo "$0 docker - run docker container"
    echo "$0 install - generate venv and install packages"
    echo "$0 database - run alembic migration"
    echo "$0 run - run application"
elif [[ $1 == "docker" ]]
then
    docker run -d --name fastapi_app -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -p 6233:5432 postgres:15.5
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
fi