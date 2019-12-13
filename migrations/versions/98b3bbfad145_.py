"""empty message

Revision ID: 98b3bbfad145
Revises: 7134a7f940f8
Create Date: 2019-12-13 11:09:53.195072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98b3bbfad145'
down_revision = '7134a7f940f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_aadf_by_direction_count_point_id'), 'aadf_by_direction', ['count_point_id'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_direction_of_travel'), 'aadf_by_direction', ['direction_of_travel'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_estimation_method'), 'aadf_by_direction', ['estimation_method'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_estimation_method_detailed'), 'aadf_by_direction', ['estimation_method_detailed'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_local_authority_id'), 'aadf_by_direction', ['local_authority_id'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_local_authority_name'), 'aadf_by_direction', ['local_authority_name'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_point'), 'aadf_by_direction', ['point'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_region_id'), 'aadf_by_direction', ['region_id'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_region_name'), 'aadf_by_direction', ['region_name'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_road_name'), 'aadf_by_direction', ['road_name'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_road_type'), 'aadf_by_direction', ['road_type'], unique=False)
    op.create_index(op.f('ix_aadf_by_direction_year'), 'aadf_by_direction', ['year'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_aadf_by_direction_year'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_road_type'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_road_name'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_region_name'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_region_id'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_point'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_local_authority_name'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_local_authority_id'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_estimation_method_detailed'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_estimation_method'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_direction_of_travel'), table_name='aadf_by_direction')
    op.drop_index(op.f('ix_aadf_by_direction_count_point_id'), table_name='aadf_by_direction')
    # ### end Alembic commands ###