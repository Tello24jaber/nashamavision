"""Clean up tracks and reset video for reprocessing"""
from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
video_id = '91623b08-4a7a-41f5-a6a5-94193b195a42'

# Delete track points first (foreign key constraint)
result1 = db.execute(text(f"DELETE FROM track_points WHERE track_id IN (SELECT id FROM tracks WHERE video_id = '{video_id}')"))
print(f"Deleted {result1.rowcount} track points")

# Delete tracks
result2 = db.execute(text(f"DELETE FROM tracks WHERE video_id = '{video_id}'"))
print(f"Deleted {result2.rowcount} tracks")

# Reset video status
result3 = db.execute(text(f"UPDATE videos SET status = 'pending', processing_error = NULL WHERE id = '{video_id}'"))
print(f"Updated {result3.rowcount} video")

db.commit()
db.close()
print("Done!")
