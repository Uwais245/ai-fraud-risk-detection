"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-09-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.Enum('admin', 'business_manager', 'analyst', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('bin_country', sa.String(length=100), nullable=True),
        sa.Column('channel', sa.Enum('web', 'mobile', 'api', 'pos', name='transactionchannel'), nullable=False, default='web'),
        sa.Column('merchant_category', sa.String(length=100), nullable=True),
        sa.Column('promo_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('avs_match', sa.Boolean(), nullable=False, default=True),
        sa.Column('cvv_result', sa.Boolean(), nullable=False, default=True),
        sa.Column('three_ds_flag', sa.Boolean(), nullable=False, default=False),
        sa.Column('shipping_distance_km', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('account_age_days', sa.Integer(), nullable=True),
        sa.Column('total_transactions_user', sa.Integer(), nullable=True),
        sa.Column('avg_amount_user', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('device_id', sa.String(length=100), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('is_fraud', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index(op.f('ix_transactions_customer_created'), 'transactions', ['customer_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_transactions_device_created'), 'transactions', ['device_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_transactions_ip_created'), 'transactions', ['ip_address', 'created_at'], unique=False)
    op.create_index(op.f('ix_transactions_amount_created'), 'transactions', ['amount', 'created_at'], unique=False)
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_id'), 'transactions', ['transaction_id'], unique=True)
    op.create_index(op.f('ix_transactions_is_fraud'), 'transactions', ['is_fraud'], unique=False)

    # Create risk_assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(length=50), nullable=False),
        sa.Column('ml_anomaly_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('rule_engine_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('customer_behavior_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('final_risk_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('risk_level', sa.String(length=10), nullable=False),
        sa.Column('decision', sa.String(length=20), nullable=False),
        sa.Column('risk_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('ai_explanation', sa.Text(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_assessments_transaction_id'), 'risk_assessments', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_risk_assessments_assessed_at'), 'risk_assessments', ['assessed_at'], unique=False)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alertseverity'), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('NEW', 'INVESTIGATING', 'CONFIRMED_FRAUD', 'FALSE_POSITIVE', 'RESOLVED', name='alertstatus'), nullable=False, default='NEW'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('risk_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('ai_explanation', sa.Text(), nullable=True),
        sa.Column('investigation_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_transaction_id'), 'alerts', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_alerts_status'), 'alerts', ['status'], unique=False)
    op.create_index(op.f('ix_alerts_created_at'), 'alerts', ['created_at'], unique=False)

    # Create rules table
    op.create_table(
        'rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('condition', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('risk_increase', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rules_id'), 'rules', ['id'], unique=False)

    # Create customer_risk_profiles table
    op.create_table(
        'customer_risk_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.String(length=50), nullable=False),
        sa.Column('risk_level', sa.String(length=10), nullable=False, default='LOW'),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=False, default=0),
        sa.Column('total_transactions', sa.Integer(), nullable=False, default=0),
        sa.Column('suspicious_transactions', sa.Integer(), nullable=False, default=0),
        sa.Column('devices_used', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('ips_used', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('locations_used', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('previous_fraud_reports', sa.Integer(), nullable=False, default=0),
        sa.Column('last_transaction_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_id')
    )
    op.create_index(op.f('ix_customer_risk_profiles_customer_id'), 'customer_risk_profiles', ['customer_id'], unique=True)
    op.create_index(op.f('ix_customer_risk_profiles_id'), 'customer_risk_profiles', ['id'], unique=False)

    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(length=50), nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=True),
        sa.Column('feedback_type', sa.Enum('CONFIRMED_FRAUD', 'FALSE_POSITIVE', name='feedbacktype'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('submitted_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_id'), 'feedback', ['id'], unique=False)
    op.create_index(op.f('ix_feedback_transaction_id'), 'feedback', ['transaction_id'], unique=False)


def downgrade() -> None:
    op.drop_table('feedback')
    op.drop_table('customer_risk_profiles')
    op.drop_table('rules')
    op.drop_table('alerts')
    op.drop_table('risk_assessments')
    op.drop_table('transactions')
    op.drop_table('users')