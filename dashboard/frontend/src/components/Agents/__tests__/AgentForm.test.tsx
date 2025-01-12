import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AgentForm from '../AgentForm';

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

describe('AgentForm', () => {
  beforeEach(() => {
    queryClient.clear();
  });

  it('renders form fields', () => {
    renderWithProviders(<AgentForm />);
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/capabilities/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create agent/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty required fields', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AgentForm />);
    
    const submitButton = screen.getByRole('button', { name: /create agent/i });
    await user.click(submitButton);

    expect(await screen.findByText('Name is required')).toBeInTheDocument();
    expect(await screen.findByText('Capabilities are required')).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    renderWithProviders(<AgentForm />);
    
    await user.type(screen.getByLabelText(/name/i), 'Test Agent');
    await user.type(screen.getByLabelText(/description/i), 'A test agent description');
    await user.type(screen.getByLabelText(/capabilities/i), 'test,debug');
    
    const submitButton = screen.getByRole('button', { name: /create agent/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Agent created')).toBeInTheDocument();
    });

    // Form should be reset after successful submission
    expect(screen.getByLabelText(/name/i)).toHaveValue('');
    expect(screen.getByLabelText(/description/i)).toHaveValue('');
    expect(screen.getByLabelText(/capabilities/i)).toHaveValue('');
  });
}); 