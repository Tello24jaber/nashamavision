/**
 * ReplayPitch Component
 * Phase 4: Virtual Match Engine
 * 
 * Renders the virtual pitch with players, ball, and events using Konva
 */
import React, { useEffect, useRef, useMemo } from 'react';
import { Stage, Layer, Rect, Circle, Line, Text, Arrow, Group } from 'react-konva';

const ReplayPitch = ({
  width = 900,
  height = 600,
  players = [],
  ball = null,
  currentTime = 0,
  events = [],
  highlightedPlayerId = null,
  showTrails = false,
  showEventOverlay = true,
  debugMode = false,
  onPlayerClick = null,
}) => {
  const stageRef = useRef(null);
  
  // Pitch dimensions in meters
  const PITCH_LENGTH = 105;
  const PITCH_WIDTH = 68;
  
  // Calculate scaling
  const scale = useMemo(() => {
    const scaleX = width / PITCH_LENGTH;
    const scaleY = height / PITCH_WIDTH;
    return Math.min(scaleX, scaleY) * 0.95; // 95% to leave margin
  }, [width, height]);
  
  // Actual canvas dimensions
  const canvasWidth = PITCH_LENGTH * scale;
  const canvasHeight = PITCH_WIDTH * scale;
  const offsetX = (width - canvasWidth) / 2;
  const offsetY = (height - canvasHeight) / 2;
  
  // Convert meters to canvas pixels
  const toCanvasX = (x) => offsetX + x * scale;
  const toCanvasY = (y) => offsetY + y * scale;
  
  // Get player position at current time
  const getPlayerPosition = (player) => {
    if (!player.positions || player.positions.length === 0) return null;
    
    // Find closest position by time
    let closestPos = player.positions[0];
    let minDiff = Math.abs(player.positions[0].t - currentTime);
    
    for (const pos of player.positions) {
      const diff = Math.abs(pos.t - currentTime);
      if (diff < minDiff) {
        minDiff = diff;
        closestPos = pos;
      }
      if (pos.t > currentTime) break; // Positions are sorted
    }
    
    return closestPos;
  };
  
  // Get ball position at current time
  const getBallPosition = () => {
    if (!ball || ball.length === 0) return null;
    
    let closestPos = ball[0];
    let minDiff = Math.abs(ball[0].t - currentTime);
    
    for (const pos of ball) {
      const diff = Math.abs(pos.t - currentTime);
      if (diff < minDiff) {
        minDiff = diff;
        closestPos = pos;
      }
      if (pos.t > currentTime) break;
    }
    
    return closestPos;
  };
  
  // Get active events near current time
  const getActiveEvents = () => {
    const timeWindow = 2; // Show events within 2 seconds
    return events.filter((event) => {
      return Math.abs(event.t - currentTime) < timeWindow;
    });
  };
  
  // Get player trail (last N seconds)
  const getPlayerTrail = (player, seconds = 2) => {
    if (!showTrails || !player.positions) return [];
    
    const trailStart = currentTime - seconds;
    return player.positions.filter((pos) => pos.t >= trailStart && pos.t <= currentTime);
  };
  
  const activeEvents = useMemo(() => getActiveEvents(), [events, currentTime]);
  
  return (
    <div className="relative" style={{ width, height }}>
      <Stage width={width} height={height} ref={stageRef}>
        {/* Background Layer */}
        <Layer>
          {/* Pitch background */}
          <Rect
            x={offsetX}
            y={offsetY}
            width={canvasWidth}
            height={canvasHeight}
            fill="#1a8b3a"
            stroke="#ffffff"
            strokeWidth={2}
          />
          
          {/* Center line */}
          <Line
            points={[
              toCanvasX(PITCH_LENGTH / 2),
              toCanvasY(0),
              toCanvasX(PITCH_LENGTH / 2),
              toCanvasY(PITCH_WIDTH),
            ]}
            stroke="#ffffff"
            strokeWidth={2}
          />
          
          {/* Center circle */}
          <Circle
            x={toCanvasX(PITCH_LENGTH / 2)}
            y={toCanvasY(PITCH_WIDTH / 2)}
            radius={9.15 * scale}
            stroke="#ffffff"
            strokeWidth={2}
          />
          
          {/* Center spot */}
          <Circle
            x={toCanvasX(PITCH_LENGTH / 2)}
            y={toCanvasY(PITCH_WIDTH / 2)}
            radius={0.3 * scale}
            fill="#ffffff"
          />
          
          {/* Penalty boxes */}
          {/* Left penalty box */}
          <Rect
            x={toCanvasX(0)}
            y={toCanvasY((PITCH_WIDTH - 40.32) / 2)}
            width={16.5 * scale}
            height={40.32 * scale}
            stroke="#ffffff"
            strokeWidth={2}
          />
          
          {/* Right penalty box */}
          <Rect
            x={toCanvasX(PITCH_LENGTH - 16.5)}
            y={toCanvasY((PITCH_WIDTH - 40.32) / 2)}
            width={16.5 * scale}
            height={40.32 * scale}
            stroke="#ffffff"
            strokeWidth={2}
          />
          
          {/* Goal boxes */}
          {/* Left goal box */}
          <Rect
            x={toCanvasX(0)}
            y={toCanvasY((PITCH_WIDTH - 18.32) / 2)}
            width={5.5 * scale}
            height={18.32 * scale}
            stroke="#ffffff"
            strokeWidth={2}
          />
          
          {/* Right goal box */}
          <Rect
            x={toCanvasX(PITCH_LENGTH - 5.5)}
            y={toCanvasY((PITCH_WIDTH - 18.32) / 2)}
            width={5.5 * scale}
            height={18.32 * scale}
            stroke="#ffffff"
            strokeWidth={2}
          />
        </Layer>
        
        {/* Events Layer */}
        {showEventOverlay && (
          <Layer>
            {activeEvents.map((event) => {
              const fromX = toCanvasX(event.from.x);
              const fromY = toCanvasY(event.from.y);
              const toX = toCanvasX(event.to.x);
              const toY = toCanvasY(event.to.y);
              
              let color = '#3B82F6'; // Blue for pass
              if (event.type === 'carry') color = '#F59E0B'; // Yellow
              if (event.type === 'shot') color = '#EF4444'; // Red
              
              const opacity = 1 - Math.abs(event.t - currentTime) / 2;
              
              return (
                <Group key={event.id} opacity={Math.max(0.3, opacity)}>
                  <Arrow
                    points={[fromX, fromY, toX, toY]}
                    stroke={color}
                    fill={color}
                    strokeWidth={3}
                    pointerLength={8}
                    pointerWidth={8}
                  />
                  {event.xt_gain && (
                    <Text
                      x={(fromX + toX) / 2}
                      y={(fromY + toY) / 2 - 15}
                      text={`xT: ${event.xt_gain.toFixed(3)}`}
                      fontSize={12}
                      fill="#ffffff"
                      stroke="#000000"
                      strokeWidth={0.5}
                    />
                  )}
                </Group>
              );
            })}
          </Layer>
        )}
        
        {/* Players Layer */}
        <Layer>
          {players.map((player) => {
            const pos = getPlayerPosition(player);
            if (!pos) return null;
            
            const x = toCanvasX(pos.x);
            const y = toCanvasY(pos.y);
            const isHighlighted = highlightedPlayerId === player.player_id;
            const radius = isHighlighted ? 8 : 6;
            
            // Draw trail if enabled
            const trail = getPlayerTrail(player);
            
            return (
              <Group key={player.player_id}>
                {trail.length > 1 && (
                  <Line
                    points={trail.flatMap((p) => [toCanvasX(p.x), toCanvasY(p.y)])}
                    stroke={player.color}
                    strokeWidth={2}
                    opacity={0.5}
                    lineCap="round"
                    lineJoin="round"
                  />
                )}
                
                <Circle
                  x={x}
                  y={y}
                  radius={radius}
                  fill={player.color}
                  stroke={isHighlighted ? '#ffffff' : '#000000'}
                  strokeWidth={isHighlighted ? 3 : 1}
                  onClick={() => onPlayerClick && onPlayerClick(player)}
                  onTap={() => onPlayerClick && onPlayerClick(player)}
                  style={{ cursor: 'pointer' }}
                />
                
                {player.shirt_number && (
                  <Text
                    x={x}
                    y={y - 4}
                    text={player.shirt_number.toString()}
                    fontSize={10}
                    fill="#ffffff"
                    align="center"
                    verticalAlign="middle"
                  />
                )}
                
                {debugMode && (
                  <Text
                    x={x + 10}
                    y={y - 10}
                    text={`T${player.track_id}`}
                    fontSize={8}
                    fill="#ffffff"
                    stroke="#000000"
                    strokeWidth={0.5}
                  />
                )}
              </Group>
            );
          })}
        </Layer>
        
        {/* Ball Layer */}
        <Layer>
          {(() => {
            const ballPos = getBallPosition();
            if (!ballPos) return null;
            
            const x = toCanvasX(ballPos.x);
            const y = toCanvasY(ballPos.y);
            
            return (
              <Circle
                x={x}
                y={y}
                radius={4}
                fill="#ffffff"
                stroke="#000000"
                strokeWidth={1}
              />
            );
          })()}
        </Layer>
        
        {/* Debug Overlay */}
        {debugMode && (
          <Layer>
            <Text
              x={10}
              y={10}
              text={`Time: ${currentTime.toFixed(2)}s\nPlayers: ${players.length}\nFPS: ${(1000 / 16).toFixed(1)}`}
              fontSize={12}
              fill="#ffffff"
              stroke="#000000"
              strokeWidth={0.5}
            />
          </Layer>
        )}
      </Stage>
    </div>
  );
};

export default ReplayPitch;
