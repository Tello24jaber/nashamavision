-- ============================================================
-- Create Videos Table for Supabase
-- Run this in the Supabase SQL Editor
-- ============================================================

-- Create processingstatus enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE processingstatus AS ENUM (
        'pending', 
        'processing', 
        'completed', 
        'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create videos table
CREATE TABLE IF NOT EXISTS public.videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES public.matches(id) ON DELETE CASCADE,
    
    -- File Information
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    storage_path TEXT NOT NULL,
    
    -- Video Metadata
    duration FLOAT NOT NULL,
    fps FLOAT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    codec VARCHAR(50),
    bitrate INTEGER,
    total_frames INTEGER,
    
    -- Processing Status
    status processingstatus NOT NULL DEFAULT 'pending',
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error TEXT,
    processed_video_path TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
) TABLESPACE pg_default;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_video_match_id ON public.videos(match_id);
CREATE INDEX IF NOT EXISTS idx_video_status ON public.videos(status);

-- Enable Row Level Security (RLS)
ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your auth requirements)
CREATE POLICY "Allow all operations on videos" ON public.videos
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Grant permissions
GRANT ALL ON public.videos TO postgres;
GRANT ALL ON public.videos TO service_role;

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON public.videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Videos table created successfully!';
END $$;
