"""Add blocked suggestions

Revision ID: a2a4385fe7ce
Revises: cf0a8401ea3d
Create Date: 2024-01-09 17:19:05.385873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2a4385fe7ce'
down_revision = 'cf0a8401ea3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blocked_suggestions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('date_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='fk_blocked_suggestions_tasks', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blocked_suggestions')
    # ### end Alembic commands ###