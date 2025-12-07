/**
 * Events Timeline Page - Phase 3
 * Displays detected events (passes, carries, shots) with timeline visualization
 */

import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMatchEvents } from '../hooks/usePhase3Analytics';

const EVENT_COLORS = {
  pass: 'bg-blue-500',
  carry: 'bg-green-500',
  shot: 'bg-red-500',
  dribble: 'bg-yellow-500'
};

const EVENT_ICONS = {
  pass: '⚡',
  carry: '🏃',
  shot: '⚽',
  dribble: '💨'
};

export default function EventsTimeline() {
  const { matchId } = useParams();
  const [selectedEventType, setSelectedEventType] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  
  const { data: eventsData, isLoading } = useMatchEvents(matchId, selectedEventType);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!eventsData) {
    return (
      <div className="p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">No events data available for this match.</p>
        </div>
      </div>
    );
  }

  // Sort events by timestamp
  const sortedEvents = [...eventsData.events].sort((a, b) => a.timestamp - b.timestamp);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Events Timeline</h1>
              <p className="mt-1 text-sm text-gray-500">Match ID: {matchId}</p>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => setSelectedEventType(null)}
                className={`px-4 py-2 rounded-lg font-medium ${
                  !selectedEventType
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                All Events
              </button>
              <button
                onClick={() => setSelectedEventType('pass')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedEventType === 'pass'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Passes
              </button>
              <button
                onClick={() => setSelectedEventType('carry')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedEventType === 'carry'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Carries
              </button>
              <button
                onClick={() => setSelectedEventType('shot')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedEventType === 'shot'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Shots
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Events</p>
                <p className="text-3xl font-bold text-gray-900">{eventsData.total_events}</p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Passes</p>
                <p className="text-3xl font-bold text-blue-900">{eventsData.num_passes}</p>
              </div>
              <div className="text-4xl">{EVENT_ICONS.pass}</div>
            </div>
          </div>

          <div className="bg-green-50 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600">Carries</p>
                <p className="text-3xl font-bold text-green-900">{eventsData.num_carries}</p>
              </div>
              <div className="text-4xl">{EVENT_ICONS.carry}</div>
            </div>
          </div>

          <div className="bg-red-50 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Shots</p>
                <p className="text-3xl font-bold text-red-900">{eventsData.num_shots}</p>
              </div>
              <div className="text-4xl">{EVENT_ICONS.shot}</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Events List */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Event Timeline</h2>
              <p className="text-sm text-gray-500 mt-1">
                {sortedEvents.length} events detected
              </p>
            </div>
            
            <div className="p-6 space-y-3 max-h-[600px] overflow-y-auto">
              {sortedEvents.map((event, index) => (
                <div
                  key={event.id}
                  onClick={() => setSelectedEvent(event)}
                  className={`p-4 border-l-4 rounded cursor-pointer transition-all hover:shadow-md ${
                    EVENT_COLORS[event.event_type] || 'bg-gray-500'
                  } bg-white hover:bg-gray-50 ${
                    selectedEvent?.id === event.id ? 'ring-2 ring-blue-500' : ''
                  }`}
                  style={{ borderLeftColor: getEventColor(event.event_type) }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{EVENT_ICONS[event.event_type] || '📍'}</span>
                      <div>
                        <p className="font-semibold text-gray-900 capitalize">
                          {event.event_type}
                        </p>
                        <p className="text-xs text-gray-500">
                          Time: {formatTimestamp(event.timestamp)} | 
                          Team: {event.team_side}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-600">
                        {event.distance.toFixed(1)}m
                      </p>
                      <p className="text-xs text-gray-500">
                        {event.velocity.toFixed(1)} m/s
                      </p>
                      {event.xt_value && (
                        <p className="text-xs font-semibold text-blue-600">
                          xT: {event.xt_value > 0 ? '+' : ''}{event.xt_value.toFixed(3)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Event Details Panel */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Event Details</h2>
            </div>
            
            {selectedEvent ? (
              <div className="p-6 space-y-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Event Type</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-2xl">{EVENT_ICONS[selectedEvent.event_type]}</span>
                    <p className="text-lg font-semibold capitalize">{selectedEvent.event_type}</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-500">Team</p>
                  <p className="text-lg font-semibold capitalize">{selectedEvent.team_side}</p>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-500">Timestamp</p>
                  <p className="text-lg">{formatTimestamp(selectedEvent.timestamp)}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Distance</p>
                    <p className="text-lg font-semibold">{selectedEvent.distance.toFixed(2)}m</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Duration</p>
                    <p className="text-lg font-semibold">{selectedEvent.duration.toFixed(2)}s</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-500">Velocity</p>
                  <p className="text-lg font-semibold">{selectedEvent.velocity.toFixed(2)} m/s</p>
                </div>

                {selectedEvent.xt_value && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Expected Threat (xT)</p>
                    <p className={`text-xl font-bold ${
                      selectedEvent.xt_value > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {selectedEvent.xt_value > 0 ? '+' : ''}{selectedEvent.xt_value.toFixed(4)}
                    </p>
                  </div>
                )}

                <div>
                  <p className="text-sm font-medium text-gray-500 mb-2">Position</p>
                  <div className="bg-gray-50 rounded p-3 space-y-1">
                    <p className="text-sm">
                      <span className="font-medium">Start:</span> ({selectedEvent.start_x.toFixed(1)}, {selectedEvent.start_y.toFixed(1)})
                    </p>
                    <p className="text-sm">
                      <span className="font-medium">End:</span> ({selectedEvent.end_x.toFixed(1)}, {selectedEvent.end_y.toFixed(1)})
                    </p>
                  </div>
                </div>

                {selectedEvent.metadata && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">Additional Info</p>
                    <div className="bg-gray-50 rounded p-3">
                      <pre className="text-xs overflow-auto">
                        {JSON.stringify(selectedEvent.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-6 text-center text-gray-500">
                <p>Select an event to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper functions
function formatTimestamp(timestamp) {
  const minutes = Math.floor(timestamp / 60);
  const seconds = Math.floor(timestamp % 60);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function getEventColor(eventType) {
  const colors = {
    pass: '#3b82f6',
    carry: '#10b981',
    shot: '#ef4444',
    dribble: '#f59e0b'
  };
  return colors[eventType] || '#6b7280';
}
