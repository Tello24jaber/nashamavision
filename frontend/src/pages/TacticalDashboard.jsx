/**
 * Tactical Dashboard Page - Phase 3
 * Displays formation, positioning, pressing, and tactical metrics
 */

import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { useMatchTactics, useTacticalTimeline } from '../hooks/usePhase3Analytics';

export default function TacticalDashboard() {
  const { matchId } = useParams();
  const [selectedTeam, setSelectedTeam] = useState('home');
  
  const { data: tacticsData, isLoading: loadingTactics } = useMatchTactics(matchId);
  const { data: timelineData, isLoading: loadingTimeline } = useTacticalTimeline(matchId, selectedTeam);

  if (loadingTactics || loadingTimeline) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!tacticsData) {
    return (
      <div className="p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">No tactical data available for this match.</p>
        </div>
      </div>
    );
  }

  const snapshots = selectedTeam === 'home' ? tacticsData.home_snapshots : tacticsData.away_snapshots;
  const latestSnapshot = snapshots.length > 0 ? snapshots[snapshots.length - 1] : null;

  // Prepare data for charts
  const formationTimelineData = timelineData?.formation_timeline?.map(item => ({
    time: (item.timestamp / 60).toFixed(1),
    confidence: (item.confidence * 100).toFixed(1)
  })) || [];

  const pressingData = snapshots.map((snap, idx) => ({
    time: (snap.timestamp / 60).toFixed(1),
    pressing: snap.pressing_intensity.toFixed(1),
    compactness: snap.compactness.toFixed(1)
  }));

  const defensiveLineData = snapshots.map(snap => ({
    time: (snap.timestamp / 60).toFixed(1),
    height: snap.defensive_line_height.toFixed(1),
    blockType: snap.block_type
  }));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Tactical Analysis</h1>
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
        {/* Formation & Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Formation</h3>
            <p className="text-3xl font-bold text-gray-900">{latestSnapshot?.formation || 'N/A'}</p>
            <p className="text-sm text-gray-600 mt-1">
              {latestSnapshot ? `${(latestSnapshot.formation_confidence * 100).toFixed(0)}% confidence` : ''}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Defensive Block</h3>
            <p className="text-3xl font-bold text-gray-900 capitalize">
              {latestSnapshot?.block_type || 'N/A'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {latestSnapshot ? `${latestSnapshot.defensive_line_height.toFixed(1)}m from goal` : ''}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Pressing Intensity</h3>
            <p className="text-3xl font-bold text-gray-900">
              {latestSnapshot ? latestSnapshot.pressing_intensity.toFixed(0) : 'N/A'}
            </p>
            <p className="text-sm text-gray-600 mt-1">0-100 scale</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Team Compactness</h3>
            <p className="text-3xl font-bold text-gray-900">
              {latestSnapshot ? latestSnapshot.compactness.toFixed(0) : 'N/A'}
            </p>
            <p className="text-sm text-gray-600 mt-1">m² area</p>
          </div>
        </div>

        {/* Formation Timeline */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Formation Timeline</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={formationTimelineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  label={{ value: 'Time (min)', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  label={{ value: 'Confidence %', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip />
                <Legend />
                <Bar dataKey="confidence" fill="#3b82f6" name="Formation Confidence %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pressing Intensity Over Time */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pressing Intensity Over Time</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={pressingData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  label={{ value: 'Time (min)', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  label={{ value: 'Intensity', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="pressing" 
                  stroke="#ef4444" 
                  fill="#ef4444" 
                  fillOpacity={0.6}
                  name="Pressing Intensity"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Defensive Line Height */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Defensive Line Height</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={defensiveLineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  label={{ value: 'Time (min)', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  label={{ value: 'Distance from goal (m)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="height" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  name="Line Height (m)"
                  dot={{ r: 1 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Team Shape Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Team Centroid</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Average X Position:</span>
                <span className="font-semibold">
                  {latestSnapshot ? `${latestSnapshot.centroid_x.toFixed(1)}m` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Average Y Position:</span>
                <span className="font-semibold">
                  {latestSnapshot ? `${latestSnapshot.centroid_y.toFixed(1)}m` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Spread X:</span>
                <span className="font-semibold">
                  {latestSnapshot ? `${latestSnapshot.spread_x.toFixed(1)}m` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Spread Y:</span>
                <span className="font-semibold">
                  {latestSnapshot ? `${latestSnapshot.spread_y.toFixed(1)}m` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Line Spacing</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Defense - Midfield:</span>
                <span className="font-semibold">
                  {latestSnapshot ? `${latestSnapshot.line_spacing_def_mid.toFixed(1)}m` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Midfield - Attack:</span>
                <span className="font-semibold">
                  {latestSnapshot ? `${latestSnapshot.line_spacing_mid_att.toFixed(1)}m` : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Average Metrics */}
        {timelineData && (
          <div className="mt-8 bg-blue-50 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Match Averages</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Avg Pressing Intensity</p>
                <p className="text-2xl font-bold text-blue-600">
                  {timelineData.avg_pressing_intensity.toFixed(1)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg Compactness</p>
                <p className="text-2xl font-bold text-blue-600">
                  {timelineData.avg_compactness.toFixed(1)} m²
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg Defensive Line Height</p>
                <p className="text-2xl font-bold text-blue-600">
                  {timelineData.avg_defensive_line_height.toFixed(1)} m
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
