import React from 'react';
import { vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Projects } from '../Projects';
import { projectApi } from '../../../services/api';

// Create a new QueryClient for each test
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// Wrapper component with providers
const renderWithProviders = (ui: React.ReactElement) => {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>
      {ui}
    </QueryClientProvider>
  );
};

describe('Projects Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    renderWithProviders(<Projects />);
    expect(screen.getByText('Loading projects...')).toBeInTheDocument();
  });

  it('displays projects after loading', async () => {
    renderWithProviders(<Projects />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });
    
    expect(screen.getByText('A test project')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
  });

  it('opens create project dialog when clicking create button', async () => {
    renderWithProviders(<Projects />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
    });

    // Click create button
    fireEvent.click(screen.getByText('Create Project'));
    
    // Check if dialog is open
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Create Project')).toBeInTheDocument();
  });

  it('creates a new project successfully', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Projects />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
    });

    // Open create dialog
    fireEvent.click(screen.getByText('Create Project'));

    // Fill form
    await user.type(screen.getByLabelText('Name *'), 'New Test Project');
    await user.type(screen.getByLabelText('Description'), 'A new test project');

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: 'Create' }));

    // Wait for success and dialog close
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('edits a project successfully', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Projects />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
    });

    // Click edit button
    const editButtons = screen.getAllByTestId('EditIcon');
    fireEvent.click(editButtons[0]);

    // Check if edit dialog is open
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Edit Project')).toBeInTheDocument();

    // Edit name
    const nameInput = screen.getByLabelText('Name *');
    await user.clear(nameInput);
    await user.type(nameInput, 'Updated Project Name');

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));

    // Wait for success and dialog close
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('deletes a project after confirmation', async () => {
    // Mock window.confirm
    const confirmSpy = vi.spyOn(window, 'confirm');
    confirmSpy.mockImplementation(() => true);

    renderWithProviders(<Projects />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
    });

    // Click delete button
    const deleteButtons = screen.getAllByTestId('DeleteIcon');
    fireEvent.click(deleteButtons[0]);

    // Verify confirm was called
    expect(confirmSpy).toHaveBeenCalled();

    // Wait for success
    await waitFor(() => {
      expect(screen.queryByText('Test Project')).not.toBeInTheDocument();
    });

    confirmSpy.mockRestore();
  });

  it('handles project status changes', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Projects />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
    });

    // Open create dialog
    fireEvent.click(screen.getByText('Create Project'));

    // Change status
    fireEvent.mouseDown(screen.getByLabelText('Status'));
    const completedOption = screen.getByRole('option', { name: 'Completed' });
    fireEvent.click(completedOption);

    // Fill required name
    await user.type(screen.getByLabelText('Name *'), 'Status Test Project');

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: 'Create' }));

    // Wait for success and dialog close
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('validates required fields', async () => {
    renderWithProviders(<Projects />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument();
    });

    // Open create dialog
    fireEvent.click(screen.getByText('Create Project'));

    // Try to submit without required fields
    fireEvent.click(screen.getByRole('button', { name: 'Create' }));

    // Check for HTML5 validation message
    const nameInput = screen.getByLabelText('Name *');
    expect(nameInput).toBeInvalid();
  });
});
