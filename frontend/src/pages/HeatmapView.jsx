/**
 * HeatmapView Component
 * Display player or team heatmaps
 */
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePlayerHeatmap, useTeamHeatmap, useMatchPlayers } from '../hooks/useAnalytics';
import HeatmapCanvas from '../components/HeatmapCanvas';

const HeatmapView = () => {
  const { matchId, playerId } = useParams();
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState('player'); // 'player' or 'team'
  const [selectedTeam, setSelectedTeam] = useState('home');

  const { data: playerHeatmap, isLoading: playerLoading } = usePlayerHeatmap(
    playerId,
    matchId
  );
  
  const { data: teamHeatmap, isLoading: teamLoading } = useTeamHeatmap(
    viewMode === 'team' ? matchId : null,
    selectedTeam
  );

  const { data: players } = useMatchPlayers(matchId);

  const isLoading = viewMode === 'player' ? playerLoading : teamLoading;
  const heatmapData = viewMode === 'player' ? playerHeatmap : teamHeatmap;

  const handlePlayerChange = (newPlayerId) => {
    navigate(`/matches/${matchId}/player/${newPlayerId}/heatmap`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(`/matches/${matchId}`)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Match
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Position Heatmap</h1>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-wrap gap-4">
          {/* View Mode Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('player')}
              className={`px-4 py-2 rounded-lg ${
                viewMode === 'player'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Player Heatmap
            </button>
            <button
              onClick={() => setViewMode('team')}
              className={`px-4 py-2 rounded-lg ${
                viewMode === 'team'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Team Heatmap
            </button>
          </div>

          {/* Player Selector */}
          {viewMode === 'player' && players && (
            <select
              value={playerId}
              onChange={(e) => handlePlayerChange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              {players.players.map((player) => (
                <option key={player.player_id} value={player.player_id}>
                  Track #{player.track_id} - {player.team_side || 'Unknown'}
                </option>
              ))}
            </select>
          )}

          {/* Team Selector */}
          {viewMode === 'team' && (
            <select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="home">Home Team</option>
              <option value="away">Away Team</option>
            </select>
          )}
        </div>
      </div>

      {/* Heatmap Display */}
      <div className="bg-white rounded-lg shadow p-6">
        {isLoading && (
          <div className="flex items-center justify-center h-96">
            <div className="text-xl">Loading heatmap...</div>
          </div>
        )}

        {!isLoading && !heatmapData && (
          <div className="flex items-center justify-center h-96">
            <div className="text-xl text-red-600">No heatmap data available</div>
          </div>
        )}

        {!isLoading && heatmapData && (
          <div className="flex flex-col items-center">
            <HeatmapCanvas heatmapData={heatmapData} width={900} height={585} />
            
            {/* Legend */}
            <div className="mt-6 flex items-center gap-4">
              <span className="text-sm font-medium">Intensity:</span>
              <div className="flex items-center gap-2">
                <div className="w-20 h-6 bg-gradient-to-r from-transparent to-red-600 rounded"></div>
                <span className="text-sm">Low → High</span>
              </div>
            </div>

            {/* Stats */}
            <div className="mt-6 grid grid-cols-3 gap-4 w-full max-w-2xl">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold">{heatmapData.total_positions}</div>
                <div className="text-sm text-gray-600">Total Positions</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold">
                  {heatmapData.grid_width} × {heatmapData.grid_height}
                </div>
                <div className="text-sm text-gray-600">Grid Size</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold">
                  {heatmapData.pitch_length} × {heatmapData.pitch_width}
                </div>
                <div className="text-sm text-gray-600">Pitch Dimensions (m)</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HeatmapView;
