"""
Clean tracks and reprocess video with improved SORT tracking
This will delete old fragmented tracks and create new persistent ones
"""
import psycopg2
import os

# Database connection - use direct connection
DB_URL = "postgresql://postgres.zjsyuuaryyhdelyxnubm:S%40sha1234@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

def clean_and_reprocess():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    video_id = "91623b08-4a7a-41f5-a6a5-94193b195a42"
    
    print(f"Cleaning tracks for video {video_id}...")
    
    # Delete all track points
    cur.execute("""
        DELETE FROM track_points 
        WHERE track_id IN (
            SELECT id FROM tracks WHERE video_id = %s
        )
    """, (video_id,))
    deleted_points = cur.rowcount
    print(f"Deleted {deleted_points} track points")
    
    # Delete all tracks
    cur.execute("DELETE FROM tracks WHERE video_id = %s", (video_id,))
    deleted_tracks = cur.rowcount
    print(f"Deleted {deleted_tracks} tracks")
    
    # Reset video status to uploaded
    cur.execute("""
        UPDATE videos 
        SET status = 'uploaded',
            processing_started_at = NULL,
            processing_completed_at = NULL
        WHERE id = %s
    """, (video_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n✅ Database cleaned successfully!")
    print(f"\nNext steps:")
    print(f"1. Backend should be running with updated SORT parameters")
    print(f"2. Run: Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/simple-processing/process/{video_id}' -Method POST")
    print(f"\nNew tracking parameters:")
    print(f"  - max_age: 150 frames (5 seconds @ 30fps)")
    print(f"  - min_hits: 1 (immediate tracking)")
    print(f"  - iou_threshold: 0.15 (very permissive)")
    print(f"  - confidence: 0.15 (detect all players)")
    print(f"  - Processing: ~15 fps for continuous tracking")

if __name__ == "__main__":
    clean_and_reprocess()
