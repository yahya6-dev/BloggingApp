"""second-migration1

Revision ID: 817de41942fc
Revises: aa724ef2f105
Create Date: 2021-12-04 15:40:04.409248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '817de41942fc'
down_revision = 'aa724ef2f105'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('replies', sa.Column('timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('replies', 'timestamp')
    # ### end Alembic commands ###
