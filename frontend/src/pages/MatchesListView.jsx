/**
 * Matches List View
 * Shows all matches with filtering and search
 */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMatches } from '../hooks/useAnalytics';
import Breadcrumbs from '../components/layout/Breadcrumbs';
import { MatchListSkeleton } from '../components/common/LoadingSkeleton';
import { NoMatchesEmpty } from '../components/common/EmptyState';

export default function MatchesListView() {
  const { data: matches, isLoading } = useMatches();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredMatches = matches?.filter(match => 
    match.home_team?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    match.away_team?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumbs items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Matches' }
        ]} />

        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">All Matches</h1>
            <p className="text-slate-500 mt-1">
              {matches?.length || 0} total matches
            </p>
          </div>
          <Link
            to="/upload"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center space-x-2"
          >
            <span>+</span>
            <span>Upload Match</span>
          </Link>
        </div>

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search matches by team name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full max-w-md px-4 py-3 rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
          />
        </div>

        {/* Matches List */}
        {isLoading ? (
          <MatchListSkeleton />
        ) : !filteredMatches || filteredMatches.length === 0 ? (
          <NoMatchesEmpty />
        ) : (
          <div className="space-y-4">
            {filteredMatches.map(match => (
              <MatchCard key={match.id} match={match} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MatchCard({ match }) {
  const statusColors = {
    completed: 'bg-green-100 text-green-800',
    processing: 'bg-yellow-100 text-yellow-800',
    pending: 'bg-slate-100 text-slate-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <Link
      to={`/matches/${match.id}`}
      className="block bg-white rounded-xl shadow-sm hover:shadow-md transition-all p-6 border border-transparent hover:border-blue-200"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-4 mb-3">
            <h3 className="text-xl font-semibold text-slate-900">
              {match.home_team} vs {match.away_team}
            </h3>
            {match.home_score !== null && match.away_score !== null && (
              <span className="text-2xl font-bold text-slate-600">
                {match.home_score} - {match.away_score}
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-slate-500">
            <span>📅 {new Date(match.match_date).toLocaleDateString()}</span>
            {match.competition && <span>🏆 {match.competition}</span>}
            {match.venue && <span>🏟️ {match.venue}</span>}
          </div>
        </div>

        <div className="flex flex-col items-end space-y-2">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[match.processing_status] || statusColors.pending}`}>
            {match.processing_status || 'pending'}
          </span>
          
          <span className="text-blue-600 font-medium text-sm hover:underline flex items-center space-x-1">
            <span>View Details</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </Link>
  );
}
