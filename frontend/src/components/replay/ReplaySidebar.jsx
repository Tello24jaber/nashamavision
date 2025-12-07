/**
 * ReplaySidebar Component
 * Phase 4: Virtual Match Engine
 * 
 * Sidebar with player list, event filters, and statistics
 */
import React, { useState, useMemo } from 'react';

const ReplaySidebar = ({
  players = [],
  events = [],
  currentTime,
  highlightedPlayerId,
  onPlayerClick,
  onEventClick,
  showBallTrail,
  onToggleBallTrail,
  debugMode,
  onToggleDebugMode,
}) => {
  const [eventFilter, setEventFilter] = useState('all');
  const [teamFilter, setTeamFilter] = useState('all');
  
  // Group players by team
  const playersByTeam = useMemo(() => {
    const grouped = {
      home: [],
      away: [],
      other: [],
    };
    
    players.forEach((player) => {
      if (player.team === 'home') {
        grouped.home.push(player);
      } else if (player.team === 'away') {
        grouped.away.push(player);
      } else {
        grouped.other.push(player);
      }
    });
    
    return grouped;
  }, [players]);
  
  // Filter events
  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      if (eventFilter !== 'all' && event.type !== eventFilter) {
        return false;
      }
      return true;
    });
  }, [events, eventFilter]);
  
  // Event statistics
  const eventStats = useMemo(() => {
    const stats = {
      total: events.length,
      pass: 0,
      carry: 0,
      shot: 0,
    };
    
    events.forEach((event) => {
      if (event.type === 'pass') stats.pass++;
      else if (event.type === 'carry') stats.carry++;
      else if (event.type === 'shot') stats.shot++;
    });
    
    return stats;
  }, [events]);
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  return (
    <div className="bg-gray-800 rounded-lg p-4 h-full overflow-y-auto space-y-6">
      {/* Event Statistics */}
      <div className="space-y-2">
        <h3 className="text-white font-semibold text-lg">Event Statistics</h3>
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-gray-700 rounded p-2">
            <div className="text-gray-400 text-xs">Total Events</div>
            <div className="text-white text-xl font-bold">{eventStats.total}</div>
          </div>
          <div className="bg-blue-700/30 rounded p-2">
            <div className="text-gray-400 text-xs">Passes</div>
            <div className="text-white text-xl font-bold">{eventStats.pass}</div>
          </div>
          <div className="bg-yellow-700/30 rounded p-2">
            <div className="text-gray-400 text-xs">Carries</div>
            <div className="text-white text-xl font-bold">{eventStats.carry}</div>
          </div>
          <div className="bg-red-700/30 rounded p-2">
            <div className="text-gray-400 text-xs">Shots</div>
            <div className="text-white text-xl font-bold">{eventStats.shot}</div>
          </div>
        </div>
      </div>
      
      {/* View Controls */}
      <div className="space-y-2">
        <h3 className="text-white font-semibold text-lg">View Options</h3>
        <div className="space-y-2">
          <label className="flex items-center space-x-2 text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={showBallTrail}
              onChange={(e) => onToggleBallTrail(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">Show Ball Trail</span>
          </label>
          <label className="flex items-center space-x-2 text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => onToggleDebugMode(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm">Debug Mode</span>
          </label>
        </div>
      </div>
      
      {/* Event Filter */}
      <div className="space-y-2">
        <h3 className="text-white font-semibold text-lg">Event Filter</h3>
        <div className="flex flex-wrap gap-2">
          {['all', 'pass', 'carry', 'shot'].map((type) => (
            <button
              key={type}
              onClick={() => setEventFilter(type)}
              className={`px-3 py-1 text-xs rounded capitalize ${
                eventFilter === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              } transition`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>
      
      {/* Players List */}
      <div className="space-y-2">
        <h3 className="text-white font-semibold text-lg">Players</h3>
        
        {/* Team Filter */}
        <div className="flex gap-2 mb-3">
          {['all', 'home', 'away'].map((team) => (
            <button
              key={team}
              onClick={() => setTeamFilter(team)}
              className={`px-3 py-1 text-xs rounded capitalize ${
                teamFilter === team
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              } transition`}
            >
              {team}
            </button>
          ))}
        </div>
        
        {/* Home Team */}
        {(teamFilter === 'all' || teamFilter === 'home') && playersByTeam.home.length > 0 && (
          <div className="space-y-1">
            <div className="text-red-400 text-sm font-medium">Home Team</div>
            {playersByTeam.home.map((player) => (
              <button
                key={player.player_id}
                onClick={() => onPlayerClick(player)}
                className={`w-full text-left px-3 py-2 rounded text-sm ${
                  highlightedPlayerId === player.player_id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                } transition`}
              >
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: player.color }}
                  />
                  <span>
                    Track {player.track_id}
                    {player.shirt_number && ` (#${player.shirt_number})`}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
        
        {/* Away Team */}
        {(teamFilter === 'all' || teamFilter === 'away') && playersByTeam.away.length > 0 && (
          <div className="space-y-1 mt-3">
            <div className="text-blue-400 text-sm font-medium">Away Team</div>
            {playersByTeam.away.map((player) => (
              <button
                key={player.player_id}
                onClick={() => onPlayerClick(player)}
                className={`w-full text-left px-3 py-2 rounded text-sm ${
                  highlightedPlayerId === player.player_id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                } transition`}
              >
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: player.color }}
                  />
                  <span>
                    Track {player.track_id}
                    {player.shirt_number && ` (#${player.shirt_number})`}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* Events List */}
      <div className="space-y-2">
        <h3 className="text-white font-semibold text-lg">
          Events ({filteredEvents.length})
        </h3>
        <div className="space-y-1 max-h-96 overflow-y-auto">
          {filteredEvents.map((event) => {
            const isNearCurrent = Math.abs(event.t - currentTime) < 2;
            
            let bgColor = 'bg-gray-700';
            if (event.type === 'pass') bgColor = 'bg-blue-700/30';
            else if (event.type === 'carry') bgColor = 'bg-yellow-700/30';
            else if (event.type === 'shot') bgColor = 'bg-red-700/30';
            
            return (
              <button
                key={event.id}
                onClick={() => onEventClick(event)}
                className={`w-full text-left px-3 py-2 rounded text-xs ${bgColor} ${
                  isNearCurrent ? 'ring-2 ring-blue-500' : ''
                } hover:opacity-80 transition`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="text-white font-medium capitalize">
                      {event.type}
                    </div>
                    <div className="text-gray-400">
                      Time: {formatTime(event.t)}
                    </div>
                    {event.xt_gain && (
                      <div className="text-gray-400">
                        xT: {event.xt_gain.toFixed(3)}
                      </div>
                    )}
                  </div>
                  {event.distance && (
                    <div className="text-gray-400 text-right">
                      {event.distance.toFixed(1)}m
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ReplaySidebar;
