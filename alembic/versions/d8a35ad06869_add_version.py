"""add version

Revision ID: d8a35ad06869
Revises: 0cc5dea432ad
Create Date: 2017-05-16 08:31:48.454052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8a35ad06869'
down_revision = '0cc5dea432ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('version', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'version')
    # ### end Alembic commands ###