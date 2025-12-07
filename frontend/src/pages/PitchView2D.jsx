import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { processingApi } from '../services/api';

// Football pitch dimensions in meters (standard)
const PITCH_LENGTH = 105;
const PITCH_WIDTH = 68;

// Canvas dimensions
const CANVAS_WIDTH = 900;
const CANVAS_HEIGHT = 585;

// Scale factors
const SCALE_X = CANVAS_WIDTH / PITCH_LENGTH;
const SCALE_Y = CANVAS_HEIGHT / PITCH_WIDTH;

// Player colors for teams
const TEAM_COLORS = {
  teamA: { fill: '#ef4444', stroke: '#dc2626', text: '#ffffff' },
  teamB: { fill: '#3b82f6', stroke: '#2563eb', text: '#ffffff' },
  ball: { fill: '#fbbf24', stroke: '#f59e0b', text: '#000000' }
};

/**
 * Draw a professional football pitch on canvas
 */
function drawPitch(ctx) {
  // Grass pattern background
  const gradient = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT);
  gradient.addColorStop(0, '#22c55e');
  gradient.addColorStop(0.5, '#16a34a');
  gradient.addColorStop(1, '#22c55e');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  
  // Grass stripes effect
  ctx.fillStyle = 'rgba(255, 255, 255, 0.03)';
  for (let i = 0; i < CANVAS_WIDTH; i += 60) {
    ctx.fillRect(i, 0, 30, CANVAS_HEIGHT);
  }
  
  // Pitch markings
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.95)';
  ctx.lineWidth = 2.5;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  
  const margin = 20;
  const pitchWidth = CANVAS_WIDTH - margin * 2;
  const pitchHeight = CANVAS_HEIGHT - margin * 2;
  
  // Outer boundary
  ctx.strokeRect(margin, margin, pitchWidth, pitchHeight);
  
  // Center line
  ctx.beginPath();
  ctx.moveTo(CANVAS_WIDTH / 2, margin);
  ctx.lineTo(CANVAS_WIDTH / 2, CANVAS_HEIGHT - margin);
  ctx.stroke();
  
  // Center circle
  const centerCircleRadius = 9.15 * SCALE_X;
  ctx.beginPath();
  ctx.arc(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, centerCircleRadius, 0, Math.PI * 2);
  ctx.stroke();
  
  // Center spot
  ctx.beginPath();
  ctx.arc(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, 4, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
  ctx.fill();
  
  // Penalty areas
  const penaltyAreaWidth = 16.5 * SCALE_X;
  const penaltyAreaHeight = 40.3 * SCALE_Y;
  const penaltyAreaTop = (CANVAS_HEIGHT - penaltyAreaHeight) / 2;
  
  // Left penalty area
  ctx.strokeRect(margin, penaltyAreaTop, penaltyAreaWidth, penaltyAreaHeight);
  
  // Right penalty area
  ctx.strokeRect(CANVAS_WIDTH - margin - penaltyAreaWidth, penaltyAreaTop, penaltyAreaWidth, penaltyAreaHeight);
  
  // Goal areas (6-yard box)
  const goalAreaWidth = 5.5 * SCALE_X;
  const goalAreaHeight = 18.32 * SCALE_Y;
  const goalAreaTop = (CANVAS_HEIGHT - goalAreaHeight) / 2;
  
  ctx.strokeRect(margin, goalAreaTop, goalAreaWidth, goalAreaHeight);
  ctx.strokeRect(CANVAS_WIDTH - margin - goalAreaWidth, goalAreaTop, goalAreaWidth, goalAreaHeight);
  
  // Penalty spots
  const penaltySpotDist = 11 * SCALE_X;
  ctx.beginPath();
  ctx.arc(margin + penaltySpotDist, CANVAS_HEIGHT / 2, 4, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(CANVAS_WIDTH - margin - penaltySpotDist, CANVAS_HEIGHT / 2, 4, 0, Math.PI * 2);
  ctx.fill();
  
  // Penalty arcs
  ctx.beginPath();
  ctx.arc(margin + penaltySpotDist, CANVAS_HEIGHT / 2, centerCircleRadius, -0.93, 0.93);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(CANVAS_WIDTH - margin - penaltySpotDist, CANVAS_HEIGHT / 2, centerCircleRadius, Math.PI - 0.93, Math.PI + 0.93);
  ctx.stroke();
  
  // Corner arcs
  const cornerRadius = 8;
  ctx.beginPath();
  ctx.arc(margin, margin, cornerRadius, 0, Math.PI / 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(CANVAS_WIDTH - margin, margin, cornerRadius, Math.PI / 2, Math.PI);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(margin, CANVAS_HEIGHT - margin, cornerRadius, -Math.PI / 2, 0);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(CANVAS_WIDTH - margin, CANVAS_HEIGHT - margin, cornerRadius, Math.PI, Math.PI * 1.5);
  ctx.stroke();
  
  // Goals
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 3;
  const goalWidth = 7.32 * SCALE_Y;
  const goalDepth = 8;
  const goalTop = (CANVAS_HEIGHT - goalWidth) / 2;
  
  // Left goal
  ctx.fillRect(margin - goalDepth, goalTop, goalDepth, goalWidth);
  ctx.strokeRect(margin - goalDepth, goalTop, goalDepth, goalWidth);
  
  // Right goal
  ctx.fillRect(CANVAS_WIDTH - margin, goalTop, goalDepth, goalWidth);
  ctx.strokeRect(CANVAS_WIDTH - margin, goalTop, goalDepth, goalWidth);
}

/**
 * Convert video pixel coordinates to pitch coordinates
 */
function videoToPitch(x, y, videoWidth, videoHeight) {
  const margin = 20;
  const pitchX = margin + ((x / videoWidth) * (CANVAS_WIDTH - margin * 2));
  const pitchY = margin + ((y / videoHeight) * (CANVAS_HEIGHT - margin * 2));
  
  return { x: pitchX, y: pitchY };
}

/**
 * Draw players on pitch with nice styling
 */
function drawPlayers(ctx, players, videoWidth, videoHeight) {
  players.forEach((player) => {
    const pos = videoToPitch(player.x, player.y, videoWidth, videoHeight);
    
    // Determine color based on track_id (alternate between two teams for demo)
    const isTeamA = player.track_id % 2 === 0;
    const colors = isTeamA ? TEAM_COLORS.teamA : TEAM_COLORS.teamB;
    
    // Shadow
    ctx.beginPath();
    ctx.ellipse(pos.x + 2, pos.y + 14, 10, 4, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fill();
    
    // Player circle with gradient
    const playerGradient = ctx.createRadialGradient(pos.x - 3, pos.y - 3, 0, pos.x, pos.y, 14);
    playerGradient.addColorStop(0, colors.fill);
    playerGradient.addColorStop(1, colors.stroke);
    
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 14, 0, Math.PI * 2);
    ctx.fillStyle = playerGradient;
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Player number/ID
    ctx.fillStyle = colors.text;
    ctx.font = 'bold 11px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(player.track_id.toString(), pos.x, pos.y);
  });
}

/**
 * Draw player trails (movement history)
 */
function drawTrails(ctx, tracks, currentFrame, videoWidth, videoHeight) {
  tracks.forEach((track) => {
    const isTeamA = track.track_id % 2 === 0;
    const color = isTeamA ? 'rgba(239, 68, 68, 0.4)' : 'rgba(59, 130, 246, 0.4)';
    
    const relevantPoints = track.points.filter(p => p.frame <= currentFrame).slice(-20);
    
    if (relevantPoints.length < 2) return;
    
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    relevantPoints.forEach((point, i) => {
      const pos = videoToPitch(point.x, point.y, videoWidth, videoHeight);
      if (i === 0) {
        ctx.moveTo(pos.x, pos.y);
      } else {
        ctx.lineTo(pos.x, pos.y);
      }
    });
    
    ctx.stroke();
  });
}

/**
 * Main 2D Pitch View Component
 */
export default function PitchView2D() {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const canvasRef = useRef(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trackData, setTrackData] = useState(null);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [showTrails, setShowTrails] = useState(true);
  
  // Fetch track data
  useEffect(() => {
    const fetchTracks = async () => {
      try {
        setLoading(true);
        const response = await processingApi.getTracks(videoId);
        setTrackData(response.data);
        setError(null);
        
        // Set initial frame to first tracked frame
        if (response.data?.tracks?.length > 0) {
          const minFrame = Math.min(...response.data.tracks.flatMap(t => t.points.map(p => p.frame)));
          setCurrentFrame(minFrame);
        }
      } catch (err) {
        console.error('Error fetching tracks:', err);
        setError(err.response?.data?.detail || 'Failed to load track data. Make sure the video has been processed.');
      } finally {
        setLoading(false);
      }
    };
    
    if (videoId) {
      fetchTracks();
    }
  }, [videoId]);
  
  // Get players at current frame
  const getPlayersAtFrame = useCallback((frameNum) => {
    if (!trackData?.tracks) return [];
    
    const players = [];
    trackData.tracks.forEach(track => {
      const point = track.points.find(p => p.frame === frameNum);
      if (point) {
        players.push({
          track_id: track.track_id,
          x: point.x,
          y: point.y,
          bbox: point.bbox,
          confidence: point.confidence
        });
      } else {
        const beforePoints = track.points.filter(p => p.frame <= frameNum);
        if (beforePoints.length > 0) {
          const closest = beforePoints[beforePoints.length - 1];
          if (frameNum - closest.frame < 15) {
            players.push({
              track_id: track.track_id,
              x: closest.x,
              y: closest.y,
              bbox: closest.bbox,
              confidence: closest.confidence
            });
          }
        }
      }
    });
    
    return players;
  }, [trackData]);
  
  // Draw the pitch and players
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !trackData) return;
    
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    drawPitch(ctx);
    
    if (showTrails) {
      drawTrails(ctx, trackData.tracks, currentFrame, trackData.video_info.width, trackData.video_info.height);
    }
    
    const players = getPlayersAtFrame(currentFrame);
    drawPlayers(ctx, players, trackData.video_info.width, trackData.video_info.height);
    
  }, [currentFrame, trackData, getPlayersAtFrame, showTrails]);
  
  // Playback animation
  useEffect(() => {
    if (!isPlaying || !trackData) return;
    
    const fps = trackData.video_info.fps || 30;
    const frameSkip = Math.ceil(fps / 5);
    const interval = (1000 / fps) * frameSkip / playbackSpeed;
    
    const timer = setInterval(() => {
      setCurrentFrame(prev => {
        const maxFrame = Math.max(...trackData.tracks.flatMap(t => t.points.map(p => p.frame)));
        if (prev >= maxFrame) {
          setIsPlaying(false);
          return prev;
        }
        return prev + frameSkip;
      });
    }, interval);
    
    return () => clearInterval(timer);
  }, [isPlaying, trackData, playbackSpeed]);
  
  // Get frame range
  const getFrameRange = () => {
    if (!trackData?.tracks?.length) return { min: 0, max: 100 };
    
    const allFrames = trackData.tracks.flatMap(t => t.points.map(p => p.frame));
    return { min: Math.min(...allFrames), max: Math.max(...allFrames) };
  };
  
  const frameRange = getFrameRange();
  const currentTimestamp = trackData ? (currentFrame / (trackData.video_info.fps || 30)).toFixed(1) : '0.0';
  const totalDuration = trackData ? trackData.video_info.duration?.toFixed(1) || '0.0' : '0.0';
  const playersAtFrame = trackData ? getPlayersAtFrame(currentFrame).length : 0;
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
          <h2 className="text-2xl font-bold text-white mb-2">Loading Match Data</h2>
          <p className="text-slate-400">Preparing the 2D pitch visualization...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
        <div className="bg-slate-800/80 backdrop-blur border border-red-500/30 rounded-2xl p-10 max-w-lg text-center shadow-2xl">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-3xl">⚠️</span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">Unable to Load Data</h2>
          <p className="text-slate-400 mb-8">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-8 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-medium transition-all duration-200"
          >
            ← Go Back
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
              <h1 className="text-xl font-bold text-white">2D Match Visualization</h1>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-slate-400">
                <span className="text-lg">👥</span>
                <span className="font-medium">{playersAtFrame} visible</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <span className="text-lg">⏱️</span>
                <span className="font-medium">{currentTimestamp}s / {totalDuration}s</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Main Canvas Area */}
          <div className="xl:col-span-3">
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6 shadow-2xl border border-slate-700/50">
              {/* Canvas */}
              <div className="relative rounded-xl overflow-hidden shadow-inner mb-6" style={{ background: '#1a1a2e' }}>
                <canvas
                  ref={canvasRef}
                  width={CANVAS_WIDTH}
                  height={CANVAS_HEIGHT}
                  className="w-full h-auto"
                  style={{ maxWidth: CANVAS_WIDTH }}
                />
                
                {/* Frame indicator overlay */}
                <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-sm px-3 py-1.5 rounded-lg">
                  <span className="text-white text-sm font-mono">Frame: {currentFrame}</span>
                </div>
              </div>
              
              {/* Timeline */}
              <div className="mb-6">
                <input
                  type="range"
                  min={frameRange.min}
                  max={frameRange.max}
                  value={currentFrame}
                  onChange={(e) => setCurrentFrame(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-full appearance-none cursor-pointer
                    [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 
                    [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-emerald-500 
                    [&::-webkit-slider-thumb]:hover:bg-emerald-400 [&::-webkit-slider-thumb]:transition-colors
                    [&::-webkit-slider-thumb]:shadow-lg"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-2">
                  <span>0:00</span>
                  <span>{totalDuration}s</span>
                </div>
              </div>
              
              {/* Controls */}
              <div className="flex items-center justify-center gap-3">
                <button
                  onClick={() => setCurrentFrame(frameRange.min)}
                  className="p-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors"
                  title="Go to start"
                >
                  <span className="text-xl">⏮️</span>
                </button>
                
                <button
                  onClick={() => setCurrentFrame(prev => Math.max(frameRange.min, prev - 30))}
                  className="p-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors"
                  title="Back 1 second"
                >
                  <span className="text-xl">⏪</span>
                </button>
                
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className={`p-4 rounded-xl transition-all duration-200 ${
                    isPlaying 
                      ? 'bg-amber-500 hover:bg-amber-400 text-white' 
                      : 'bg-emerald-500 hover:bg-emerald-400 text-white'
                  }`}
                >
                  <span className="text-2xl">{isPlaying ? '⏸️' : '▶️'}</span>
                </button>
                
                <button
                  onClick={() => setCurrentFrame(prev => Math.min(frameRange.max, prev + 30))}
                  className="p-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors"
                  title="Forward 1 second"
                >
                  <span className="text-xl">⏩</span>
                </button>
                
                <button
                  onClick={() => setCurrentFrame(frameRange.max)}
                  className="p-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-colors"
                  title="Go to end"
                >
                  <span className="text-xl">⏭️</span>
                </button>
                
                <div className="w-px h-8 bg-slate-700 mx-2"></div>
                
                {/* Speed selector */}
                <select
                  value={playbackSpeed}
                  onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                  className="bg-slate-700 text-white px-4 py-2 rounded-xl border-0 focus:ring-2 focus:ring-emerald-500"
                >
                  <option value={0.25}>0.25x</option>
                  <option value={0.5}>0.5x</option>
                  <option value={1}>1x</option>
                  <option value={2}>2x</option>
                </select>
                
                {/* Trails toggle */}
                <button
                  onClick={() => setShowTrails(!showTrails)}
                  className={`px-4 py-2 rounded-xl transition-colors ${
                    showTrails ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-400'
                  }`}
                >
                  Trails {showTrails ? 'ON' : 'OFF'}
                </button>
              </div>
            </div>
          </div>
          
          {/* Sidebar Stats */}
          <div className="xl:col-span-1 space-y-6">
            {/* Legend */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6 border border-slate-700/50">
              <h3 className="text-lg font-semibold text-white mb-4">Legend</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center text-white text-xs font-bold shadow-lg">A</div>
                  <span className="text-slate-300">Team A (Red)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-bold shadow-lg">B</div>
                  <span className="text-slate-300">Team B (Blue)</span>
                </div>
              </div>
            </div>
            
            {/* Match Stats */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6 border border-slate-700/50">
              <h3 className="text-lg font-semibold text-white mb-4">Match Statistics</h3>
              <div className="space-y-4">
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <div className="text-3xl font-bold text-emerald-400">{trackData?.tracks?.length || 0}</div>
                  <div className="text-sm text-slate-400">Players Tracked</div>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <div className="text-3xl font-bold text-blue-400">{trackData?.video_info?.total_frames || 0}</div>
                  <div className="text-sm text-slate-400">Total Frames</div>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <div className="text-3xl font-bold text-purple-400">{(trackData?.video_info?.fps || 0).toFixed(1)}</div>
                  <div className="text-sm text-slate-400">FPS</div>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <div className="text-3xl font-bold text-amber-400">
                    {trackData?.tracks?.reduce((sum, t) => sum + t.points.length, 0) || 0}
                  </div>
                  <div className="text-sm text-slate-400">Total Detections</div>
                </div>
              </div>
            </div>
            
            {/* Video Info */}
            <div className="bg-slate-800/50 backdrop-blur rounded-2xl p-6 border border-slate-700/50">
              <h3 className="text-lg font-semibold text-white mb-4">Video Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Resolution</span>
                  <span className="text-white font-medium">
                    {trackData?.video_info?.width || 0} × {trackData?.video_info?.height || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Duration</span>
                  <span className="text-white font-medium">{totalDuration}s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
