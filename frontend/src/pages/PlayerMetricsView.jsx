/**
 * PlayerMetricsView Component
 * Displays comprehensive analytics for a single player
 */
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { usePlayerMetrics, usePlayerTimeSeries } from '../hooks/useAnalytics';
import MetricCard from '../components/MetricCard';

const PlayerMetricsView = () => {
  const { matchId, playerId } = useParams();
  const navigate = useNavigate();

  const { data: metrics, isLoading: metricsLoading } = usePlayerMetrics(playerId, matchId);
  const { data: speedData } = usePlayerTimeSeries(playerId, 'speed', matchId);
  const { data: staminaData } = usePlayerTimeSeries(playerId, 'stamina', matchId);
  const { data: accelData } = usePlayerTimeSeries(playerId, 'acceleration', matchId);

  if (metricsLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading metrics...</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-red-600">No metrics found</div>
      </div>
    );
  }

  // Format chart data
  const formatChartData = (timeSeriesData) => {
    if (!timeSeriesData?.data_points) return [];
    return timeSeriesData.data_points.map((point) => ({
      time: (point.timestamp / 60).toFixed(1), // Convert to minutes
      value: point.value,
    }));
  };

  const speedChartData = formatChartData(speedData);
  const staminaChartData = formatChartData(staminaData);
  const accelChartData = formatChartData(accelData);

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
        <h1 className="text-3xl font-bold text-gray-900">
          Player Analytics - Track #{metrics.track_id}
        </h1>
        <p className="text-gray-600 mt-2">
          {metrics.team_side && `Team: ${metrics.team_side.toUpperCase()}`}
        </p>
      </div>

      {/* Aggregate Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Total Distance"
          value={metrics.total_distance_km.toFixed(2)}
          unit="km"
          icon="🏃"
          color="blue"
        />
        <MetricCard
          label="Top Speed"
          value={metrics.top_speed_kmh.toFixed(1)}
          unit="km/h"
          icon="⚡"
          color="yellow"
        />
        <MetricCard
          label="Average Speed"
          value={metrics.avg_speed_kmh.toFixed(1)}
          unit="km/h"
          icon="📊"
          color="green"
        />
        <MetricCard
          label="Sprint Count"
          value={metrics.sprint_count}
          unit=""
          icon="💨"
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <MetricCard
          label="High Intensity Distance"
          value={metrics.high_intensity_distance_m.toFixed(0)}
          unit="m"
          icon="🔥"
          color="red"
        />
        <MetricCard
          label="Max Acceleration"
          value={metrics.max_acceleration_mps2.toFixed(2)}
          unit="m/s²"
          icon="🚀"
          color="blue"
        />
        <MetricCard
          label="Stamina Index"
          value={metrics.stamina_index.toFixed(1)}
          unit="/100"
          icon="💪"
          color="green"
        />
      </div>

      {/* Speed Over Time Chart */}
      {speedChartData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Speed Over Time</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={speedChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" label={{ value: 'Time (minutes)', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Speed (m/s)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Speed"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Stamina Curve */}
      {staminaChartData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Stamina Curve</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={staminaChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" label={{ value: 'Time (minutes)', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Rolling Avg Speed (m/s)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.3}
                name="Stamina"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Acceleration Profile */}
      {accelChartData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Acceleration Profile</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={accelChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" label={{ value: 'Time (minutes)', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Acceleration (m/s²)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#8b5cf6"
                strokeWidth={2}
                name="Acceleration"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default PlayerMetricsView;
