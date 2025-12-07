"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-12-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE processingstatus AS ENUM ('pending', 'processing', 'completed', 'failed')")
    op.execute("CREATE TYPE objectclass AS ENUM ('player', 'ball', 'referee', 'goalkeeper')")
    op.execute("CREATE TYPE teamside AS ENUM ('home', 'away', 'referee', 'unknown')")
    
    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('home_team', sa.String(length=255), nullable=False),
        sa.Column('away_team', sa.String(length=255), nullable=False),
        sa.Column('match_date', sa.DateTime(), nullable=True),
        sa.Column('venue', sa.String(length=255), nullable=True),
        sa.Column('competition', sa.String(length=255), nullable=True),
        sa.Column('season', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_extension', sa.String(length=10), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('fps', sa.Float(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('codec', sa.String(length=50), nullable=True),
        sa.Column('bitrate', sa.Integer(), nullable=True),
        sa.Column('total_frames', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='processingstatus'), nullable=False),
        sa.Column('processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('processed_video_path', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_video_match_id', 'videos', ['match_id'])
    op.create_index('idx_video_status', 'videos', ['status'])
    
    # Create tracks table
    op.create_table(
        'tracks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('object_class', sa.Enum('player', 'ball', 'referee', 'goalkeeper', name='objectclass'), nullable=False),
        sa.Column('team_side', sa.Enum('home', 'away', 'referee', 'unknown', name='teamside'), nullable=True),
        sa.Column('player_number', sa.Integer(), nullable=True),
        sa.Column('player_name', sa.String(length=255), nullable=True),
        sa.Column('first_frame', sa.Integer(), nullable=False),
        sa.Column('last_frame', sa.Integer(), nullable=False),
        sa.Column('total_detections', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('video_id', 'track_id', name='uq_video_track_id')
    )
    op.create_index('idx_track_video_id', 'tracks', ['video_id'])
    op.create_index('idx_track_video_track_id', 'tracks', ['video_id', 'track_id'])
    
    # Create track_points table
    op.create_table(
        'track_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('track_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('frame_number', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.Float(), nullable=False),
        sa.Column('bbox_x1', sa.Integer(), nullable=False),
        sa.Column('bbox_y1', sa.Integer(), nullable=False),
        sa.Column('bbox_x2', sa.Integer(), nullable=False),
        sa.Column('bbox_y2', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('x_px', sa.Float(), nullable=False),
        sa.Column('y_px', sa.Float(), nullable=False),
        sa.Column('x_m', sa.Float(), nullable=True),
        sa.Column('y_m', sa.Float(), nullable=True),
        sa.Column('keypoints', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_trackpoint_track_id', 'track_points', ['track_id'])
    op.create_index('idx_trackpoint_track_frame', 'track_points', ['track_id', 'frame_number'])
    op.create_index('idx_trackpoint_frame', 'track_points', ['frame_number'])
    
    # Create calibration_matrices table
    op.create_table(
        'calibration_matrices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('matrix', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('source_points', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('target_points', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('pitch_length', sa.Float(), nullable=True),
        sa.Column('pitch_width', sa.Float(), nullable=True),
        sa.Column('reprojection_error', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_calibration_match_id', 'calibration_matrices', ['match_id'])
    
    # Create team_colors table
    op.create_table(
        'team_colors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_side', sa.Enum('home', 'away', 'referee', 'unknown', name='teamside'), nullable=False),
        sa.Column('team_name', sa.String(length=255), nullable=False),
        sa.Column('primary_color_rgb', postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column('secondary_color_rgb', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('color_cluster_centers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id', 'team_side', name='uq_match_team_side')
    )
    op.create_index('idx_teamcolor_match_id', 'team_colors', ['match_id'])


def downgrade() -> None:
    op.drop_index('idx_teamcolor_match_id', table_name='team_colors')
    op.drop_table('team_colors')
    
    op.drop_index('idx_calibration_match_id', table_name='calibration_matrices')
    op.drop_table('calibration_matrices')
    
    op.drop_index('idx_trackpoint_frame', table_name='track_points')
    op.drop_index('idx_trackpoint_track_frame', table_name='track_points')
    op.drop_index('idx_trackpoint_track_id', table_name='track_points')
    op.drop_table('track_points')
    
    op.drop_index('idx_track_video_track_id', table_name='tracks')
    op.drop_index('idx_track_video_id', table_name='tracks')
    op.drop_table('tracks')
    
    op.drop_index('idx_video_status', table_name='videos')
    op.drop_index('idx_video_match_id', table_name='videos')
    op.drop_table('videos')
    
    op.drop_table('matches')
    
    op.execute("DROP TYPE teamside")
    op.execute("DROP TYPE objectclass")
    op.execute("DROP TYPE processingstatus")
