/**
 * useReplayController Hook
 * Phase 4: Virtual Match Engine
 * 
 * Manages replay playback state, timing, and controls
 */
import { useState, useEffect, useRef, useCallback } from 'react';

export const useReplayController = (duration = 0) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  
  const animationFrameRef = useRef(null);
  const lastTimestampRef = useRef(null);
  
  // Animation loop
  useEffect(() => {
    if (!isPlaying) {
      lastTimestampRef.current = null;
      return;
    }
    
    const animate = (timestamp) => {
      if (lastTimestampRef.current === null) {
        lastTimestampRef.current = timestamp;
      }
      
      const deltaTime = (timestamp - lastTimestampRef.current) / 1000; // Convert to seconds
      lastTimestampRef.current = timestamp;
      
      setCurrentTime((prevTime) => {
        const newTime = prevTime + deltaTime * playbackSpeed;
        
        // Stop at end
        if (newTime >= duration) {
          setIsPlaying(false);
          return duration;
        }
        
        return newTime;
      });
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    
    animationFrameRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying, playbackSpeed, duration]);
  
  // Controls
  const play = useCallback(() => {
    if (currentTime >= duration) {
      setCurrentTime(0);
    }
    setIsPlaying(true);
  }, [currentTime, duration]);
  
  const pause = useCallback(() => {
    setIsPlaying(false);
  }, []);
  
  const togglePlay = useCallback(() => {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }, [isPlaying, play, pause]);
  
  const stop = useCallback(() => {
    setIsPlaying(false);
    setCurrentTime(0);
  }, []);
  
  const seek = useCallback((time) => {
    const clampedTime = Math.max(0, Math.min(time, duration));
    setCurrentTime(clampedTime);
  }, [duration]);
  
  const jumpToEvent = useCallback((eventTime) => {
    seek(eventTime);
    setIsPlaying(true);
  }, [seek]);
  
  const skipForward = useCallback((seconds = 10) => {
    seek(currentTime + seconds);
  }, [currentTime, seek]);
  
  const skipBackward = useCallback((seconds = 10) => {
    seek(currentTime - seconds);
  }, [currentTime, seek]);
  
  const changeSpeed = useCallback((speed) => {
    setPlaybackSpeed(Math.max(0.25, Math.min(4, speed)));
  }, []);
  
  return {
    // State
    isPlaying,
    currentTime,
    playbackSpeed,
    duration,
    progress: duration > 0 ? (currentTime / duration) * 100 : 0,
    
    // Controls
    play,
    pause,
    togglePlay,
    stop,
    seek,
    jumpToEvent,
    skipForward,
    skipBackward,
    changeSpeed,
  };
};
