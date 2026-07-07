"""init POS schema: tenants, users, categories, menu_items, orders, order_items

Revision ID: 0001_init
Revises:
Create Date: 2026-07-07 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = '0001_init'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts():
    return (
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def upgrade() -> None:
    role = sa.Enum('OWNER', 'CASHIER', name='userrole')
    otype = sa.Enum('DINE_IN', 'TAKEAWAY', name='ordertype')
    ostatus = sa.Enum('OPEN', 'PAID', 'VOID', name='orderstatus')
    pmethod = sa.Enum('CASH', 'QRIS', 'TRANSFER', name='paymentmethod')

    op.create_table(
        'tenants',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('address', sa.String(300), nullable=True),
        sa.Column('phone', sa.String(30), nullable=True),
        *_ts(),
    )

    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', role, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        *_ts(),
    )
    op.create_index('ix_categories_tenant_id', 'categories', ['tenant_id'])

    op.create_table(
        'menu_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', UUID(as_uuid=True), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )
    op.create_index('ix_menu_items_tenant_id', 'menu_items', ['tenant_id'])
    op.create_index('ix_menu_items_category_id', 'menu_items', ['category_id'])

    op.create_table(
        'orders',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_number', sa.String(30), nullable=True),
        sa.Column('order_type', otype, nullable=False),
        sa.Column('table_no', sa.String(20), nullable=True),
        sa.Column('status', ostatus, nullable=False),
        sa.Column('subtotal', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('total', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('payment_method', pmethod, nullable=True),
        sa.Column('paid_amount', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('change_amount', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('cashier_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        *_ts(),
    )
    op.create_index('ix_orders_tenant_id', 'orders', ['tenant_id'])

    op.create_table(
        'order_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_id', UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('menu_item_id', UUID(as_uuid=True), sa.ForeignKey('menu_items.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False, server_default='1'),
        sa.Column('line_total', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('note', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_order_items_tenant_id', 'order_items', ['tenant_id'])
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])


def downgrade() -> None:
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('menu_items')
    op.drop_table('categories')
    op.drop_table('users')
    op.drop_table('tenants')
    for e in ('paymentmethod', 'orderstatus', 'ordertype', 'userrole'):
        op.execute(f'DROP TYPE IF EXISTS {e}')
