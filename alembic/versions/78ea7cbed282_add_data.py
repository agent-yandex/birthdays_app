"""add_data

Revision ID: 78ea7cbed282
Revises: 5d896ea15718
Create Date: 2024-06-05 17:36:27.116633

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

from app.database.models import User


# revision identifiers, used by Alembic.
revision: str = "78ea7cbed282"
down_revision: Union[str, None] = "5d896ea15718"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

credentials = {
    "username": "test",
    "password": User.generate_hash("password"),
    "name": "test_name",
    "surname": "test_surname",
    "birthday": "2000-01-"
}


def upgrade() -> None:
    for num in range(1, 21):
        query = """
            INSERT INTO public.user(id, username, password, name, surname, birthday) VALUES
            ('{id_}', '{username}_{num}', '{password}', '{name}', '{surname}', '{birthday}{num}');
        """.format(
            id_=uuid4(),
            num=num,
            username=credentials["username"],
            password=credentials["password"],
            name=credentials["name"],
            surname=credentials["surname"],
            birthday=credentials["birthday"],
        )
        op.execute(query)


def downgrade() -> None:
    for num in range(1, 21):
        query = f"DELETE FROM public.user WHERE username = '{credentials['username']}_{num}'"
        op.execute(query)
