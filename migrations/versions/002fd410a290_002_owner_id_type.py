"""empty message

Revision ID: 002fd410a290
Revises: 0f5345ccf2a5
Create Date: 2019-02-05 13:40:59.112652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002fd410a290'
down_revision = '0f5345ccf2a5'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE "owner" DROP CONSTRAINT "owner_pkey" CASCADE')
    op.alter_column('owner', 'identity', existing_type=sa.Integer(), type_=sa.String())
    op.alter_column('title', 'owner_identity', existing_type=sa.Integer(), type_=sa.String())
    op.create_primary_key('owner_pkey', 'owner', ['identity'])


def downgrade():
    op.execute('ALTER TABLE "owner" DROP CONSTRAINT "owner_pkey" CASCADE')    
    op.alter_column('owner', 'identity', existing_type=sa.String(), type_=sa.Integer(), postgresql_using="identity::integer", autoincrement=True)
    op.alter_column('title', 'owner_identity', existing_type=sa.String(), type_=sa.Integer(), postgresql_using="identity::integer", autoincrement=True)
    op.create_primary_key('owner_pkey', 'owner', ['identity'])
