"""points_matchhist

Revision ID: b2103f9f9be6
Revises: 01f9c4d67444
Create Date: 2017-05-27 16:25:39.711201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2103f9f9be6'
down_revision = '01f9c4d67444'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('match_histories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('founder_id', sa.String(), nullable=True),
    sa.Column('waiter_id', sa.String(), nullable=True),
    sa.Column('founder_speech_count', sa.Integer(),nullable=True),
    sa.Column('waiter_speech_count', sa.Integer(),nullable=True),
    sa.Column('waited_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('ended_by', sa.String(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.Column('founder_used_points', sa.Integer(), nullable=True),
    sa.Column('waiter_used_points', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('founder_id', sa.String(), nullable=True),
    sa.Column('waiter_id', sa.String(), nullable=True),
    sa.Column('founder_speech_count', sa.Integer(),default=0, nullable=True),
    sa.Column('waiter_speech_count', sa.Integer(),default=0, nullable=True),
    sa.Column('founder_used_points', sa.Integer(), nullable=True),
    sa.Column('waiter_used_points', sa.Integer(), nullable=True),
    sa.Column('waited_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matches_founder_id'), 'matches', ['founder_id'], unique=False)
    op.create_index(op.f('ix_matches_waiter_id'), 'matches', ['waiter_id'], unique=False)
    op.create_table('menu_prices',
    sa.Column('points', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('points', 'currency')
    )
    op.create_table('payment_sources',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('stripe_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('payments',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('stripe_user_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'matching_queue', sa.Column('finding_genders', sa.String(), nullable=True))
    op.add_column(u'users', sa.Column('points', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_users_fb_id'), 'users', ['fb_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_fb_id'), table_name='users')
    op.drop_column(u'users', 'points')
    op.drop_column(u'matching_queue', 'finding_genders')
    op.drop_table('payments')
    op.drop_table('payment_sources')
    op.drop_table('menu_prices')
    op.drop_index(op.f('ix_matches_waiter_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_founder_id'), table_name='matches')
    op.drop_table('matches')
    op.drop_table('match_histories')
    # ### end Alembic commands ###