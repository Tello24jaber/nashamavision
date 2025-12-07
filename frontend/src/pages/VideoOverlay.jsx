/**
 * Video Overlay View
 * Plays the video with player detection boxes overlaid (motion tracking style)
 * Each player has a unique color that persists throughout the video
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { processingApi, videoApi } from '../services/api';

// Supabase storage configuration
const SUPABASE_URL = 'https://zjsyuuaryyhdelyxnubm.supabase.co';
const SUPABASE_BUCKET = 'Matches';

// Helper to construct Supabase public URL
const getSupabasePublicUrl = (storagePath) => {
  if (!storagePath) return null;
  return `${SUPABASE_URL}/storage/v1/object/public/${SUPABASE_BUCKET}/${storagePath}`;
};

// Generate unique colors for each player - high contrast palette
const PLAYER_COLORS = [
  '#00FF00', // Bright Green
  '#FF6B6B', // Coral Red
  '#4ECDC4', // Teal
  '#FFE66D', // Yellow
  '#95E1D3', // Mint
  '#F38181', // Salmon
  '#AA96DA', // Lavender
  '#FCBAD3', // Pink
  '#A8D8EA', // Sky Blue
  '#FF9F43', // Orange
  '#2ECC71', // Emerald
  '#3498DB', // Blue
  '#9B59B6', // Purple
  '#E74C3C', // Red
  '#1ABC9C', // Turquoise
  '#F39C12', // Amber
  '#00CEC9', // Cyan
  '#FD79A8', // Hot Pink
  '#6C5CE7', // Violet
  '#00B894', // Green
  '#FDCB6E', // Mustard
  '#E17055', // Burnt Orange
];

// Team-based color schemes
const TEAM_COLORS = {
  home: {
    primary: '#00FF00',    // Green for home team
    secondary: '#00CC00',
    glow: '#00FF00'
  },
  away: {
    primary: '#FF6B6B',    // Red/Coral for away team
    secondary: '#FF4444',
    glow: '#FF6B6B'
  },
  unknown: {
    primary: '#FFFFFF',    // White for unknown
    secondary: '#CCCCCC',
    glow: '#FFFFFF'
  }
};

// Get color for a specific player (consistent across frames)
const getPlayerColor = (trackId, teamSide = 'unknown') => {
  // Use track ID to pick a consistent color from the palette
  const colorIndex = (trackId - 1) % PLAYER_COLORS.length;
  return PLAYER_COLORS[colorIndex];
};

// Get team color scheme
const getTeamColorScheme = (teamSide) => {
  return TEAM_COLORS[teamSide] || TEAM_COLORS.unknown;
};

export default function VideoOverlay() {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [trackData, setTrackData] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showBoxes, setShowBoxes] = useState(true);
  const [showTrails, setShowTrails] = useState(true);
  const [showIds, setShowIds] = useState(true);

  // Fetch video URL and tracking data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get video info
        const videoResponse = await videoApi.getById(videoId);
        setVideoInfo(videoResponse.data);
        
        // Construct video URL from Supabase storage
        if (videoResponse.data.storage_path) {
          const publicUrl = getSupabasePublicUrl(videoResponse.data.storage_path);
          console.log('Video URL:', publicUrl);
          setVideoUrl(publicUrl);
        }
        
        // Get tracking data
        const tracksResponse = await processingApi.getTracks(videoId);
        setTrackData(tracksResponse.data);
        
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.response?.data?.detail || 'Failed to load video data');
      } finally {
        setLoading(false);
      }
    };
    
    if (videoId) {
      fetchData();
    }
  }, [videoId]);

  // Get detections for current frame with interpolation
  const getDetectionsAtFrame = useCallback((frameNum) => {
    if (!trackData?.tracks) return [];
    
    const detections = [];
    trackData.tracks.forEach(track => {
      const points = track.points;
      if (!points || points.length === 0) return;
      
      // Check if this track is active at this frame
      const firstFrame = points[0].frame;
      const lastFrame = points[points.length - 1].frame;
      
      // Only show if frame is within track's lifetime
      if (frameNum < firstFrame || frameNum > lastFrame) return;
      
      // Find exact match first
      const exactPoint = points.find(p => p.frame === frameNum);
      if (exactPoint && exactPoint.bbox) {
        detections.push({
          track_id: track.track_id,
          team_side: track.team_side,
          bbox: exactPoint.bbox,
          confidence: exactPoint.confidence,
          x: exactPoint.x,
          y: exactPoint.y
        });
        return;
      }
      
      // Interpolate between two nearest frames
      let beforePoint = null;
      let afterPoint = null;
      
      for (let i = 0; i < points.length; i++) {
        if (points[i].frame <= frameNum) {
          beforePoint = points[i];
        }
        if (points[i].frame >= frameNum && !afterPoint) {
          afterPoint = points[i];
          break;
        }
      }
      
      // If we have both points, interpolate
      if (beforePoint && afterPoint && beforePoint.bbox && afterPoint.bbox) {
        const totalFrames = afterPoint.frame - beforePoint.frame;
        const progress = totalFrames > 0 ? (frameNum - beforePoint.frame) / totalFrames : 0;
        
        // Linear interpolation of bbox
        const bbox = [
          beforePoint.bbox[0] + (afterPoint.bbox[0] - beforePoint.bbox[0]) * progress,
          beforePoint.bbox[1] + (afterPoint.bbox[1] - beforePoint.bbox[1]) * progress,
          beforePoint.bbox[2] + (afterPoint.bbox[2] - beforePoint.bbox[2]) * progress,
          beforePoint.bbox[3] + (afterPoint.bbox[3] - beforePoint.bbox[3]) * progress,
        ];
        
        const x = beforePoint.x + (afterPoint.x - beforePoint.x) * progress;
        const y = beforePoint.y + (afterPoint.y - beforePoint.y) * progress;
        
        detections.push({
          track_id: track.track_id,
          team_side: track.team_side,
          bbox: bbox,
          confidence: (beforePoint.confidence + afterPoint.confidence) / 2,
          x: x,
          y: y,
          interpolated: true
        });
      } else if (beforePoint && beforePoint.bbox) {
        // Use last known position (track continues but no future point yet)
        detections.push({
          track_id: track.track_id,
          team_side: track.team_side,
          bbox: beforePoint.bbox,
          confidence: beforePoint.confidence,
          x: beforePoint.x,
          y: beforePoint.y,
          interpolated: true
        });
      }
    });
    
    return detections;
  }, [trackData]);

  // Get trail points for a track
  const getTrailPoints = useCallback((trackId, currentFrame) => {
    if (!trackData?.tracks) return [];
    
    const track = trackData.tracks.find(t => t.track_id === trackId);
    if (!track) return [];
    
    // Get last 30 points before current frame
    return track.points
      .filter(p => p.frame <= currentFrame && p.frame > currentFrame - 90)
      .map(p => ({ x: p.x, y: p.y, frame: p.frame }));
  }, [trackData]);

  // Draw overlays on canvas
  const drawOverlays = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !trackData) return;
    
    const ctx = canvas.getContext('2d');
    const fps = trackData.video_info?.fps || 30;
    const currentFrame = Math.floor(video.currentTime * fps);
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Scale factors
    const scaleX = canvas.width / (trackData.video_info?.width || video.videoWidth);
    const scaleY = canvas.height / (trackData.video_info?.height || video.videoHeight);
    
    const detections = getDetectionsAtFrame(currentFrame);
    
    // Draw trails first (behind boxes) - using player-specific colors
    if (showTrails) {
      detections.forEach(det => {
        const trailPoints = getTrailPoints(det.track_id, currentFrame);
        if (trailPoints.length < 2) return;
        
        // Get unique color for this player
        const playerColor = getPlayerColor(det.track_id, det.team_side);
        
        ctx.beginPath();
        ctx.strokeStyle = playerColor + '66';  // Add transparency
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        trailPoints.forEach((point, i) => {
          const x = point.x * scaleX;
          const y = point.y * scaleY;
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        ctx.stroke();
      });
    }
    
    // Draw bounding boxes with UNIQUE colors per player
    if (showBoxes) {
      detections.forEach(det => {
        const [x1, y1, x2, y2] = det.bbox;
        
        // Get unique color for this player
        const playerColor = getPlayerColor(det.track_id, det.team_side);
        
        // Scale bbox coordinates
        const sx1 = x1 * scaleX;
        const sy1 = y1 * scaleY;
        const sx2 = x2 * scaleX;
        const sy2 = y2 * scaleY;
        const width = sx2 - sx1;
        const height = sy2 - sy1;
        
        // Draw glow effect with player's unique color
        ctx.shadowColor = playerColor;
        ctx.shadowBlur = 15;
        
        // Draw bounding box with player's unique color
        ctx.strokeStyle = playerColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(sx1, sy1, width, height);
        
        // Reset shadow
        ctx.shadowBlur = 0;
        
        // Draw corner accents (motion tracking style) - thicker corners with player color
        const cornerLength = Math.min(width, height) * 0.25;
        ctx.strokeStyle = playerColor;
        ctx.lineWidth = 3;
        
        // Top-left corner
        ctx.beginPath();
        ctx.moveTo(sx1, sy1 + cornerLength);
        ctx.lineTo(sx1, sy1);
        ctx.lineTo(sx1 + cornerLength, sy1);
        ctx.stroke();
        
        // Top-right corner
        ctx.beginPath();
        ctx.moveTo(sx2 - cornerLength, sy1);
        ctx.lineTo(sx2, sy1);
        ctx.lineTo(sx2, sy1 + cornerLength);
        ctx.stroke();
        
        // Bottom-left corner
        ctx.beginPath();
        ctx.moveTo(sx1, sy2 - cornerLength);
        ctx.lineTo(sx1, sy2);
        ctx.lineTo(sx1 + cornerLength, sy2);
        ctx.stroke();
        
        // Bottom-right corner
        ctx.beginPath();
        ctx.moveTo(sx2 - cornerLength, sy2);
        ctx.lineTo(sx2, sy2);
        ctx.lineTo(sx2, sy2 - cornerLength);
        ctx.stroke();
        
        // Draw ID label with player number and team
        if (showIds) {
          const teamLabel = det.team_side === 'home' ? 'H' : det.team_side === 'away' ? 'A' : '';
          const label = teamLabel ? `#${det.track_id} (${teamLabel})` : `#${det.track_id}`;
          ctx.font = 'bold 12px Inter, system-ui, sans-serif';
          const textWidth = ctx.measureText(label).width;
          
          // Label background - dark with player color border
          ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
          ctx.fillRect(sx1, sy1 - 22, textWidth + 14, 20);
          ctx.strokeStyle = playerColor;
          ctx.lineWidth = 2;
          ctx.strokeRect(sx1, sy1 - 22, textWidth + 14, 20);
          
          // Small color indicator circle
          ctx.beginPath();
          ctx.arc(sx1 + 8, sy1 - 12, 4, 0, Math.PI * 2);
          ctx.fillStyle = playerColor;
          ctx.fill();
          
          // Label text - white for readability
          ctx.fillStyle = '#FFFFFF';
          ctx.textBaseline = 'middle';
          ctx.fillText(label, sx1 + 16, sy1 - 12);
        }
        
        // Draw center crosshair with player color
        const centerX = (sx1 + sx2) / 2;
        const centerY = (sy1 + sy2) / 2;
        ctx.strokeStyle = playerColor;
        ctx.lineWidth = 1;
        
        // Horizontal line of crosshair
        ctx.beginPath();
        ctx.moveTo(centerX - 6, centerY);
        ctx.lineTo(centerX + 6, centerY);
        ctx.stroke();
        
        // Vertical line of crosshair
        ctx.beginPath();
        ctx.moveTo(centerX, centerY - 6);
        ctx.lineTo(centerX, centerY + 6);
        ctx.stroke();
      });
    }
    
    // Continue animation if playing
    if (isPlaying) {
      animationRef.current = requestAnimationFrame(drawOverlays);
    }
  }, [trackData, isPlaying, showBoxes, showTrails, showIds, getDetectionsAtFrame, getTrailPoints]);

  // Handle video play/pause
  useEffect(() => {
    if (isPlaying) {
      animationRef.current = requestAnimationFrame(drawOverlays);
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      // Draw current frame when paused
      drawOverlays();
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, drawOverlays]);

  // Sync canvas size with video
  const handleVideoLoaded = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (video && canvas) {
      canvas.width = video.clientWidth;
      canvas.height = video.clientHeight;
      drawOverlays();
    }
  };

  const handlePlay = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);
  const handleTimeUpdate = () => {
    if (!isPlaying) {
      drawOverlays();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-slate-400">Loading video and tracking data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-white mb-2">Error Loading Video</h2>
          <p className="text-slate-400 mb-6">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-slate-700 text-white rounded-xl hover:bg-slate-600 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
              >
                <span className="text-xl">←</span>
                <span className="font-medium">Back</span>
              </button>
              <div className="h-6 w-px bg-slate-700"></div>
              <div>
                <h1 className="text-xl font-bold text-white">🎯 Motion Tracking View</h1>
                <p className="text-sm text-slate-400">AI-detected players with tracking overlay</p>
              </div>
            </div>
            
            {/* Controls */}
            <div className="flex items-center gap-3">
              <Link
                to={`/videos/${videoId}/player-analysis`}
                className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors font-medium"
              >
                📊 Player Analytics
              </Link>
              <Link
                to={`/videos/${videoId}/analytics`}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium"
              >
                📈 Team Overview
              </Link>
              <div className="h-6 w-px bg-slate-700"></div>
              <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showBoxes}
                  onChange={(e) => setShowBoxes(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-700 border-slate-600 text-blue-500 focus:ring-blue-500"
                />
                Boxes
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showTrails}
                  onChange={(e) => setShowTrails(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-700 border-slate-600 text-blue-500 focus:ring-blue-500"
                />
                Trails
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showIds}
                  onChange={(e) => setShowIds(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-700 border-slate-600 text-blue-500 focus:ring-blue-500"
                />
                IDs
              </label>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Video Container */}
        <div className="relative bg-black rounded-2xl overflow-hidden shadow-2xl">
          {videoUrl ? (
            <>
              <video
                ref={videoRef}
                src={videoUrl}
                className="w-full"
                controls
                onLoadedMetadata={handleVideoLoaded}
                onResize={handleVideoLoaded}
                onPlay={handlePlay}
                onPause={handlePause}
                onTimeUpdate={handleTimeUpdate}
                onSeeked={handleTimeUpdate}
                crossOrigin="anonymous"
              />
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 w-full h-full pointer-events-none"
                style={{ objectFit: 'contain' }}
              />
            </>
          ) : (
            <div className="aspect-video flex items-center justify-center">
              <p className="text-slate-400">No video available</p>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4">
            <p className="text-sm text-slate-400 mb-1">Players Tracked</p>
            <p className="text-2xl font-bold text-white">{trackData?.tracks?.length || 0}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4">
            <p className="text-sm text-slate-400 mb-1">Total Detections</p>
            <p className="text-2xl font-bold text-white">
              {trackData?.tracks?.reduce((sum, t) => sum + t.points.length, 0) || 0}
            </p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4">
            <p className="text-sm text-slate-400 mb-1">Video FPS</p>
            <p className="text-2xl font-bold text-white">{trackData?.video_info?.fps?.toFixed(1) || 'N/A'}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4">
            <p className="text-sm text-slate-400 mb-1">Resolution</p>
            <p className="text-2xl font-bold text-white">
              {trackData?.video_info?.width || 0}×{trackData?.video_info?.height || 0}
            </p>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-6 bg-slate-800/30 backdrop-blur rounded-xl p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Detection Legend</h3>
          <div className="flex flex-wrap gap-6">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#00ff00' }}></div>
              <span className="text-sm text-slate-400">Detected Players</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border-2" style={{ borderColor: '#00ff00', backgroundColor: 'transparent' }}></div>
              <span className="text-sm text-slate-400">Bounding Box</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-6 flex gap-4">
          <button
            onClick={() => navigate(`/videos/${videoId}/pitch`)}
            className="flex-1 px-6 py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium transition-colors"
          >
            <span className="flex items-center justify-center gap-2">
              <span>🏟️</span>
              <span>View 2D Pitch</span>
            </span>
          </button>
        </div>
      </main>
    </div>
  );
}
