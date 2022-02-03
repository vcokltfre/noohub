"""add initial models

Revision ID: b4968e8fda3d
Revises: 
Create Date: 2022-02-03 13:08:46.083445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b4968e8fda3d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=255), nullable=False),
        sa.Column("spec", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("banned", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "keys",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("project", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["user"], ["users.id"], name="fk_keys_users_id_user"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("keys")
    op.drop_table("users")
    op.drop_table("projects")
    # ### end Alembic commands ###