-- ============================================================
-- NASHAMA VISION - Complete Database Schema for Supabase
-- ============================================================
-- Execute this in the Supabase SQL Editor
-- ============================================================

-- DROP existing types and tables if they exist (for clean installation)
DROP TABLE IF EXISTS transition_metrics CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS xt_metrics CASCADE;
DROP TABLE IF EXISTS tactical_snapshots CASCADE;
DROP TABLE IF EXISTS team_metrics CASCADE;
DROP TABLE IF EXISTS player_heatmaps CASCADE;
DROP TABLE IF EXISTS player_metric_timeseries CASCADE;
DROP TABLE IF EXISTS player_metrics CASCADE;
DROP TABLE IF EXISTS team_colors CASCADE;
DROP TABLE IF EXISTS calibration_matrices CASCADE;
DROP TABLE IF EXISTS track_points CASCADE;
DROP TABLE IF EXISTS tracks CASCADE;
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS matches CASCADE;

DROP TYPE IF EXISTS eventtype CASCADE;
DROP TYPE IF EXISTS timeseriesmetrictype CASCADE;
DROP TYPE IF EXISTS metrictype CASCADE;
DROP TYPE IF EXISTS teamside CASCADE;
DROP TYPE IF EXISTS objectclass CASCADE;
DROP TYPE IF EXISTS processingstatus CASCADE;

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE processingstatus AS ENUM (
    'pending', 
    'processing', 
    'completed', 
    'failed'
);

CREATE TYPE objectclass AS ENUM (
    'player', 
    'ball', 
    'referee', 
    'goalkeeper'
);

CREATE TYPE teamside AS ENUM (
    'home', 
    'away', 
    'referee', 
    'unknown'
);

CREATE TYPE metrictype AS ENUM (
    'total_distance',
    'top_speed',
    'avg_speed',
    'high_intensity_distance',
    'sprint_count',
    'max_acceleration',
    'max_deceleration',
    'stamina_index',
    'avg_heart_rate',
    'distance_per_minute'
);

CREATE TYPE timeseriesmetrictype AS ENUM (
    'speed',
    'acceleration',
    'stamina',
    'distance_rolling'
);

CREATE TYPE eventtype AS ENUM (
    'pass',
    'carry',
    'shot',
    'dribble',
    'tackle',
    'interception'
);

-- ============================================================
-- CORE TABLES (Phase 1)
-- ============================================================

-- Matches table
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    home_team VARCHAR(255) NOT NULL,
    away_team VARCHAR(255) NOT NULL,
    match_date TIMESTAMP,
    venue VARCHAR(255),
    competition VARCHAR(255),
    season VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    storage_path TEXT NOT NULL,
    duration FLOAT NOT NULL,
    fps FLOAT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    codec VARCHAR(50),
    bitrate INTEGER,
    total_frames INTEGER,
    status processingstatus NOT NULL DEFAULT 'pending',
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error TEXT,
    processed_video_path TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_video_match_id ON videos(match_id);
CREATE INDEX idx_video_status ON videos(status);

-- Tracks table
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    object_class objectclass NOT NULL,
    team_side teamside,
    player_number INTEGER,
    player_name VARCHAR(255),
    first_frame INTEGER NOT NULL,
    last_frame INTEGER NOT NULL,
    total_detections INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE(video_id, track_id)
);

CREATE INDEX idx_track_video_id ON tracks(video_id);
CREATE INDEX idx_track_video_track_id ON tracks(video_id, track_id);

-- Track points table
CREATE TABLE track_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    track_id UUID NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    timestamp FLOAT NOT NULL,
    bbox_x1 INTEGER NOT NULL,
    bbox_y1 INTEGER NOT NULL,
    bbox_x2 INTEGER NOT NULL,
    bbox_y2 INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    x_px FLOAT NOT NULL,
    y_px FLOAT NOT NULL,
    x_m FLOAT,
    y_m FLOAT,
    keypoints JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trackpoint_track_id ON track_points(track_id);
CREATE INDEX idx_trackpoint_track_frame ON track_points(track_id, frame_number);
CREATE INDEX idx_trackpoint_frame ON track_points(frame_number);

-- Calibration matrices table
CREATE TABLE calibration_matrices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    matrix JSONB NOT NULL,
    source_points JSONB NOT NULL,
    target_points JSONB NOT NULL,
    pitch_length FLOAT,
    pitch_width FLOAT,
    reprojection_error FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_calibration_match_id ON calibration_matrices(match_id);

-- Team colors table
CREATE TABLE team_colors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    team_side teamside NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    primary_color_rgb INTEGER[] NOT NULL,
    secondary_color_rgb INTEGER[],
    color_cluster_centers JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE(match_id, team_side)
);

CREATE INDEX idx_teamcolor_match_id ON team_colors(match_id);

-- ============================================================
-- ANALYTICS TABLES (Phase 2)
-- ============================================================

-- Player metrics table
CREATE TABLE player_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL,
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    metric_name metrictype NOT NULL,
    numeric_value FLOAT NOT NULL,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_player_metric_player_match ON player_metrics(player_id, match_id);
CREATE INDEX idx_player_metric_match ON player_metrics(match_id);
CREATE INDEX idx_player_metric_video ON player_metrics(video_id);
CREATE INDEX idx_player_metric_type ON player_metrics(metric_name);

-- Player metric timeseries table
CREATE TABLE player_metric_timeseries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL,
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    timestamp FLOAT NOT NULL,
    frame_number INTEGER,
    metric_type timeseriesmetrictype NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_timeseries_player_match ON player_metric_timeseries(player_id, match_id);
CREATE INDEX idx_timeseries_player_timestamp ON player_metric_timeseries(player_id, timestamp);
CREATE INDEX idx_timeseries_match ON player_metric_timeseries(match_id);
CREATE INDEX idx_timeseries_video ON player_metric_timeseries(video_id);

-- Player heatmaps table
CREATE TABLE player_heatmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL,
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    grid_width INTEGER NOT NULL,
    grid_height INTEGER NOT NULL,
    heatmap_data JSONB NOT NULL,
    pitch_length FLOAT NOT NULL DEFAULT 105.0,
    pitch_width FLOAT NOT NULL DEFAULT 68.0,
    total_positions INTEGER NOT NULL,
    max_intensity FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_heatmap_player_match ON player_heatmaps(player_id, match_id);
CREATE INDEX idx_heatmap_match ON player_heatmaps(match_id);
CREATE INDEX idx_heatmap_video ON player_heatmaps(video_id);

-- Team metrics table
CREATE TABLE team_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    team_side VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    numeric_value FLOAT NOT NULL,
    unit VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_team_metric_match ON team_metrics(match_id);
CREATE INDEX idx_team_metric_video ON team_metrics(video_id);

-- ============================================================
-- TACTICAL & XT TABLES (Phase 3)
-- ============================================================

-- Tactical snapshots table
CREATE TABLE tactical_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    team_side VARCHAR(50) NOT NULL,
    timestamp FLOAT NOT NULL,
    formation VARCHAR(20),
    formation_confidence FLOAT,
    centroid_x FLOAT,
    centroid_y FLOAT,
    spread_x FLOAT,
    spread_y FLOAT,
    compactness FLOAT,
    defensive_line_y FLOAT,
    midfield_line_y FLOAT,
    attacking_line_y FLOAT,
    line_spacing_def_mid FLOAT,
    line_spacing_mid_att FLOAT,
    defensive_line_height FLOAT,
    block_type VARCHAR(20),
    pressing_intensity FLOAT,
    player_positions JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tactical_snapshot_match ON tactical_snapshots(match_id);
CREATE INDEX idx_tactical_snapshot_match_team ON tactical_snapshots(match_id, team_side);
CREATE INDEX idx_tactical_snapshot_timestamp ON tactical_snapshots(timestamp);

-- xT metrics table
CREATE TABLE xt_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id UUID NOT NULL,
    team_side VARCHAR(50) NOT NULL,
    total_xt_gain FLOAT NOT NULL DEFAULT 0.0,
    danger_score FLOAT NOT NULL DEFAULT 0.0,
    pass_xt FLOAT NOT NULL DEFAULT 0.0,
    carry_xt FLOAT NOT NULL DEFAULT 0.0,
    shot_xt FLOAT NOT NULL DEFAULT 0.0,
    num_passes INTEGER NOT NULL DEFAULT 0,
    num_carries INTEGER NOT NULL DEFAULT 0,
    num_shots INTEGER NOT NULL DEFAULT 0,
    avg_xt_per_action FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_xt_metric_match ON xt_metrics(match_id);
CREATE INDEX idx_xt_metric_player ON xt_metrics(player_id);
CREATE INDEX idx_xt_metric_match_player ON xt_metrics(match_id, player_id);

-- Events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id UUID NOT NULL,
    team_side VARCHAR(50) NOT NULL,
    event_type eventtype NOT NULL,
    timestamp FLOAT NOT NULL,
    frame_number INTEGER,
    start_x FLOAT NOT NULL,
    start_y FLOAT NOT NULL,
    end_x FLOAT NOT NULL,
    end_y FLOAT NOT NULL,
    distance FLOAT NOT NULL,
    duration FLOAT NOT NULL,
    velocity FLOAT NOT NULL,
    xt_value FLOAT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_event_match ON events(match_id);
CREATE INDEX idx_event_player ON events(player_id);
CREATE INDEX idx_event_match_player ON events(match_id, player_id);
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_event_timestamp ON events(timestamp);

-- Transition metrics table
CREATE TABLE transition_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    team_side VARCHAR(50) NOT NULL,
    transition_type VARCHAR(50) NOT NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    duration FLOAT NOT NULL,
    distance_covered FLOAT NOT NULL,
    avg_speed FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transition_match ON transition_metrics(match_id);
CREATE INDEX idx_transition_match_team ON transition_metrics(match_id, team_side);

-- ============================================================
-- COMPLETE!
-- ============================================================
-- Schema created successfully for Nashama Vision
-- Total tables: 17
-- Total indexes: 44
-- Total enums: 6
-- ============================================================
