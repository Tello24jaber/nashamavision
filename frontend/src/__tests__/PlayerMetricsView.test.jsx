/**
 * Tests for PlayerMetricsView Component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import PlayerMetricsView from '../pages/PlayerMetricsView';

// Mock the analytics hook
vi.mock('../hooks/useAnalytics', () => ({
  default: () => ({
    metrics: {
      players: [
        {
          player_id: 'p1',
          jersey_number: 10,
          team: 'home',
          total_distance: 12500,
          avg_speed: 6.5,
          max_speed: 28.5,
          sprints_count: 15
        },
        {
          player_id: 'p2',
          jersey_number: 7,
          team: 'away',
          total_distance: 11800,
          avg_speed: 6.2,
          max_speed: 27.0,
          sprints_count: 12
        }
      ]
    },
    isLoading: false,
    error: null
  })
}));

describe('PlayerMetricsView', () => {
  let queryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
  });

  it('renders metrics page with player data', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <PlayerMetricsView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should display player data
    expect(screen.getByText(/12500|12.5|distance/i)).toBeInTheDocument();
  });

  it('displays player jersey numbers', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <PlayerMetricsView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    expect(screen.getByText(/10/)).toBeInTheDocument();
    expect(screen.getByText(/7/)).toBeInTheDocument();
  });

  it('shows key metrics (distance, speed, sprints)', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <PlayerMetricsView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should show distance values
    const distanceElements = screen.queryAllByText(/12500|11800|12.5|11.8/);
    expect(distanceElements.length).toBeGreaterThan(0);

    // Should show speed values
    const speedElements = screen.queryAllByText(/6\.\d|28\.\d|27\.\d/);
    expect(speedElements.length).toBeGreaterThan(0);
  });

  it('displays sprint counts', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <PlayerMetricsView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    expect(screen.getByText(/15/)).toBeInTheDocument();
    expect(screen.getByText(/12/)).toBeInTheDocument();
  });

  it('shows team affiliation', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <PlayerMetricsView />
        </QueryClientProvider>
      </BrowserRouter>
    );

    const teamElements = screen.queryAllByText(/home|away/i);
    expect(teamElements.length).toBeGreaterThan(0);
  });
});
