/**
 * ReplayControls Component
 * Phase 4: Virtual Match Engine
 * 
 * Playback controls for the replay engine
 */
import React from 'react';

const ReplayControls = ({
  isPlaying,
  currentTime,
  duration,
  playbackSpeed,
  onPlay,
  onPause,
  onStop,
  onSeek,
  onSpeedChange,
  onSkipForward,
  onSkipBackward,
}) => {
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  const handleSliderChange = (e) => {
    const value = parseFloat(e.target.value);
    onSeek(value);
  };
  
  const speedOptions = [0.25, 0.5, 1, 1.5, 2, 4];
  
  return (
    <div className="bg-gray-800 rounded-lg p-4 space-y-4">
      {/* Timeline Slider */}
      <div className="space-y-2">
        <input
          type="range"
          min={0}
          max={duration}
          step={0.1}
          value={currentTime}
          onChange={handleSliderChange}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
        <div className="flex justify-between text-sm text-gray-400">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>
      
      {/* Control Buttons */}
      <div className="flex items-center justify-center space-x-4">
        {/* Skip Backward */}
        <button
          onClick={() => onSkipBackward(10)}
          className="p-2 text-white hover:bg-gray-700 rounded-lg transition"
          title="Skip Backward 10s"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z"
            />
          </svg>
        </button>
        
        {/* Play/Pause */}
        <button
          onClick={isPlaying ? onPause : onPlay}
          className="p-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition"
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          ) : (
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </button>
        
        {/* Stop */}
        <button
          onClick={onStop}
          className="p-2 text-white hover:bg-gray-700 rounded-lg transition"
          title="Stop"
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 6h12v12H6z" />
          </svg>
        </button>
        
        {/* Skip Forward */}
        <button
          onClick={() => onSkipForward(10)}
          className="p-2 text-white hover:bg-gray-700 rounded-lg transition"
          title="Skip Forward 10s"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z"
            />
          </svg>
        </button>
      </div>
      
      {/* Playback Speed */}
      <div className="flex items-center justify-center space-x-2">
        <span className="text-sm text-gray-400">Speed:</span>
        <div className="flex space-x-1">
          {speedOptions.map((speed) => (
            <button
              key={speed}
              onClick={() => onSpeedChange(speed)}
              className={`px-3 py-1 text-xs rounded ${
                playbackSpeed === speed
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              } transition`}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReplayControls;
