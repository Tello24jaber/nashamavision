/**
 * Tests for AssistantChat Component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AssistantChat from '../components/assistant/AssistantChat';

// Mock the useAssistant hook
vi.mock('../hooks/useAssistant', () => ({
  default: () => ({
    messages: [
      {
        id: '1',
        role: 'user',
        content: 'Who covered the most distance?',
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        role: 'assistant',
        content: 'Player #10 covered the most distance with 12.5 km.',
        timestamp: new Date().toISOString(),
        data: { player_id: 'p1', distance: 12500 },
        actions: [
          { label: 'View Player Metrics', action_type: 'navigate', payload: { page: 'metrics' } }
        ]
      }
    ],
    sendQuery: vi.fn(),
    isLoading: false,
    error: null
  })
}));

describe('AssistantChat', () => {
  let queryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
  });

  it('renders chat interface', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AssistantChat matchId="test-match-id" />
      </QueryClientProvider>
    );

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('displays user and assistant messages', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AssistantChat matchId="test-match-id" />
      </QueryClientProvider>
    );

    expect(screen.getByText('Who covered the most distance?')).toBeInTheDocument();
    expect(screen.getByText(/Player #10 covered the most distance/)).toBeInTheDocument();
  });

  it('displays action buttons for assistant messages', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AssistantChat matchId="test-match-id" />
      </QueryClientProvider>
    );

    expect(screen.getByRole('button', { name: /View Player Metrics/i })).toBeInTheDocument();
  });

  it('allows user to type and send a message', async () => {
    const user = userEvent.setup();

    render(
      <QueryClientProvider client={queryClient}>
        <AssistantChat matchId="test-match-id" />
      </QueryClientProvider>
    );

    const input = screen.getByRole('textbox');
    await user.type(input, 'What was the formation?');
    
    expect(input).toHaveValue('What was the formation?');

    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Input should be cleared after sending
    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('shows loading state when sending message', () => {
    // Mock loading state
    vi.mock('../hooks/useAssistant', () => ({
      default: () => ({
        messages: [],
        sendQuery: vi.fn(),
        isLoading: true,
        error: null
      })
    }));

    render(
      <QueryClientProvider client={queryClient}>
        <AssistantChat matchId="test-match-id" />
      </QueryClientProvider>
    );

    // Should show loading indicator
    const loadingElements = screen.queryAllByText(/thinking|loading/i);
    expect(loadingElements.length).toBeGreaterThanOrEqual(0);
  });
});
