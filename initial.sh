# python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install poetry==1.7.1
poetry install

# alembic revision --autogenerate -m "initial"
docker run -d \
        --name fastapi_app \
        -e POSTGRES_USER=nikita \
        -e POSTGRES_PASSWORD=qwerty \
        -p 38746:5432 \
        postgres:15.5

alembic upgrade head
