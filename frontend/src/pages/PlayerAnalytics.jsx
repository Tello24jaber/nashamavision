import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, PieChart, Pie, Cell
} from 'recharts';

const API_URL = 'http://127.0.0.1:8000';

// Color scheme for charts
const COLORS = ['#00D4AA', '#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181'];

const PlayerAnalytics = () => {
  const { videoId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerHeatmap, setPlayerHeatmap] = useState(null);
  const [combinedHeatmap, setCombinedHeatmap] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const heatmapCanvasRef = useRef(null);

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/v1/player-analytics/video/${videoId}/players`);
        if (!response.ok) {
          throw new Error('Failed to fetch analytics');
        }
        const data = await response.json();
        setAnalyticsData(data);
        
        // Fetch combined heatmap
        const heatmapRes = await fetch(`${API_URL}/api/v1/player-analytics/video/${videoId}/heatmap?grid_size=30`);
        if (heatmapRes.ok) {
          const heatmapData = await heatmapRes.json();
          setCombinedHeatmap(heatmapData);
        }
        
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (videoId) {
      fetchAnalytics();
    }
  }, [videoId]);

  // Fetch individual player heatmap
  useEffect(() => {
    const fetchPlayerHeatmap = async () => {
      if (!selectedPlayer) {
        setPlayerHeatmap(null);
        return;
      }
      
      try {
        const response = await fetch(
          `${API_URL}/api/v1/player-analytics/player/${selectedPlayer.player_id}/heatmap?grid_size=25`
        );
        if (response.ok) {
          const data = await response.json();
          setPlayerHeatmap(data);
        }
      } catch (err) {
        console.error('Failed to fetch player heatmap:', err);
      }
    };

    fetchPlayerHeatmap();
  }, [selectedPlayer]);

  // Render heatmap on canvas
  useEffect(() => {
    const canvas = heatmapCanvasRef.current;
    if (!canvas) return;

    const heatmapData = selectedPlayer ? playerHeatmap : combinedHeatmap;
    if (!heatmapData || !heatmapData.data) return;

    const ctx = canvas.getContext('2d');
    const { data, grid_width, grid_height } = heatmapData;

    // Set canvas size
    const width = 600;
    const height = Math.floor(width * (68 / 105)); // Football pitch ratio
    canvas.width = width;
    canvas.height = height;

    // Clear canvas
    ctx.fillStyle = '#1a472a';
    ctx.fillRect(0, 0, width, height);

    // Draw pitch lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    
    // Outer boundary
    ctx.strokeRect(10, 10, width - 20, height - 20);
    
    // Center line
    ctx.beginPath();
    ctx.moveTo(width / 2, 10);
    ctx.lineTo(width / 2, height - 10);
    ctx.stroke();
    
    // Center circle
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, 50, 0, Math.PI * 2);
    ctx.stroke();

    // Penalty areas
    const penaltyWidth = 100;
    const penaltyHeight = 180;
    ctx.strokeRect(10, (height - penaltyHeight) / 2, penaltyWidth, penaltyHeight);
    ctx.strokeRect(width - 10 - penaltyWidth, (height - penaltyHeight) / 2, penaltyWidth, penaltyHeight);

    // Draw heatmap cells
    const cellWidth = (width - 20) / grid_width;
    const cellHeight = (height - 20) / grid_height;

    for (let row = 0; row < data.length; row++) {
      for (let col = 0; col < data[row].length; col++) {
        const intensity = data[row][col];
        if (intensity > 0.05) {
          const x = 10 + col * cellWidth;
          const y = 10 + row * cellHeight;
          
          // Color gradient: green -> yellow -> red
          let r, g, b;
          if (intensity < 0.5) {
            r = Math.floor(255 * intensity * 2);
            g = 255;
            b = 0;
          } else {
            r = 255;
            g = Math.floor(255 * (1 - (intensity - 0.5) * 2));
            b = 0;
          }
          
          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.3 + intensity * 0.5})`;
          ctx.fillRect(x, y, cellWidth + 1, cellHeight + 1);
        }
      }
    }
  }, [combinedHeatmap, playerHeatmap, selectedPlayer]);

  const MetricCard = ({ title, value, unit, icon, color = 'cyan' }) => (
    <div className={`bg-slate-800 rounded-lg p-4 border border-slate-700`}>
      <div className="flex items-center gap-3">
        <div className={`text-2xl`}>{icon}</div>
        <div>
          <div className="text-slate-400 text-sm">{title}</div>
          <div className={`text-2xl font-bold text-${color}-400`}>
            {value}
            <span className="text-sm text-slate-500 ml-1">{unit}</span>
          </div>
        </div>
      </div>
    </div>
  );

  const PlayerCard = ({ player, onClick, isSelected }) => {
    const { metrics } = player;
    return (
      <div 
        onClick={() => onClick(player)}
        className={`bg-slate-800 rounded-lg p-4 cursor-pointer transition-all border-2 ${
          isSelected ? 'border-cyan-500 bg-slate-700' : 'border-transparent hover:border-slate-600'
        }`}
      >
        <div className="flex justify-between items-start mb-3">
          <div>
            <span className="text-xl font-bold text-white">Player #{player.track_id}</span>
            <span className={`ml-2 px-2 py-1 rounded text-xs ${
              player.team_side === 'home' ? 'bg-blue-600' : 'bg-red-600'
            }`}>
              {player.team_side || 'Unknown'}
            </span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-slate-400">Distance:</span>
            <span className="ml-2 text-cyan-400">{metrics.total_distance_m.toFixed(0)}m</span>
          </div>
          <div>
            <span className="text-slate-400">Top Speed:</span>
            <span className="ml-2 text-yellow-400">{metrics.top_speed_kmh.toFixed(1)} km/h</span>
          </div>
          <div>
            <span className="text-slate-400">Sprints:</span>
            <span className="ml-2 text-red-400">{metrics.sprint_count}</span>
          </div>
          <div>
            <span className="text-slate-400">Avg Speed:</span>
            <span className="ml-2 text-green-400">{metrics.avg_speed_kmh.toFixed(1)} km/h</span>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-xl">Loading Analytics...</div>
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
          <Link to={`/video/${videoId}/overlay`} className="text-cyan-400 hover:underline mt-4 block">
            ← Back to Video
          </Link>
        </div>
      </div>
    );
  }

  if (!analyticsData || analyticsData.players.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <div className="text-xl">No analytics data available</div>
          <p className="text-slate-400 mt-2">Process the video first to generate tracking data</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const distanceChartData = analyticsData.players.map(p => ({
    name: `#${p.track_id}`,
    distance: p.metrics.total_distance_m,
    sprints: p.metrics.sprint_count * 50, // Scale for visibility
  }));

  const speedChartData = analyticsData.players.map(p => ({
    name: `#${p.track_id}`,
    topSpeed: p.metrics.top_speed_kmh,
    avgSpeed: p.metrics.avg_speed_kmh,
  }));

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to={`/video/${videoId}/overlay`} className="text-slate-400 hover:text-white">
              ← Back to Video
            </Link>
            <h1 className="text-2xl font-bold">📊 Player Analytics</h1>
          </div>
          <div className="flex gap-2">
            {['overview', 'players', 'heatmaps'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg capitalize ${
                  activeTab === tab 
                    ? 'bg-cyan-600 text-white' 
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <MetricCard
            title="Total Players"
            value={analyticsData.total_players}
            icon="👥"
          />
          <MetricCard
            title="Combined Distance"
            value={analyticsData.summary.total_distance_km.toFixed(2)}
            unit="km"
            icon="📏"
            color="green"
          />
          <MetricCard
            title="Avg Team Speed"
            value={analyticsData.summary.avg_team_speed_kmh.toFixed(1)}
            unit="km/h"
            icon="⚡"
            color="yellow"
          />
          <MetricCard
            title="Total Sprints"
            value={analyticsData.summary.total_sprints}
            icon="🏃"
            color="red"
          />
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Distance Chart */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <h3 className="text-lg font-semibold mb-4">Distance Covered by Player</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={distanceChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ background: '#1F2937', border: 'none', borderRadius: '8px' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="distance" fill="#00D4AA" name="Distance (m)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Speed Chart */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <h3 className="text-lg font-semibold mb-4">Speed Analysis</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={speedChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ background: '#1F2937', border: 'none', borderRadius: '8px' }}
                  />
                  <Legend />
                  <Bar dataKey="topSpeed" fill="#FFE66D" name="Top Speed (km/h)" />
                  <Bar dataKey="avgSpeed" fill="#4ECDC4" name="Avg Speed (km/h)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Combined Heatmap */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 md:col-span-2">
              <h3 className="text-lg font-semibold mb-4">Team Heatmap - All Players</h3>
              <div className="flex justify-center">
                <canvas 
                  ref={heatmapCanvasRef} 
                  className="rounded-lg"
                  style={{ maxWidth: '100%' }}
                />
              </div>
              <div className="flex justify-center mt-2 gap-4 text-sm text-slate-400">
                <span>🟢 Low Activity</span>
                <span>🟡 Medium Activity</span>
                <span>🔴 High Activity</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'players' && (
          <div className="grid md:grid-cols-3 gap-4">
            {analyticsData.players.map(player => (
              <PlayerCard 
                key={player.player_id}
                player={player}
                onClick={setSelectedPlayer}
                isSelected={selectedPlayer?.player_id === player.player_id}
              />
            ))}
          </div>
        )}

        {activeTab === 'heatmaps' && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Player selector */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <h3 className="text-lg font-semibold mb-4">Select Player</h3>
              <div className="grid grid-cols-4 gap-2">
                <button
                  onClick={() => setSelectedPlayer(null)}
                  className={`px-3 py-2 rounded ${
                    !selectedPlayer ? 'bg-cyan-600' : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                >
                  All
                </button>
                {analyticsData.players.map(player => (
                  <button
                    key={player.player_id}
                    onClick={() => setSelectedPlayer(player)}
                    className={`px-3 py-2 rounded ${
                      selectedPlayer?.player_id === player.player_id 
                        ? 'bg-cyan-600' 
                        : 'bg-slate-700 hover:bg-slate-600'
                    }`}
                  >
                    #{player.track_id}
                  </button>
                ))}
              </div>
            </div>

            {/* Selected player stats */}
            {selectedPlayer && (
              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <h3 className="text-lg font-semibold mb-4">
                  Player #{selectedPlayer.track_id} Stats
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-slate-400">Distance:</span>
                    <span className="ml-2 text-cyan-400 text-xl font-bold">
                      {selectedPlayer.metrics.total_distance_m.toFixed(0)}m
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Top Speed:</span>
                    <span className="ml-2 text-yellow-400 text-xl font-bold">
                      {selectedPlayer.metrics.top_speed_kmh.toFixed(1)} km/h
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Avg Speed:</span>
                    <span className="ml-2 text-green-400 text-xl font-bold">
                      {selectedPlayer.metrics.avg_speed_kmh.toFixed(1)} km/h
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Sprints:</span>
                    <span className="ml-2 text-red-400 text-xl font-bold">
                      {selectedPlayer.metrics.sprint_count}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Max Acceleration:</span>
                    <span className="ml-2 text-purple-400 text-xl font-bold">
                      {selectedPlayer.metrics.max_acceleration_mps2.toFixed(1)} m/s²
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Stamina Index:</span>
                    <span className="ml-2 text-orange-400 text-xl font-bold">
                      {selectedPlayer.metrics.stamina_index.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Heatmap display */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 md:col-span-2">
              <h3 className="text-lg font-semibold mb-4">
                {selectedPlayer 
                  ? `Player #${selectedPlayer.track_id} Heatmap` 
                  : 'Combined Team Heatmap'}
              </h3>
              <div className="flex justify-center">
                <canvas 
                  ref={heatmapCanvasRef} 
                  className="rounded-lg"
                  style={{ maxWidth: '100%' }}
                />
              </div>
              <div className="flex justify-center mt-2 gap-4 text-sm text-slate-400">
                <span>🟢 Low Activity</span>
                <span>🟡 Medium Activity</span>
                <span>🔴 High Activity</span>
              </div>
            </div>

            {/* Speed time series for selected player */}
            {selectedPlayer && selectedPlayer.metrics.speed_timeseries && (
              <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 md:col-span-2">
                <h3 className="text-lg font-semibold mb-4">
                  Speed Over Time - Player #{selectedPlayer.track_id}
                </h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={selectedPlayer.metrics.speed_timeseries}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="timestamp" 
                      stroke="#9CA3AF"
                      tickFormatter={v => `${v.toFixed(1)}s`}
                    />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ background: '#1F2937', border: 'none', borderRadius: '8px' }}
                      labelFormatter={v => `Time: ${v.toFixed(2)}s`}
                      formatter={v => [`${v.toFixed(2)} m/s`, 'Speed']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#00D4AA" 
                      dot={false}
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerAnalytics;
