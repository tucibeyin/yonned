"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-28 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. PERSONS
    op.create_table(
        'persons',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_persons'))
    )
    op.create_index(op.f('ix_persons_phone'), 'persons', ['phone'], unique=True)
    op.create_index(op.f('ix_persons_email'), 'persons', ['email'], unique=True)

    # 2. ASSETS
    op.create_table(
        'assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('owner_person_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('owner_type', sa.String(length=20), server_default='business', nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('identifier', sa.String(length=100), nullable=True),
        sa.Column('qr_code', sa.String(length=100), nullable=True),
        sa.Column('current_location_asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('capacity', sa.Integer(), server_default='1', nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['assets.id'], name=op.f('fk_assets_parent_id_assets'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_person_id'], ['persons.id'], name=op.f('fk_assets_owner_person_id_persons'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['current_location_asset_id'], ['assets.id'], name=op.f('fk_assets_current_location_asset_id_assets'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_assets'))
    )
    op.create_index(op.f('ix_assets_tenant_id'), 'assets', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_assets_parent_id'), 'assets', ['parent_id'], unique=False)
    op.create_index(op.f('ix_assets_owner_person_id'), 'assets', ['owner_person_id'], unique=False)
    op.create_index(op.f('ix_assets_asset_type'), 'assets', ['asset_type'], unique=False)
    op.create_index(op.f('ix_assets_identifier'), 'assets', ['identifier'], unique=False)
    op.create_index(op.f('ix_assets_qr_code'), 'assets', ['qr_code'], unique=True)

    # 3. ASSET_SHARES (VASIF)
    op.create_table(
        'asset_shares',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('shared_with_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('can_view', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('can_edit', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('can_add', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('can_delete', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], name=op.f('fk_asset_shares_asset_id_assets'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with_person_id'], ['persons.id'], name=op.f('fk_asset_shares_shared_with_person_id_persons'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_asset_shares')),
        sa.UniqueConstraint('asset_id', 'shared_with_person_id', name='uq_asset_shares_asset_person')
    )
    op.create_index(op.f('ix_asset_shares_asset_id'), 'asset_shares', ['asset_id'], unique=False)
    op.create_index(op.f('ix_asset_shares_shared_with_person_id'), 'asset_shares', ['shared_with_person_id'], unique=False)

    # 4. PROCESS_DEFINITIONS
    op.create_table(
        'process_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('is_instant', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('default_location_type', sa.String(length=50), nullable=True),
        sa.Column('is_customer_visible', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('customer_label', sa.String(length=255), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('metadata_schema', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_process_definitions'))
    )
    op.create_index(op.f('ix_process_definitions_tenant_id'), 'process_definitions', ['tenant_id'], unique=False)

    # 4.1 PROCESS_DEFINITION_RELATIONS
    op.create_table(
        'process_definition_relations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('parent_definition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_definition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_optional', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.ForeignKeyConstraint(['parent_definition_id'], ['process_definitions.id'], name=op.f('fk_process_definition_relations_parent_definition_id_process_definitions'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['child_definition_id'], ['process_definitions.id'], name=op.f('fk_process_definition_relations_child_definition_id_process_definitions'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_process_definition_relations'))
    )

    # 5. ASSET_SESSIONS (Geçici Zilyetlik & Check-in)
    op.create_table(
        'asset_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('branch_asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subject_asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='checked_in', nullable=False),
        sa.Column('current_location_asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tracking_token', sa.String(length=100), nullable=False),
        sa.Column('check_in_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('check_out_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['branch_asset_id'], ['assets.id'], name=op.f('fk_asset_sessions_branch_asset_id_assets'), ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['subject_asset_id'], ['assets.id'], name=op.f('fk_asset_sessions_subject_asset_id_assets'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['current_location_asset_id'], ['assets.id'], name=op.f('fk_asset_sessions_current_location_asset_id_assets'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_asset_sessions'))
    )
    op.create_index(op.f('ix_asset_sessions_tenant_id'), 'asset_sessions', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_asset_sessions_subject_asset_id'), 'asset_sessions', ['subject_asset_id'], unique=False)
    op.create_index(op.f('ix_asset_sessions_status'), 'asset_sessions', ['status'], unique=False)
    op.create_index(op.f('ix_asset_sessions_tracking_token'), 'asset_sessions', ['tracking_token'], unique=True)

    # 6. LIVE_PROCESSES
    op.create_table(
        'live_processes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('definition_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('previous_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('is_instant', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='queued', nullable=False),
        sa.Column('location_asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_person_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('completed_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('is_customer_visible', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('customer_notes', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('photos', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['asset_sessions.id'], name=op.f('fk_live_processes_session_id_asset_sessions'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['definition_id'], ['process_definitions.id'], name=op.f('fk_live_processes_definition_id_process_definitions'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['live_processes.id'], name=op.f('fk_live_processes_parent_id_live_processes'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['previous_id'], ['live_processes.id'], name=op.f('fk_live_processes_previous_id_live_processes'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['location_asset_id'], ['assets.id'], name=op.f('fk_live_processes_location_asset_id_assets'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_person_id'], ['persons.id'], name=op.f('fk_live_processes_assigned_person_id_persons'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['completed_by_id'], ['persons.id'], name=op.f('fk_live_processes_completed_by_id_persons'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_live_processes'))
    )
    op.create_index(op.f('ix_live_processes_session_id'), 'live_processes', ['session_id'], unique=False)
    op.create_index(op.f('ix_live_processes_status'), 'live_processes', ['status'], unique=False)

    # 6.1 LIVE_PROCESS_OPERATORS
    op.create_table(
        'live_process_operators',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('process_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='operator', nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['process_id'], ['live_processes.id'], name=op.f('fk_live_process_operators_process_id_live_processes'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], name=op.f('fk_live_process_operators_person_id_persons'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_live_process_operators'))
    )

    # 7. PROCESS_CONSUMABLES (Sarf & İlaç)
    op.create_table(
        'process_consumables',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('process_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('consumable_asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('custom_name', sa.String(length=150), nullable=True),
        sa.Column('barcode_scanned', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), server_default='1.0', nullable=False),
        sa.Column('unit', sa.String(length=20), server_default='adet', nullable=False),
        sa.Column('administered_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['process_id'], ['live_processes.id'], name=op.f('fk_process_consumables_process_id_live_processes'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['consumable_asset_id'], ['assets.id'], name=op.f('fk_process_consumables_consumable_asset_id_assets'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['administered_by_id'], ['persons.id'], name=op.f('fk_process_consumables_administered_by_id_persons'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_process_consumables'))
    )
    op.create_index(op.f('ix_process_consumables_process_id'), 'process_consumables', ['process_id'], unique=False)
    op.create_index(op.f('ix_process_consumables_barcode_scanned'), 'process_consumables', ['barcode_scanned'], unique=False)


def downgrade() -> None:
    op.drop_table('process_consumables')
    op.drop_table('live_process_operators')
    op.drop_table('live_processes')
    op.drop_table('asset_sessions')
    op.drop_table('process_definition_relations')
    op.drop_table('process_definitions')
    op.drop_table('asset_shares')
    op.drop_table('assets')
    op.drop_table('persons')
