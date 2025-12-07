# How to Process Videos and View Heatmaps

## Quick Start

After uploading a video, you now have the video stored in Supabase. Here's how to process it and view heatmaps:

## Step 1: Process the Video

### Option A: Using the API directly

Make a POST request to process your video:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/simple-processing/process/{VIDEO_ID}"
```

Replace `{VIDEO_ID}` with your actual video ID from the database.

### Option B: Using the Frontend (You'll need to add a button)

In your VideoUpload success handler, after upload completes:

```javascript
// After successful upload
const response = await uploadApi.uploadVideo(uploadFormData);
const videoId = response.data.video_id;

// Start processing
await processingApi.processSimple(videoId);
```

## Step 2: Check Processing Status

```bash
curl "http://127.0.0.1:8000/api/v1/simple-processing/status/{VIDEO_ID}"
```

Status will be one of:
- `pending` - Not started yet
- `processing` - Currently being processed
- `completed` - Processing finished successfully
- `failed` - Processing encountered an error

## Step 3: View Heatmaps

Once processing is complete, you can fetch heatmaps:

### Get Player Heatmap
```bash
curl "http://127.0.0.1:8000/api/v1/analytics/players/{PLAYER_ID}/heatmap?match_id={MATCH_ID}"
```

### Get Match Heatmaps
```bash
curl "http://127.0.0.1:8000/api/v1/analytics/matches/{MATCH_ID}/heatmaps"
```

## What the Processing Does

The simple processing pipeline includes:

1. **Frame Extraction**: Extracts key frames from the video
2. **Object Detection**: Detects players, ball, and referees using YOLO
3. **Player Tracking**: Tracks each player across frames
4. **Heatmap Generation**: Creates spatial heatmaps showing where players moved

## Frontend Integration Example

Here's how to add a "Process Video" button to your VideoUpload page:

```jsx
const [processing, setProcessing] = useState(false);

const handleProcess = async (videoId) => {
  setProcessing(true);
  try {
    await processingApi.processSimple(videoId);
    addToast('Processing started', 'info');
    
    // Poll for status
    const checkStatus = setInterval(async () => {
      const status = await processingApi.getSimpleStatus(videoId);
      if (status.data.status === 'completed') {
        clearInterval(checkStatus);
        addToast('Processing complete!', 'success');
        navigate(`/matches/${matchId}/heatmaps`);
      } else if (status.data.status === 'failed') {
        clearInterval(checkStatus);
        addToast('Processing failed', 'error');
      }
    }, 5000); // Check every 5 seconds
    
  } catch (error) {
    addToast('Failed to start processing', 'error');
  } finally {
    setProcessing(false);
  }
};
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/simple-processing/process/{video_id}` | POST | Start video processing |
| `/api/v1/simple-processing/status/{video_id}` | GET | Get processing status |
| `/api/v1/analytics/players/{player_id}/heatmap` | GET | Get player heatmap |
| `/api/v1/analytics/matches/{match_id}/heatmaps` | GET | Get all match heatmaps |
| `/api/v1/tracks?video_id={video_id}` | GET | Get player tracks |

## Current Limitations

- Processing runs in the background but is not as robust as Celery
- Limited to 100 frames per video for demo purposes
- No real-time progress updates (check status endpoint manually)
- Requires computer vision models to be available

## Next Steps

To enable full processing with Celery/Redis:

1. Install Redis on Windows
2. Start Redis server
3. Start Celery worker: `celery -A app.workers.celery_app worker --loglevel=info`
4. Use `/api/v1/processing/start/{video_id}` instead

## Testing the Heatmap Visualization

You can test with the uploaded video:
- Video ID: Check your database `videos` table
- Match ID: Check your database `matches` table

Example:
```bash
# Get video ID from your latest upload
VIDEO_ID="1432bd53-c1bc-4dcf-8680-e6b331cb8404"
MATCH_ID="22e5d32a-e7e0-466b-b532-0d1300530d03"

# Start processing
curl -X POST "http://127.0.0.1:8000/api/v1/simple-processing/process/${VIDEO_ID}"

# Check status
curl "http://127.0.0.1:8000/api/v1/simple-processing/status/${VIDEO_ID}"

# Once complete, view heatmaps
curl "http://127.0.0.1:8000/api/v1/analytics/matches/${MATCH_ID}/heatmaps"
```
