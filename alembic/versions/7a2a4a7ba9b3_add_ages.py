"""add ages

Revision ID: 7a2a4a7ba9b3
Revises: 399a02b8d8e3
Create Date: 2017-04-14 10:26:08.616753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a2a4a7ba9b3'
down_revision = '399a02b8d8e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('age_max', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('age_min', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(), nullable=True))
    op.add_column('users', sa.Column('signup_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'signup_date')
    op.drop_column('users', 'country')
    op.drop_column('users', 'age_min')
    op.drop_column('users', 'age_max')
    # ### end Alembic commands ###
