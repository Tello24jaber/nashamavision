/**
 * Expected Threat (xT) Dashboard - Phase 3
 * Displays xT metrics, heatmaps, and event timeline
 */

import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useMatchXT, useXTGrid } from '../hooks/usePhase3Analytics';

export default function XTDashboard() {
  const { matchId } = useParams();
  const [selectedTeam, setSelectedTeam] = useState('home');
  const canvasRef = useRef(null);
  
  const { data: xtData, isLoading: loadingXT } = useMatchXT(matchId);
  const { data: gridData, isLoading: loadingGrid } = useXTGrid();

  useEffect(() => {
    if (gridData && canvasRef.current) {
      drawXTGrid(gridData);
    }
  }, [gridData]);

  const drawXTGrid = (grid) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const { grid_width, grid_height, values, pitch_length, pitch_width } = grid;

    // Canvas dimensions
    const width = canvas.width;
    const height = canvas.height;
    
    const cellWidth = width / grid_width;
    const cellHeight = height / grid_height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw pitch
    ctx.fillStyle = '#1e7a3e';
    ctx.fillRect(0, 0, width, height);

    // Draw xT grid
    for (let i = 0; i < grid_width; i++) {
      for (let j = 0; j < grid_height; j++) {
        const xtValue = values[i][j];
        
        // Color intensity based on xT value (0-1)
        const intensity = Math.min(255, Math.floor(xtValue * 500));
        ctx.fillStyle = `rgba(255, 0, 0, ${xtValue})`;
        
        const x = i * cellWidth;
        const y = j * cellHeight;
        
        ctx.fillRect(x, y, cellWidth, cellHeight);
        
        // Draw cell border
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.strokeRect(x, y, cellWidth, cellHeight);
      }
    }

    // Draw pitch lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, width, height); // Outer boundary

    // Center line
    ctx.beginPath();
    ctx.moveTo(width / 2, 0);
    ctx.lineTo(width / 2, height);
    ctx.stroke();

    // Center circle
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, 30, 0, 2 * Math.PI);
    ctx.stroke();
  };

  if (loadingXT || loadingGrid) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!xtData) {
    return (
      <div className="p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">No xT data available for this match.</p>
        </div>
      </div>
    );
  }

  const teamData = selectedTeam === 'home' ? xtData.home : xtData.away;
  const opponentData = selectedTeam === 'home' ? xtData.away : xtData.home;

  // Sort players by danger score
  const sortedPlayers = [...teamData.player_summaries].sort((a, b) => b.danger_score - a.danger_score);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Expected Threat (xT) Analysis</h1>
              <p className="mt-1 text-sm text-gray-500">Match ID: {matchId}</p>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedTeam('home')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedTeam === 'home'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Home Team
              </button>
              <button
                onClick={() => setSelectedTeam('away')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedTeam === 'away'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Away Team
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Team xT Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Team xT Score</h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-bold text-blue-600">
                  {teamData.total_xt.toFixed(2)}
                </p>
                <p className="text-sm text-gray-600 mt-1">Total Expected Threat</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-semibold text-gray-400">
                  {opponentData.total_xt.toFixed(2)}
                </p>
                <p className="text-xs text-gray-500">Opponent</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">xT Breakdown</h2>
            <div className="space-y-2">
              {sortedPlayers.slice(0, 1).map(player => (
                <div key={player.player_id}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">Passes:</span>
                    <span className="font-semibold">{player.pass_xt.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">Carries:</span>
                    <span className="font-semibold">{player.carry_xt.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Shots:</span>
                    <span className="font-semibold">{player.shot_xt.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* xT Grid Visualization */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">xT Grid (Baseline Values)</h2>
          <div className="flex justify-center">
            <canvas 
              ref={canvasRef} 
              width={800} 
              height={520}
              className="border-2 border-gray-300 rounded"
            />
          </div>
          <div className="mt-4 flex items-center justify-center space-x-4">
            <div className="flex items-center">
              <div className="w-12 h-4 bg-gradient-to-r from-green-500 to-red-500"></div>
              <span className="ml-2 text-sm text-gray-600">Low → High Threat</span>
            </div>
          </div>
        </div>

        {/* Player xT Rankings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Player xT Rankings</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Player ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total xT
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Danger Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Passes
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Carries
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Shots
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedPlayers.map((player, index) => (
                  <tr key={player.player_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {player.player_id.substring(0, 8)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                      {player.total_xt_gain.toFixed(3)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 font-semibold">
                      {player.danger_score.toFixed(1)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {player.num_passes} ({player.pass_xt.toFixed(3)})
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {player.num_carries} ({player.carry_xt.toFixed(3)})
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {player.num_shots} ({player.shot_xt.toFixed(3)})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
