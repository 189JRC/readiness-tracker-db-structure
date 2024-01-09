"""Task progress table

Revision ID: cf0a8401ea3d
Revises: 6f3d93c489d8
Create Date: 2024-01-09 17:04:31.412895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf0a8401ea3d'
down_revision = '6f3d93c489d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('task_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('blocked_reason', sa.String(length=200), nullable=True),
    sa.Column('blocked_plan', sa.String(length=200), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('organisation_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('task_status_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organisation_id'], ['organisations.id'], name='fk_task_progress_organisations', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='fk_task_progress_tasks', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_status_id'], ['task_status.id'], name='fk_task_progress_task_status', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_task_progress_users', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_progress')
    op.drop_table('task_status')
    # ### end Alembic commands ###
