"""
Phase 3: Tactical Analysis, xT, and Event Detection

Revision ID: 003_phase3_tables
Revises: 002_analytics_tables
Create Date: 2024-12-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '003_phase3_tables'
down_revision = '002_analytics_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Phase 3 tables"""
    
    # Create EventType enum
    event_type_enum = postgresql.ENUM(
        'pass', 'carry', 'shot', 'dribble', 'tackle', 'interception',
        name='eventtype',
        create_type=True
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)
    
    # ========================================================================
    # 1. TacticalSnapshot Table
    # ========================================================================
    op.create_table(
        'tactical_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('team_side', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.Float, nullable=False),
        
        # Formation
        sa.Column('formation', sa.String(20), nullable=True),
        sa.Column('formation_confidence', sa.Float, nullable=True),
        
        # Positioning
        sa.Column('centroid_x', sa.Float, nullable=True),
        sa.Column('centroid_y', sa.Float, nullable=True),
        sa.Column('spread_x', sa.Float, nullable=True),
        sa.Column('spread_y', sa.Float, nullable=True),
        sa.Column('compactness', sa.Float, nullable=True),
        
        # Lines
        sa.Column('defensive_line_y', sa.Float, nullable=True),
        sa.Column('midfield_line_y', sa.Float, nullable=True),
        sa.Column('attacking_line_y', sa.Float, nullable=True),
        sa.Column('line_spacing_def_mid', sa.Float, nullable=True),
        sa.Column('line_spacing_mid_att', sa.Float, nullable=True),
        
        # Defensive metrics
        sa.Column('defensive_line_height', sa.Float, nullable=True),
        sa.Column('block_type', sa.String(20), nullable=True),
        
        # Pressing
        sa.Column('pressing_intensity', sa.Float, nullable=True),
        
        # Player positions
        sa.Column('player_positions', postgresql.JSON, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )
    
    # Indexes for tactical_snapshots
    op.create_index('idx_tactical_snapshot_match', 'tactical_snapshots', ['match_id'])
    op.create_index('idx_tactical_snapshot_match_team', 'tactical_snapshots', ['match_id', 'team_side'])
    op.create_index('idx_tactical_snapshot_timestamp', 'tactical_snapshots', ['timestamp'])
    
    # ========================================================================
    # 2. XTMetric Table
    # ========================================================================
    op.create_table(
        'xt_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_side', sa.String(50), nullable=False),
        
        # xT Summary
        sa.Column('total_xt_gain', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('danger_score', sa.Float, nullable=False, server_default='0.0'),
        
        sa.Column('pass_xt', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('carry_xt', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('shot_xt', sa.Float, nullable=False, server_default='0.0'),
        
        sa.Column('num_passes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('num_carries', sa.Integer, nullable=False, server_default='0'),
        sa.Column('num_shots', sa.Integer, nullable=False, server_default='0'),
        
        sa.Column('avg_xt_per_action', sa.Float, nullable=False, server_default='0.0'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Indexes for xt_metrics
    op.create_index('idx_xt_metric_match', 'xt_metrics', ['match_id'])
    op.create_index('idx_xt_metric_player', 'xt_metrics', ['player_id'])
    op.create_index('idx_xt_metric_match_player', 'xt_metrics', ['match_id', 'player_id'])
    
    # ========================================================================
    # 3. Events Table
    # ========================================================================
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_side', sa.String(50), nullable=False),
        
        sa.Column('event_type', event_type_enum, nullable=False),
        sa.Column('timestamp', sa.Float, nullable=False),
        sa.Column('frame_number', sa.Integer, nullable=True),
        
        # Spatial data
        sa.Column('start_x', sa.Float, nullable=False),
        sa.Column('start_y', sa.Float, nullable=False),
        sa.Column('end_x', sa.Float, nullable=False),
        sa.Column('end_y', sa.Float, nullable=False),
        
        # Event metrics
        sa.Column('distance', sa.Float, nullable=False),
        sa.Column('duration', sa.Float, nullable=False),
        sa.Column('velocity', sa.Float, nullable=False),
        
        # xT value
        sa.Column('xt_value', sa.Float, nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSON, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )
    
    # Indexes for events
    op.create_index('idx_event_match', 'events', ['match_id'])
    op.create_index('idx_event_player', 'events', ['player_id'])
    op.create_index('idx_event_match_player', 'events', ['match_id', 'player_id'])
    op.create_index('idx_event_type', 'events', ['event_type'])
    op.create_index('idx_event_timestamp', 'events', ['timestamp'])
    
    # ========================================================================
    # 4. TransitionMetric Table
    # ========================================================================
    op.create_table(
        'transition_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('match_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('matches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('team_side', sa.String(50), nullable=False),
        
        sa.Column('transition_type', sa.String(50), nullable=False),
        
        sa.Column('start_time', sa.Float, nullable=False),
        sa.Column('end_time', sa.Float, nullable=False),
        sa.Column('duration', sa.Float, nullable=False),
        
        sa.Column('distance_covered', sa.Float, nullable=False),
        sa.Column('avg_speed', sa.Float, nullable=False),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )
    
    # Indexes for transition_metrics
    op.create_index('idx_transition_match', 'transition_metrics', ['match_id'])
    op.create_index('idx_transition_match_team', 'transition_metrics', ['match_id', 'team_side'])


def downgrade() -> None:
    """Drop Phase 3 tables"""
    
    # Drop tables
    op.drop_table('transition_metrics')
    op.drop_table('events')
    op.drop_table('xt_metrics')
    op.drop_table('tactical_snapshots')
    
    # Drop enum
    event_type_enum = postgresql.ENUM(name='eventtype')
    event_type_enum.drop(op.get_bind(), checkfirst=True)
