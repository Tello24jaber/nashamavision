/**
 * Empty State Component
 * Shows when no data is available
 */
import React from 'react';
import { Link } from 'react-router-dom';

export default function EmptyState({ 
  icon = '📭',
  title,
  description,
  actionLabel,
  actionTo,
  actionOnClick
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-500 text-center max-w-sm mb-6">{description}</p>
      
      {(actionLabel && (actionTo || actionOnClick)) && (
        actionTo ? (
          <Link
            to={actionTo}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            {actionLabel}
          </Link>
        ) : (
          <button
            onClick={actionOnClick}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            {actionLabel}
          </button>
        )
      )}
    </div>
  );
}

// Preset empty states for common scenarios
export function NoMatchesEmpty() {
  return (
    <EmptyState
      icon="⚽"
      title="No matches yet"
      description="Upload a match video to get started with analytics"
      actionLabel="Upload Video"
      actionTo="/upload"
    />
  );
}

export function NoEventsEmpty() {
  return (
    <EmptyState
      icon="📍"
      title="No events recorded"
      description="Events will appear here once the match video is processed"
    />
  );
}

export function NoPlayersEmpty() {
  return (
    <EmptyState
      icon="👥"
      title="No players detected"
      description="Player tracking data will appear after video processing completes"
    />
  );
}

export function NoDataEmpty() {
  return (
    <EmptyState
      icon="📊"
      title="No data available"
      description="Analytics data will be generated after processing"
    />
  );
}
