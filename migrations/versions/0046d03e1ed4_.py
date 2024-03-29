"""empty message

Revision ID: 0046d03e1ed4
Revises:
Create Date: 2019-12-10 15:53:52.370923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0046d03e1ed4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "aadf_by_direction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("count_point_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.String(length=4), nullable=False),
        sa.Column("region_id", sa.Integer(), nullable=False),
        sa.Column("region_name", sa.String(length=50), nullable=False),
        sa.Column("local_authority_id", sa.Integer(), nullable=False),
        sa.Column(
            "local_authority_name", sa.String(length=50), nullable=False
        ),
        sa.Column("road_name", sa.String(length=100), nullable=False),
        sa.Column("road_type", sa.String(length=10), nullable=False),
        sa.Column(
            "start_junction_road_name", sa.String(length=100), nullable=True
        ),
        sa.Column(
            "end_junction_road_name", sa.String(length=100), nullable=True
        ),
        sa.Column("easting", sa.Integer(), nullable=False),
        sa.Column("northing", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("link_length_km", sa.Numeric(precision=2), nullable=True),
        sa.Column("link_length_miles", sa.Numeric(precision=2), nullable=True),
        sa.Column("estimation_method", sa.String(length=15), nullable=False),
        sa.Column(
            "estimation_method_detailed", sa.String(length=100), nullable=False
        ),
        sa.Column("direction_of_travel", sa.String(length=1), nullable=False),
        sa.Column("pedal_cycles", sa.Integer(), nullable=False),
        sa.Column("two_wheeled_motor_vehicles", sa.Integer(), nullable=False),
        sa.Column("cars_and_taxis", sa.Integer(), nullable=False),
        sa.Column("buses_and_coaches", sa.Integer(), nullable=False),
        sa.Column("lgvs", sa.Integer(), nullable=False),
        sa.Column("hgvs_2_rigid_axle", sa.Integer(), nullable=False),
        sa.Column("hgvs_3_rigid_axle", sa.Integer(), nullable=False),
        sa.Column(
            "hgvs_3_or_4_articulated_axle", sa.Integer(), nullable=False
        ),
        sa.Column("hgvs_4_or_more_rigid_axle", sa.Integer(), nullable=False),
        sa.Column("hgvs_5_articulated_axle", sa.Integer(), nullable=False),
        sa.Column("hgvs_6_articulated_axle", sa.Integer(), nullable=False),
        sa.Column("all_hgvs", sa.Integer(), nullable=False),
        sa.Column("all_motor_vehicles", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("aadf_by_direction")
    # ### end Alembic commands ###
