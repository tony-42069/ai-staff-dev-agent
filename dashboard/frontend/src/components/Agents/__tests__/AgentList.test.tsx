import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AgentList from '../AgentList';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('AgentList', () => {
  beforeEach(() => {
    queryClient.clear();
  });

  it('renders loading state initially', () => {
    renderWithProviders(<AgentList />);
    expect(screen.getByText('Loading agents...')).toBeInTheDocument();
  });

  it('renders agents after loading', async () => {
    renderWithProviders(<AgentList />);
    
    await waitFor(() => {
      expect(screen.queryByText('Loading agents...')).not.toBeInTheDocument();
    });

    expect(screen.getByText('Test Agent 1')).toBeInTheDocument();
    expect(screen.getByText('A test agent')).toBeInTheDocument();
  });

  it('handles agent deletion', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AgentList />);

    await waitFor(() => {
      expect(screen.queryByText('Loading agents...')).not.toBeInTheDocument();
    });

    const deleteButton = screen.getAllByRole('button', { name: /delete agent/i })[0];
    await user.click(deleteButton);

    await waitFor(() => {
      expect(screen.queryByText('Test Agent 1')).not.toBeInTheDocument();
    });
  });
}); 