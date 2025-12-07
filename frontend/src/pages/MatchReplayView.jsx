/**
 * MatchReplayView Page
 * Phase 4: Virtual Match Engine
 * 
 * Main replay page with pitch, controls, and sidebar
 */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useReplaySummary, useReplayTimeline } from '../hooks/useReplayData';
import { useReplayController } from '../hooks/useReplayController';
import ReplayPitch from '../components/replay/ReplayPitch';
import ReplayControls from '../components/replay/ReplayControls';
import ReplaySidebar from '../components/replay/ReplaySidebar';

const MatchReplayView = () => {
  const { matchId } = useParams();
  
  // State
  const [highlightedPlayerId, setHighlightedPlayerId] = useState(null);
  const [showTrails, setShowTrails] = useState(false);
  const [showBallTrail, setShowBallTrail] = useState(false);
  const [showEventOverlay, setShowEventOverlay] = useState(true);
  const [debugMode, setDebugMode] = useState(false);
  const [selectedSegment, setSelectedSegment] = useState('full');
  
  // Fetch data
  const { data: summary, isLoading: summaryLoading, error: summaryError } = useReplaySummary(matchId);
  const { data: timeline, isLoading: timelineLoading, error: timelineError } = useReplayTimeline(matchId, {
    fps: 10,
    includeBall: true,
    includeEvents: true,
  });
  
  // Replay controller
  const {
    isPlaying,
    currentTime,
    playbackSpeed,
    duration,
    progress,
    play,
    pause,
    togglePlay,
    stop,
    seek,
    jumpToEvent,
    skipForward,
    skipBackward,
    changeSpeed,
  } = useReplayController(timeline?.duration || 0);
  
  // Handle player click
  const handlePlayerClick = (player) => {
    if (highlightedPlayerId === player.player_id) {
      setHighlightedPlayerId(null);
      setShowTrails(false);
    } else {
      setHighlightedPlayerId(player.player_id);
      setShowTrails(true);
    }
  };
  
  // Handle event click
  const handleEventClick = (event) => {
    jumpToEvent(event.t);
  };
  
  // Loading state
  if (summaryLoading || timelineLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading replay data...</p>
        </div>
      </div>
    );
  }
  
  // Error state
  if (summaryError || timelineError) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 max-w-md">
          <h3 className="text-red-500 text-xl font-bold mb-2">Error Loading Replay</h3>
          <p className="text-gray-300">
            {summaryError?.message || timelineError?.message || 'Failed to load replay data'}
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="mb-4">
          <h1 className="text-3xl font-bold text-white mb-2">
            Match Replay: {summary?.match_name}
          </h1>
          <div className="flex items-center space-x-4 text-gray-400">
            <span>{summary?.home_team} vs {summary?.away_team}</span>
            {summary?.match_date && (
              <span>
                {new Date(summary.match_date).toLocaleDateString()}
              </span>
            )}
            <span>Duration: {Math.floor(summary?.duration / 60)}min</span>
          </div>
        </div>
        
        {/* Segment Selector */}
        {summary?.segments && summary.segments.length > 1 && (
          <div className="mb-4 flex space-x-2">
            {summary.segments.map((segment) => (
              <button
                key={segment.id}
                onClick={() => setSelectedSegment(segment.id)}
                className={`px-4 py-2 rounded ${
                  selectedSegment === segment.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                } transition`}
              >
                {segment.name}
              </button>
            ))}
          </div>
        )}
        
        {/* Main Layout */}
        <div className="grid grid-cols-12 gap-4">
          {/* Pitch and Controls */}
          <div className="col-span-12 lg:col-span-9 space-y-4">
            {/* Pitch */}
            <div className="bg-gray-800 rounded-lg p-4">
              <ReplayPitch
                width={1100}
                height={700}
                players={timeline?.players || []}
                ball={timeline?.ball || []}
                currentTime={currentTime}
                events={timeline?.events || []}
                highlightedPlayerId={highlightedPlayerId}
                showTrails={showTrails}
                showEventOverlay={showEventOverlay}
                debugMode={debugMode}
                onPlayerClick={handlePlayerClick}
              />
            </div>
            
            {/* Controls */}
            <ReplayControls
              isPlaying={isPlaying}
              currentTime={currentTime}
              duration={duration}
              playbackSpeed={playbackSpeed}
              onPlay={play}
              onPause={pause}
              onStop={stop}
              onSeek={seek}
              onSpeedChange={changeSpeed}
              onSkipForward={skipForward}
              onSkipBackward={skipBackward}
            />
          </div>
          
          {/* Sidebar */}
          <div className="col-span-12 lg:col-span-3">
            <ReplaySidebar
              players={timeline?.players || []}
              events={timeline?.events || []}
              currentTime={currentTime}
              highlightedPlayerId={highlightedPlayerId}
              onPlayerClick={handlePlayerClick}
              onEventClick={handleEventClick}
              showBallTrail={showBallTrail}
              onToggleBallTrail={setShowBallTrail}
              debugMode={debugMode}
              onToggleDebugMode={setDebugMode}
            />
          </div>
        </div>
        
        {/* Info Panel */}
        <div className="mt-4 bg-gray-800 rounded-lg p-4">
          <h3 className="text-white font-semibold mb-2">Match Information</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-gray-400">Total Players</div>
              <div className="text-white text-xl font-bold">
                {summary?.players?.length || 0}
              </div>
            </div>
            <div>
              <div className="text-gray-400">Total Events</div>
              <div className="text-white text-xl font-bold">
                {summary?.total_events || 0}
              </div>
            </div>
            <div>
              <div className="text-gray-400">Current Time</div>
              <div className="text-white text-xl font-bold">
                {Math.floor(currentTime / 60)}:{String(Math.floor(currentTime % 60)).padStart(2, '0')}
              </div>
            </div>
            <div>
              <div className="text-gray-400">Playback Speed</div>
              <div className="text-white text-xl font-bold">{playbackSpeed}x</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MatchReplayView;
