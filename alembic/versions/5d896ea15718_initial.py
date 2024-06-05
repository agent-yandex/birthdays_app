"""initial

Revision ID: 5d896ea15718
Revises: 
Create Date: 2024-06-05 17:35:36.991091

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d896ea15718"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("surname", sa.String(length=20), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="username_unique"),
    )
    op.create_index(
        "hash_index_username",
        "user",
        ["username"],
        unique=False,
        postgresql_using="hash",
    )
    op.create_table(
        "subscription",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("user_sub_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_sub_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "user_sub_id", name="user_id_subscription_id_unique"
        ),
    )
    op.create_index(
        "hash_index_user_id",
        "subscription",
        ["user_id"],
        unique=False,
        postgresql_using="hash",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "hash_index_user_id",
        table_name="subscription",
        postgresql_using="hash",
    )
    op.drop_table("subscription")
    op.drop_index(
        "hash_index_username", table_name="user", postgresql_using="hash"
    )
    op.drop_table("user")
    # ### end Alembic commands ###
