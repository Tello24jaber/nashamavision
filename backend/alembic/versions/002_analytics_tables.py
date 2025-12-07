"""add analytics tables

Revision ID: 002_analytics_tables
Revises: 001_initial_schema
Create Date: 2025-12-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_analytics_tables'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE metrictype AS ENUM (
            'total_distance', 'top_speed', 'avg_speed', 
            'high_intensity_distance', 'sprint_count',
            'max_acceleration', 'max_deceleration', 
            'stamina_index', 'avg_heart_rate', 'distance_per_minute'
        )
    """)
    
    op.execute("""
        CREATE TYPE timeseriesmetrictype AS ENUM (
            'speed', 'acceleration', 'stamina', 'distance_rolling'
        )
    """)
    
    # Create player_metrics table
    op.create_table(
        'player_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.Enum(
            'total_distance', 'top_speed', 'avg_speed', 
            'high_intensity_distance', 'sprint_count',
            'max_acceleration', 'max_deceleration', 
            'stamina_index', 'avg_heart_rate', 'distance_per_minute',
            name='metrictype'
        ), nullable=False),
        sa.Column('numeric_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for player_metrics
    op.create_index('idx_player_metric_player_match', 'player_metrics', ['player_id', 'match_id'])
    op.create_index('idx_player_metric_match', 'player_metrics', ['match_id'])
    op.create_index('idx_player_metric_video', 'player_metrics', ['video_id'])
    op.create_index('idx_player_metric_type', 'player_metrics', ['metric_name'])
    
    # Create player_metric_timeseries table
    op.create_table(
        'player_metric_timeseries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.Float(), nullable=False),
        sa.Column('frame_number', sa.Integer(), nullable=True),
        sa.Column('metric_type', sa.Enum(
            'speed', 'acceleration', 'stamina', 'distance_rolling',
            name='timeseriesmetrictype'
        ), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for player_metric_timeseries
    op.create_index('idx_timeseries_player_match', 'player_metric_timeseries', ['player_id', 'match_id'])
    op.create_index('idx_timeseries_player_timestamp', 'player_metric_timeseries', ['player_id', 'timestamp'])
    op.create_index('idx_timeseries_match', 'player_metric_timeseries', ['match_id'])
    op.create_index('idx_timeseries_video', 'player_metric_timeseries', ['video_id'])
    
    # Create player_heatmaps table
    op.create_table(
        'player_heatmaps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('grid_width', sa.Integer(), nullable=False),
        sa.Column('grid_height', sa.Integer(), nullable=False),
        sa.Column('heatmap_data', postgresql.JSON(), nullable=False),
        sa.Column('pitch_length', sa.Float(), nullable=False, server_default='105.0'),
        sa.Column('pitch_width', sa.Float(), nullable=False, server_default='68.0'),
        sa.Column('total_positions', sa.Integer(), nullable=False),
        sa.Column('max_intensity', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for player_heatmaps
    op.create_index('idx_heatmap_player_match', 'player_heatmaps', ['player_id', 'match_id'])
    op.create_index('idx_heatmap_match', 'player_heatmaps', ['match_id'])
    op.create_index('idx_heatmap_video', 'player_heatmaps', ['video_id'])
    
    # Create team_metrics table
    op.create_table(
        'team_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_side', sa.String(50), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('numeric_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for team_metrics
    op.create_index('idx_team_metric_match', 'team_metrics', ['match_id'])
    op.create_index('idx_team_metric_video', 'team_metrics', ['video_id'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('team_metrics')
    op.drop_table('player_heatmaps')
    op.drop_table('player_metric_timeseries')
    op.drop_table('player_metrics')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS timeseriesmetrictype')
    op.execute('DROP TYPE IF EXISTS metrictype')
