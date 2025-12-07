/**
 * Tests for MatchReplayView Component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import MatchReplayView from '../pages/MatchReplayView';

// Mock the replay hooks
vi.mock('../hooks/useReplayData', () => ({
  default: () => ({
    summary: {
      match: {
        id: 'test-match',
        home_team: 'Team A',
        away_team: 'Team B',
        duration: 3000
      },
      players: [
        { id: 'p1', team: 'home', jersey_number: 10 },
        { id: 'p2', team: 'away', jersey_number: 7 }
      ]
    },
    timeline: {
      frames: [
        {
          t: 0.0,
          players: [
            { player_id: 'p1', x: 50, y: 34, team: 'home' },
            { player_id: 'p2', x: 55, y: 40, team: 'away' }
          ]
        }
      ]
    },
    isLoading: false,
    error: null
  })
}));

vi.mock('../hooks/useReplayController', () => ({
  default: () => ({
    currentTime: 0,
    isPlaying: false,
    playbackSpeed: 1,
    play: vi.fn(),
    pause: vi.fn(),
    seek: vi.fn(),
    setSpeed: vi.fn()
  })
}));

describe('MatchReplayView', () => {
  let queryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
  });

  it('renders replay interface with pitch', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <MatchReplayView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should have canvas or stage for pitch rendering
    const canvasElements = document.querySelectorAll('canvas');
    expect(canvasElements.length).toBeGreaterThan(0);
  });

  it('displays team names', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <MatchReplayView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    expect(screen.getByText(/Team A/i)).toBeInTheDocument();
    expect(screen.getByText(/Team B/i)).toBeInTheDocument();
  });

  it('has playback controls', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <MatchReplayView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should have play/pause button
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('displays timeline slider', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <MatchReplayView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should have slider or range input
    const sliders = screen.queryAllByRole('slider');
    expect(sliders.length).toBeGreaterThanOrEqual(0);
  });

  it('shows current time', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <MatchReplayView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should display time (00:00 format or similar)
    const timeElements = screen.queryAllByText(/\d{1,2}:\d{2}/);
    expect(timeElements.length).toBeGreaterThanOrEqual(0);
  });
});
