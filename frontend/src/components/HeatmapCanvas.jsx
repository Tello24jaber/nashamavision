/**
 * HeatmapCanvas Component
 * Renders a player or team heatmap on a pitch visualization
 */
import React, { useRef, useEffect } from 'react';

const HeatmapCanvas = ({ heatmapData, width = 800, height = 520 }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!heatmapData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw pitch outline
    drawPitch(ctx, width, height);

    // Draw heatmap
    drawHeatmap(ctx, heatmapData, width, height);
  }, [heatmapData, width, height]);

  const drawPitch = (ctx, w, h) => {
    const padding = 40;
    const pitchWidth = w - 2 * padding;
    const pitchHeight = h - 2 * padding;

    // Pitch background
    ctx.fillStyle = '#1a8f4a';
    ctx.fillRect(padding, padding, pitchWidth, pitchHeight);

    // White lines
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;

    // Outer boundary
    ctx.strokeRect(padding, padding, pitchWidth, pitchHeight);

    // Center line
    ctx.beginPath();
    ctx.moveTo(padding + pitchWidth / 2, padding);
    ctx.lineTo(padding + pitchWidth / 2, padding + pitchHeight);
    ctx.stroke();

    // Center circle
    ctx.beginPath();
    ctx.arc(padding + pitchWidth / 2, padding + pitchHeight / 2, 60, 0, 2 * Math.PI);
    ctx.stroke();

    // Penalty areas
    const penaltyBoxWidth = pitchWidth * 0.15;
    const penaltyBoxHeight = pitchHeight * 0.6;

    // Left penalty area
    ctx.strokeRect(
      padding,
      padding + (pitchHeight - penaltyBoxHeight) / 2,
      penaltyBoxWidth,
      penaltyBoxHeight
    );

    // Right penalty area
    ctx.strokeRect(
      padding + pitchWidth - penaltyBoxWidth,
      padding + (pitchHeight - penaltyBoxHeight) / 2,
      penaltyBoxWidth,
      penaltyBoxHeight
    );
  };

  const drawHeatmap = (ctx, data, w, h) => {
    const padding = 40;
    const pitchWidth = w - 2 * padding;
    const pitchHeight = h - 2 * padding;

    const gridData = data.heatmap_data || data.data;
    if (!gridData || !Array.isArray(gridData)) return;

    const gridHeight = gridData.length;
    const gridWidth = gridData[0]?.length || 0;

    if (gridHeight === 0 || gridWidth === 0) return;

    const cellWidth = pitchWidth / gridWidth;
    const cellHeight = pitchHeight / gridHeight;

    // Find max value for normalization
    const maxValue = data.max_intensity || 1.0;

    // Draw heatmap cells
    for (let row = 0; row < gridHeight; row++) {
      for (let col = 0; col < gridWidth; col++) {
        const value = gridData[row][col];
        const normalizedValue = value / maxValue;

        // Color gradient from transparent to red
        const alpha = normalizedValue * 0.7;
        ctx.fillStyle = `rgba(255, 0, 0, ${alpha})`;

        const x = padding + col * cellWidth;
        const y = padding + row * cellHeight;

        ctx.fillRect(x, y, cellWidth, cellHeight);
      }
    }
  };

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="border border-gray-300 rounded-lg"
    />
  );
};

export default HeatmapCanvas;
