"""add employee table

Revision ID: b6c4b3d4f5e7
Revises: 8a9caeae7366
Create Date: 2025-11-16 03:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = 'b6c4b3d4f5e7'
down_revision = '8a9caeae7366'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'employee',
        sa.Column('clerkId', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('emailAddress', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('firstName', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('lastName', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('fullName', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('imageUrl', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('accessStatus', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('organizationIds', sa.JSON(), server_default='[]', nullable=False),
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clerkId', name='uq_employee_clerk_id'),
        sa.UniqueConstraint('emailAddress', name='uq_employee_email'),
    )
    op.create_index('ix_employee_clerkId', 'employee', ['clerkId'], unique=False)
    op.create_index('ix_employee_emailAddress', 'employee', ['emailAddress'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_employee_emailAddress', table_name='employee')
    op.drop_index('ix_employee_clerkId', table_name='employee')
    op.drop_table('employee')
