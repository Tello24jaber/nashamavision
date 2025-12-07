/**
 * MatchDetailsView Component
 * Main match page with navigation to analytics features
 */
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMatch, useMatchAnalytics, useMatchPlayers } from '../hooks/useAnalytics';
import MetricCard from '../components/MetricCard';

const MatchDetailsView = () => {
  const { matchId } = useParams();
  const navigate = useNavigate();

  const { data: match, isLoading: matchLoading } = useMatch(matchId);
  const { data: analytics, isLoading: analyticsLoading } = useMatchAnalytics(matchId);
  const { data: players, isLoading: playersLoading, error: playersError } = useMatchPlayers(matchId);

  if (matchLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading match data...</div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-red-600">Match not found</div>
      </div>
    );
  }

  // Check if video needs processing (players endpoint returns 404)
  const needsProcessing = playersError?.response?.status === 404;
  
  const homePlayers = players?.players?.filter(p => p.team_side === 'home') || [];
  const awayPlayers = players?.players?.filter(p => p.team_side === 'away') || [];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/matches')}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Matches
        </button>
        <h1 className="text-4xl font-bold text-gray-900">{match.name}</h1>
        <div className="text-lg text-gray-600 mt-2">
          {match.home_team} vs {match.away_team}
        </div>
        {match.match_date && (
          <div className="text-sm text-gray-500 mt-1">
            {new Date(match.match_date).toLocaleDateString()}
          </div>
        )}
      </div>

      {/* Processing Required Banner */}
      {needsProcessing && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 mb-8 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-lg font-medium text-yellow-800">
                Video Processing Required
              </h3>
              <p className="mt-2 text-sm text-yellow-700">
                This match has uploaded videos but they haven't been processed yet. 
                Process the video to generate player tracking, analytics, and heatmaps.
              </p>
              <div className="mt-4">
                <button
                  onClick={() => {
                    fetch(`http://127.0.0.1:8000/api/v1/videos/match/${matchId}`)
                      .then(res => res.json())
                      .then(data => {
                        if (data.videos && data.videos.length > 0) {
                          navigate(`/matches/${matchId}/videos/${data.videos[0].id}/process`);
                        }
                      });
                  }}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition font-medium"
                >
                  ⚙️ Process Video Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Match Statistics */}
      {analytics && !needsProcessing && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Match Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="Total Players"
              value={analytics.total_players}
              icon="👥"
              color="blue"
            />
            <MetricCard
              label="Total Distance"
              value={analytics.total_distance_covered_km.toFixed(1)}
              unit="km"
              icon="🏃"
              color="green"
            />
            <MetricCard
              label="Max Speed"
              value={analytics.max_speed_kmh.toFixed(1)}
              unit="km/h"
              icon="⚡"
              color="yellow"
            />
            <MetricCard
              label="Total Sprints"
              value={analytics.total_sprints}
              icon="💨"
              color="purple"
            />
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4">Analytics Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => {
              // Get the first video for this match
              fetch(`http://127.0.0.1:8000/api/v1/videos/match/${matchId}`)
                .then(res => res.json())
                .then(data => {
                  if (data.videos && data.videos.length > 0) {
                    navigate(`/videos/${data.videos[0].id}/overlay`);
                  } else {
                    alert('No video found for this match. Please upload a video first.');
                  }
                })
                .catch(() => alert('Error loading video'));
            }}
            className="p-6 bg-purple-50 hover:bg-purple-100 rounded-lg border-2 border-purple-200 text-left transition"
          >
            <div className="text-3xl mb-2">🎥</div>
            <div className="text-lg font-bold text-purple-900">View Video</div>
            <div className="text-sm text-purple-700 mt-1">
              Watch video with player tracking
            </div>
          </button>

          <button
            onClick={() => {
              fetch(`http://127.0.0.1:8000/api/v1/videos/match/${matchId}`)
                .then(res => res.json())
                .then(data => {
                  if (data.videos && data.videos.length > 0) {
                    navigate(`/videos/${data.videos[0].id}/player-analysis`);
                  } else {
                    alert('No video found');
                  }
                })
                .catch(() => alert('Error loading video'));
            }}
            className="p-6 bg-blue-50 hover:bg-blue-100 rounded-lg border-2 border-blue-200 text-left transition"
          >
            <div className="text-3xl mb-2">📊</div>
            <div className="text-lg font-bold text-blue-900">Player Analytics</div>
            <div className="text-sm text-blue-700 mt-1">
              Detailed metrics & heatmaps per player
            </div>
          </button>

          <button
            onClick={() => {
              fetch(`http://127.0.0.1:8000/api/v1/videos/match/${matchId}`)
                .then(res => res.json())
                .then(data => {
                  if (data.videos && data.videos.length > 0) {
                    navigate(`/videos/${data.videos[0].id}/analytics`);
                  } else {
                    alert('No video found');
                  }
                })
                .catch(() => alert('Error loading video'));
            }}
            className="p-6 bg-red-50 hover:bg-red-100 rounded-lg border-2 border-red-200 text-left transition"
          >
            <div className="text-3xl mb-2">🗺️</div>
            <div className="text-lg font-bold text-red-900">Team Overview</div>
            <div className="text-sm text-red-700 mt-1">
              All players analytics & heatmaps
            </div>
          </button>

          <button
            onClick={() => navigate(`/matches/${matchId}/team-comparison`)}
            className="p-6 bg-green-50 hover:bg-green-100 rounded-lg border-2 border-green-200 text-left transition"
          >
            <div className="text-3xl mb-2">⚽</div>
            <div className="text-lg font-bold text-green-900">Team Comparison</div>
            <div className="text-sm text-green-700 mt-1">
              Compare team performance metrics
            </div>
          </button>
        </div>
      </div>

      {/* Player Lists */}
      {!needsProcessing && players && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Home Team */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">
              {match.home_team} ({homePlayers.length})
            </h2>
            <div className="space-y-2">
              {homePlayers.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No players tracked yet</p>
              ) : (
                homePlayers.map((player) => (
              <div
                key={player.player_id}
                className="flex items-center justify-between p-3 bg-blue-50 rounded-lg hover:bg-blue-100 cursor-pointer transition"
                onClick={() =>
                  navigate(`/matches/${matchId}/player/${player.player_id}/metrics`)
                }
              >
                <div>
                  <div className="font-medium">Track #{player.track_id}</div>
                  <div className="text-sm text-gray-600">
                    {player.total_detections} detections
                  </div>
                </div>
                <button className="text-blue-600 hover:text-blue-800">
                  View Analytics →
                </button>
              </div>
                ))
              )}
            </div>
          </div>

          {/* Away Team */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">
              {match.away_team} ({awayPlayers.length})
            </h2>
            <div className="space-y-2">
              {awayPlayers.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No players tracked yet</p>
              ) : (
                awayPlayers.map((player) => (
                  <div
                    key={player.player_id}
                    className="flex items-center justify-between p-3 bg-red-50 rounded-lg hover:bg-red-100 cursor-pointer transition"
                    onClick={() =>
                      navigate(`/matches/${matchId}/player/${player.player_id}/metrics`)
                    }
                  >
                    <div>
                      <div className="font-medium">Track #{player.track_id}</div>
                      <div className="text-sm text-gray-600">
                        {player.total_detections} detections
                      </div>
                    </div>
                    <button className="text-red-600 hover:text-red-800">
                      View Analytics →
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MatchDetailsView;
