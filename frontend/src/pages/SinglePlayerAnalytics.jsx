import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

const API_URL = 'http://127.0.0.1:8000';

const SinglePlayerAnalytics = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [selectedTrackId, setSelectedTrackId] = useState(null);
  const [playerMetrics, setPlayerMetrics] = useState(null);
  const [playerHeatmap, setPlayerHeatmap] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const heatmapCanvasRef = useRef(null);

  // Fetch all tracks for the video
  useEffect(() => {
    const fetchTracks = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/v1/player-analytics/video/${videoId}/players`);
        if (!response.ok) {
          throw new Error('Failed to fetch tracks');
        }
        const data = await response.json();
        
        // Filter players with meaningful tracking data
        // Only show players with at least 20 detections and 2 seconds of tracking
        const filteredPlayers = (data.players || []).filter(p => 
          p.total_detections >= 20 && 
          p.metrics.duration_seconds >= 2.0 &&
          p.metrics.total_distance_m > 3.0
        );
        
        // Sort by total distance (most active players first)
        filteredPlayers.sort((a, b) => 
          b.metrics.total_distance_m - a.metrics.total_distance_m
        );
        
        setTracks(filteredPlayers);
        
        // Auto-select player with most distance covered
        if (filteredPlayers.length > 0) {
          setSelectedTrackId(filteredPlayers[0].player_id);
        }
        
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (videoId) {
      fetchTracks();
    }
  }, [videoId]);

  // Fetch metrics and heatmap for selected player
  useEffect(() => {
    const fetchPlayerData = async () => {
      if (!selectedTrackId) return;
      
      try {
        setMetricsLoading(true);
        
        // Fetch metrics
        const metricsRes = await fetch(`${API_URL}/api/v1/player-analytics/player/${selectedTrackId}/metrics`);
        if (metricsRes.ok) {
          const metricsData = await metricsRes.json();
          setPlayerMetrics(metricsData);
        }
        
        // Fetch heatmap
        const heatmapRes = await fetch(`${API_URL}/api/v1/player-analytics/player/${selectedTrackId}/heatmap?grid_size=30`);
        if (heatmapRes.ok) {
          const heatmapData = await heatmapRes.json();
          setPlayerHeatmap(heatmapData);
        }
      } catch (err) {
        console.error('Failed to fetch player data:', err);
      } finally {
        setMetricsLoading(false);
      }
    };

    fetchPlayerData();
  }, [selectedTrackId]);

  // Draw heatmap on canvas
  useEffect(() => {
    const canvas = heatmapCanvasRef.current;
    if (!canvas || !playerHeatmap || !playerHeatmap.data) return;

    const ctx = canvas.getContext('2d');
    const { data, grid_width, grid_height } = playerHeatmap;

    // Set canvas size - football pitch aspect ratio
    const width = 700;
    const height = Math.floor(width * (68 / 105));
    canvas.width = width;
    canvas.height = height;

    // Draw pitch background
    ctx.fillStyle = '#1a472a';
    ctx.fillRect(0, 0, width, height);

    // Draw pitch markings
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 2;
    
    // Outer boundary
    ctx.strokeRect(15, 15, width - 30, height - 30);
    
    // Center line
    ctx.beginPath();
    ctx.moveTo(width / 2, 15);
    ctx.lineTo(width / 2, height - 15);
    ctx.stroke();
    
    // Center circle
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, 60, 0, Math.PI * 2);
    ctx.stroke();

    // Penalty areas
    const penaltyWidth = 120;
    const penaltyHeight = 200;
    ctx.strokeRect(15, (height - penaltyHeight) / 2, penaltyWidth, penaltyHeight);
    ctx.strokeRect(width - 15 - penaltyWidth, (height - penaltyHeight) / 2, penaltyWidth, penaltyHeight);

    // Goal boxes
    const goalBoxWidth = 50;
    const goalBoxHeight = 100;
    ctx.strokeRect(15, (height - goalBoxHeight) / 2, goalBoxWidth, goalBoxHeight);
    ctx.strokeRect(width - 15 - goalBoxWidth, (height - goalBoxHeight) / 2, goalBoxWidth, goalBoxHeight);

    // Draw heatmap
    const cellWidth = (width - 30) / grid_width;
    const cellHeight = (height - 30) / grid_height;

    for (let row = 0; row < data.length; row++) {
      for (let col = 0; col < data[row].length; col++) {
        const intensity = data[row][col];
        if (intensity > 0.05) {
          const x = 15 + col * cellWidth;
          const y = 15 + row * cellHeight;
          
          // Color gradient: blue -> green -> yellow -> red
          let r, g, b;
          if (intensity < 0.33) {
            // Blue to Green
            const t = intensity / 0.33;
            r = 0;
            g = Math.floor(255 * t);
            b = Math.floor(255 * (1 - t));
          } else if (intensity < 0.66) {
            // Green to Yellow
            const t = (intensity - 0.33) / 0.33;
            r = Math.floor(255 * t);
            g = 255;
            b = 0;
          } else {
            // Yellow to Red
            const t = (intensity - 0.66) / 0.34;
            r = 255;
            g = Math.floor(255 * (1 - t));
            b = 0;
          }
          
          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.4 + intensity * 0.4})`;
          ctx.fillRect(x, y, cellWidth + 1, cellHeight + 1);
        }
      }
    }

    // Add legend
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(width - 180, height - 50, 160, 35);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '12px Arial';
    ctx.fillText('🔵 Low Activity  🟢 Medium  🔴 High', width - 170, height - 27);
  }, [playerHeatmap]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-xl">Loading Player Data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <div className="text-xl text-red-400">{error}</div>
          <p className="text-slate-400 mt-2">Make sure the video has been processed</p>
          <Link to={`/videos/${videoId}/overlay`} className="text-cyan-400 hover:underline mt-4 block">
            ← Back to Video
          </Link>
        </div>
      </div>
    );
  }

  if (tracks.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <div className="text-xl">No player tracking data found</div>
          <p className="text-slate-400 mt-2">Process the video first to generate tracking data</p>
        </div>
      </div>
    );
  }

  const selectedPlayer = tracks.find(t => t.player_id === selectedTrackId);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to={`/videos/${videoId}/overlay`} className="text-slate-400 hover:text-white">
              ← Back to Video
            </Link>
            <h1 className="text-2xl font-bold">👤 Single Player Analysis</h1>
          </div>
          <div className="text-sm text-slate-400">
            {tracks.length} players tracked
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Summary Info */}
        <div className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-4 border border-blue-700 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">📊 Showing Top Active Players</h2>
              <p className="text-sm text-slate-300 mt-1">
                Filtered to players with at least 20 detections and 3m distance covered
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-cyan-400">{tracks.length}</div>
              <div className="text-sm text-slate-400">Active Players</div>
            </div>
          </div>
        </div>

        {/* Player Selector */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-6">
          <h2 className="text-lg font-semibold mb-4">Select Player to Analyze</h2>
          <p className="text-sm text-slate-400 mb-4">Players sorted by total distance covered (most active first)</p>
          <div className="grid grid-cols-4 md:grid-cols-8 lg:grid-cols-10 gap-2">
            {tracks.map(track => (
              <button
                key={track.player_id}
                onClick={() => setSelectedTrackId(track.player_id)}
                className={`px-4 py-3 rounded-lg font-bold transition-all ${
                  selectedTrackId === track.player_id
                    ? 'bg-cyan-600 text-white scale-105 shadow-lg'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
                title={`${track.metrics.total_distance_m.toFixed(0)}m, ${track.total_detections} detections`}
              >
                #{track.track_id}
              </button>
            ))}
          </div>
        </div>

        {selectedPlayer && playerMetrics && (
          <>
            {/* Player Info Card */}
            <div className="bg-gradient-to-br from-cyan-900 to-blue-900 rounded-lg p-6 border border-cyan-700 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold mb-2">Player #{selectedPlayer.track_id}</h2>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded text-sm font-medium ${
                      selectedPlayer.team_side === 'home' ? 'bg-blue-600' : 'bg-red-600'
                    }`}>
                      {selectedPlayer.team_side || 'Unknown Team'}
                    </span>
                    <span className="px-3 py-1 rounded text-sm font-medium bg-slate-700">
                      {selectedPlayer.total_detections} detections
                    </span>
                  </div>
                </div>
                <div className="text-6xl">👤</div>
              </div>
            </div>

            {/* Main Metrics */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-slate-400 text-sm mb-2">Distance Covered</div>
                <div className="text-4xl font-bold text-cyan-400">
                  {playerMetrics.total_distance_m.toFixed(0)}
                  <span className="text-lg text-slate-500 ml-2">meters</span>
                </div>
                <div className="text-sm text-slate-500 mt-1">
                  {playerMetrics.total_distance_km.toFixed(2)} km
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-slate-400 text-sm mb-2">Top Speed</div>
                <div className="text-4xl font-bold text-yellow-400">
                  {playerMetrics.top_speed_kmh.toFixed(1)}
                  <span className="text-lg text-slate-500 ml-2">km/h</span>
                </div>
                <div className="text-sm text-slate-500 mt-1">
                  {playerMetrics.top_speed_mps.toFixed(2)} m/s
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-slate-400 text-sm mb-2">Average Speed</div>
                <div className="text-4xl font-bold text-green-400">
                  {playerMetrics.avg_speed_kmh.toFixed(1)}
                  <span className="text-lg text-slate-500 ml-2">km/h</span>
                </div>
                <div className="text-sm text-slate-500 mt-1">
                  {playerMetrics.avg_speed_mps.toFixed(2)} m/s
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-slate-400 text-sm mb-2">Sprint Count</div>
                <div className="text-4xl font-bold text-red-400">
                  {playerMetrics.sprint_count}
                  <span className="text-lg text-slate-500 ml-2">sprints</span>
                </div>
                <div className="text-sm text-slate-500 mt-1">
                  {playerMetrics.sprint_distance_m.toFixed(0)}m at high speed
                </div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="text-slate-400 text-sm">Max Acceleration</div>
                <div className="text-2xl font-bold text-purple-400 mt-1">
                  {playerMetrics.max_acceleration_mps2.toFixed(2)} m/s²
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="text-slate-400 text-sm">High Intensity Distance</div>
                <div className="text-2xl font-bold text-orange-400 mt-1">
                  {playerMetrics.high_intensity_distance_m.toFixed(0)} m
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="text-slate-400 text-sm">Stamina Index</div>
                <div className="text-2xl font-bold text-pink-400 mt-1">
                  {playerMetrics.stamina_index.toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Heatmap */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-xl font-bold mb-4">🗺️ Player Movement Heatmap</h2>
              <p className="text-slate-400 text-sm mb-4">
                Shows where Player #{selectedPlayer.track_id} spent most time during the match.
                Hotter colors (red) indicate more time spent in that area.
              </p>
              <div className="flex justify-center">
                <canvas 
                  ref={heatmapCanvasRef} 
                  className="rounded-lg shadow-xl"
                  style={{ maxWidth: '100%' }}
                />
              </div>
            </div>

            {/* Data Summary */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mt-6">
              <h2 className="text-xl font-bold mb-4">📋 Tracking Summary</h2>
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">Total Data Points:</span>
                  <span className="ml-2 text-white font-medium">{playerMetrics.total_points}</span>
                </div>
                <div>
                  <span className="text-slate-400">Duration Tracked:</span>
                  <span className="ml-2 text-white font-medium">{playerMetrics.duration_seconds.toFixed(1)}s</span>
                </div>
                <div>
                  <span className="text-slate-400">First Frame:</span>
                  <span className="ml-2 text-white font-medium">{selectedPlayer.first_frame}</span>
                </div>
              </div>
            </div>
          </>
        )}

        {metricsLoading && (
          <div className="text-center py-12">
            <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <div className="text-slate-400">Loading player metrics...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SinglePlayerAnalytics;
