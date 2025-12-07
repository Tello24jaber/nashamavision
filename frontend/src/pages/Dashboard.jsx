/**
 * Dashboard - Main Landing Page
 * Modern, professional design with dark/light gradient theme
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { matchApi } from '../services/api';

function Dashboard() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      setLoading(true);
      const response = await matchApi.getAll();
      setMatches(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load matches');
      console.error('Error loading matches:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl"></div>
          <div className="absolute top-60 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 right-1/4 w-60 h-60 bg-cyan-500/10 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                  <span className="text-2xl">⚽</span>
                </div>
                <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-sm font-medium rounded-full border border-emerald-500/30">
                  v2.0 Active
                </span>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
                Welcome to <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Nashama Vision</span>
              </h1>
              <p className="text-slate-400 text-lg max-w-xl">
                Professional Football Analytics Platform with AI-Powered Insights, Player Tracking, and Real-Time Match Analysis
              </p>
            </div>
            <Link
              to="/upload"
              className="hidden md:flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-xl font-medium shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-300"
            >
              <span className="text-xl">📤</span>
              <span>Upload Match</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Overview - Floating Cards */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10 -mt-6">
          <StatCard
            icon="📊"
            value={matches.length}
            label="Total Matches"
            color="blue"
          />
          <StatCard
            icon="👥"
            value="∞"
            label="Players Tracked"
            color="purple"
          />
          <StatCard
            icon="🤖"
            value="AI"
            label="Powered Analysis"
            color="cyan"
          />
          <StatCard
            icon="🎯"
            value="Real-time"
            label="Processing"
            color="emerald"
          />
        </div>

        {/* Recent Matches Section */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 overflow-hidden">
          <div className="p-6 border-b border-slate-700/50 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Recent Matches</h2>
              <p className="text-sm text-slate-400 mt-1">Analyze and track your uploaded matches</p>
            </div>
            <button
              onClick={loadMatches}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
            >
              <span>🔄</span>
              <span className="text-sm font-medium">Refresh</span>
            </button>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="text-center py-16">
                <div className="inline-block w-12 h-12 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
                <p className="mt-4 text-slate-400">Loading matches...</p>
              </div>
            ) : error ? (
              <div className="text-center py-16">
                <div className="text-5xl mb-4">⚠️</div>
                <p className="text-red-400 mb-4">{error}</p>
                <button
                  onClick={loadMatches}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : matches.length === 0 ? (
              <div className="text-center py-16">
                <div className="text-6xl mb-4">📭</div>
                <p className="text-slate-300 text-lg font-medium mb-2">No matches yet</p>
                <p className="text-slate-500 mb-6">Upload your first match video to get started</p>
                <Link
                  to="/upload"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-medium hover:from-blue-500 hover:to-cyan-500 transition-all"
                >
                  <span>📤</span>
                  <span>Upload Match</span>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {matches.map((match) => (
                  <MatchCard key={match.id} match={match} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-10">
          <h2 className="text-xl font-bold text-white mb-6">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <QuickActionCard to="/upload" icon="📤" label="Upload" color="blue" />
            <QuickActionCard to="/matches" icon="⚽" label="Matches" color="emerald" />
            <QuickActionCard to="/assistant" icon="🤖" label="AI Assistant" color="purple" />
            <QuickActionCard to="/settings" icon="⚙️" label="Settings" color="slate" />
            <QuickActionCard to="/reports" icon="📊" label="Reports" color="cyan" />
          </div>
        </div>

        {/* Features Showcase */}
        <div className="mt-10 grid md:grid-cols-3 gap-6">
          <FeatureCard
            icon="🎯"
            title="Player Detection"
            description="AI-powered YOLO model automatically detects and tracks players across all frames"
          />
          <FeatureCard
            icon="🗺️"
            title="2D Pitch View"
            description="Convert video footage into interactive 2D tactical visualization"
          />
          <FeatureCard
            icon="🔥"
            title="Heatmaps"
            description="Generate detailed position heatmaps for individual players or teams"
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-slate-500 text-sm">
            Nashama Vision v2.0 • Powered by AI & Computer Vision • Built with ❤️
          </p>
        </div>
      </footer>
    </div>
  );
}

function StatCard({ icon, value, label, color }) {
  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/30',
    purple: 'from-purple-500/20 to-purple-500/5 border-purple-500/30',
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30',
    emerald: 'from-emerald-500/20 to-emerald-500/5 border-emerald-500/30',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} backdrop-blur-sm rounded-xl p-6 border`}>
      <div className="flex items-center gap-4">
        <div className="text-3xl">{icon}</div>
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          <p className="text-sm text-slate-400">{label}</p>
        </div>
      </div>
    </div>
  );
}

function MatchCard({ match }) {
  return (
    <Link
      to={`/matches/${match.id}`}
      className="group block bg-slate-900/50 rounded-xl p-5 border border-slate-700/50 hover:border-blue-500/50 hover:bg-slate-900/70 transition-all duration-300"
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-slate-500">
          {new Date(match.date).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
          })}
        </span>
        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-medium rounded-full">
          ✓ Uploaded
        </span>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="font-semibold text-white group-hover:text-blue-400 transition-colors">
            {match.home_team}
          </p>
        </div>
        <div className="px-4 py-2 bg-slate-800 rounded-lg mx-4 min-w-[80px] text-center">
          <span className="text-lg font-bold text-white">
            {match.home_score || 0} - {match.away_score || 0}
          </span>
        </div>
        <div className="flex-1 text-right">
          <p className="font-semibold text-white group-hover:text-blue-400 transition-colors">
            {match.away_team}
          </p>
        </div>
      </div>
      
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700/50">
        <span className="text-sm text-slate-500">📍 {match.venue || 'Stadium'}</span>
        <span className="text-sm text-blue-400 font-medium group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
          View Details <span>→</span>
        </span>
      </div>
    </Link>
  );
}

function QuickActionCard({ to, icon, label, color }) {
  const colorClasses = {
    blue: 'hover:border-blue-500/50 hover:shadow-blue-500/10',
    emerald: 'hover:border-emerald-500/50 hover:shadow-emerald-500/10',
    purple: 'hover:border-purple-500/50 hover:shadow-purple-500/10',
    cyan: 'hover:border-cyan-500/50 hover:shadow-cyan-500/10',
    slate: 'hover:border-slate-500/50 hover:shadow-slate-500/10',
  };

  return (
    <Link
      to={to}
      className={`block bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50 text-center hover:bg-slate-800/70 hover:shadow-lg ${colorClasses[color]} transition-all duration-300`}
    >
      <div className="text-3xl mb-3">{icon}</div>
      <p className="font-medium text-white">{label}</p>
    </Link>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
      <div className="text-3xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-400">{description}</p>
    </div>
  );
}

export default Dashboard;
