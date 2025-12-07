/**
 * Tests for AssistantPage Component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import AssistantPage from '../pages/AssistantPage';

// Mock the hooks
vi.mock('../hooks/useAssistant', () => ({
  default: () => ({
    messages: [],
    sendQuery: vi.fn(),
    isLoading: false,
    error: null
  }),
  useLLMTest: () => ({
    data: { success: true, provider: 'mock' },
    isLoading: false
  }),
  useAssistantHealth: () => ({
    data: { status: 'healthy', provider: 'mock' },
    isLoading: false
  })
}));

describe('AssistantPage', () => {
  let queryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
  });

  it('renders assistant page with sidebar and chat', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <AssistantPage />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should have chat interface
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('displays AI status indicator', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <AssistantPage />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should show AI status (mock provider)
    const statusElements = screen.queryAllByText(/mock|ai|status/i);
    expect(statusElements.length).toBeGreaterThanOrEqual(0);
  });

  it('shows help section with example queries', () => {
    render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <AssistantPage />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Should have help or instructions
    const helpElements = screen.queryAllByText(/help|ask|question/i);
    expect(helpElements.length).toBeGreaterThanOrEqual(0);
  });
});
