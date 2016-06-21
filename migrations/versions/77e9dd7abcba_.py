"""empty message

Revision ID: 77e9dd7abcba
Revises: f400973784d6
Create Date: 2016-06-21 21:20:02.396362

"""

# revision identifiers, used by Alembic.
revision = '77e9dd7abcba'
down_revision = 'f400973784d6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('verify', sa.String(length=256), nullable=False))
    op.create_index(op.f('ix_project_verify'), 'project', ['verify'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_project_verify'), table_name='project')
    op.drop_column('project', 'verify')
    ### end Alembic commands ###
