"""empty message

Revision ID: 086336241d9c
Revises: 6bd66e45a4d1
Create Date: 2022-04-28 18:27:29.042768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '086336241d9c'
down_revision = '6bd66e45a4d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cycles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cycle', sa.Integer(), nullable=True),
    sa.Column('time', sa.Time(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_cycles_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_cycles'))
    )
    with op.batch_alter_table('cycles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_cycles_cycle'), ['cycle'], unique=False)
        batch_op.create_index(batch_op.f('ix_cycles_time'), ['time'], unique=False)

    with op.batch_alter_table('medicines', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cycle_id', sa.Integer(), nullable=False))
        batch_op.drop_index('ix_medicines_cycle')
        batch_op.create_foreign_key(batch_op.f('fk_medicines_cycle_id_cycles'), 'cycles', ['cycle_id'], ['id'])
        batch_op.drop_column('cycle')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medicines', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cycle', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(batch_op.f('fk_medicines_cycle_id_cycles'), type_='foreignkey')
        batch_op.create_index('ix_medicines_cycle', ['cycle'], unique=False)
        batch_op.drop_column('cycle_id')

    with op.batch_alter_table('cycles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cycles_time'))
        batch_op.drop_index(batch_op.f('ix_cycles_cycle'))

    op.drop_table('cycles')
    # ### end Alembic commands ###
