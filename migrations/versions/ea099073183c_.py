"""empty message

Revision ID: ea099073183c
Revises: 8a9e82f772c3
Create Date: 2022-04-27 21:50:23.045598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea099073183c'
down_revision = '8a9e82f772c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medicines', schema=None) as batch_op:
        batch_op.drop_index('ix_medicines_name')
        batch_op.create_index(batch_op.f('ix_medicines_name'), ['name'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medicines', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_medicines_name'))
        batch_op.create_index('ix_medicines_name', ['name'], unique=False)

    # ### end Alembic commands ###
