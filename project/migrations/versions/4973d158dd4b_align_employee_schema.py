"""align employee schema

Revision ID: 4973d158dd4b
Revises: b6c4b3d4f5e7
Create Date: 2025-11-16 17:11:11.107069

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4973d158dd4b'
down_revision = 'b6c4b3d4f5e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'employee',
        sa.Column(
            'tareas_asignadas',
            sa.JSON(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        'employee',
        sa.Column(
            'estado',
            sqlmodel.sql.sqltypes.AutoString(),
            server_default='pendiente',
            nullable=False,
        ),
    )
    op.drop_index('ix_employee_emailAddress', table_name='employee')
    op.drop_constraint('uq_employee_clerk_id', 'employee', type_='unique')
    op.drop_constraint('uq_employee_email', 'employee', type_='unique')
    op.drop_constraint('employee_pkey', 'employee', type_='primary')
    op.drop_column('employee', 'firstName')
    op.drop_column('employee', 'role')
    op.drop_column('employee', 'emailAddress')
    op.drop_column('employee', 'accessStatus')
    op.drop_column('employee', 'lastName')
    op.drop_column('employee', 'id')
    op.drop_column('employee', 'updatedAt')
    op.drop_column('employee', 'imageUrl')
    op.drop_column('employee', 'fullName')
    op.drop_column('employee', 'organizationIds')
    op.drop_column('employee', 'createdAt')
    op.create_primary_key('employee_pkey', 'employee', ['clerkId'])

    op.drop_column('service', 'description')
    op.drop_column('service', 'rating')


def downgrade() -> None:
    op.add_column('service', sa.Column('rating', postgresql.DOUBLE_PRECISION(precision=53), nullable=False))
    op.add_column('service', sa.Column('description', sa.VARCHAR(), nullable=True))

    op.drop_constraint('employee_pkey', 'employee', type_='primary')
    op.add_column('employee', sa.Column('createdAt', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column(
        'employee',
        sa.Column(
            'organizationIds',
            postgresql.JSON(astext_type=sa.Text()),
            server_default=sa.text("'[]'::json"),
            nullable=False,
        ),
    )
    op.add_column('employee', sa.Column('fullName', sa.VARCHAR(), nullable=True))
    op.add_column('employee', sa.Column('imageUrl', sa.VARCHAR(), nullable=True))
    op.add_column('employee', sa.Column('updatedAt', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('employee', sa.Column('id', sa.VARCHAR(), nullable=False))
    op.add_column('employee', sa.Column('lastName', sa.VARCHAR(), nullable=True))
    op.add_column('employee', sa.Column('accessStatus', sa.VARCHAR(), nullable=False))
    op.add_column('employee', sa.Column('emailAddress', sa.VARCHAR(), nullable=False))
    op.add_column('employee', sa.Column('role', sa.VARCHAR(), nullable=False))
    op.add_column('employee', sa.Column('firstName', sa.VARCHAR(), nullable=True))
    op.create_index('ix_employee_emailAddress', 'employee', ['emailAddress'], unique=False)
    op.create_unique_constraint('uq_employee_email', 'employee', ['emailAddress'])
    op.create_unique_constraint('uq_employee_clerk_id', 'employee', ['clerkId'])
    op.create_primary_key('employee_pkey', 'employee', ['id'])
    op.drop_column('employee', 'estado')
    op.drop_column('employee', 'tareas_asignadas')
