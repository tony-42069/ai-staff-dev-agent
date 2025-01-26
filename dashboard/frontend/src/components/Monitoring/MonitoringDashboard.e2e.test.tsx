import { test, expect } from '@playwright/test';

test.describe('MonitoringDashboard Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/monitoring');
  });

  test('displays metrics cards', async ({ page }) => {
    const metricsCards = page.locator('[data-testid="metric-card"]');
    await expect(metricsCards).toHaveCount(4); // Assuming we have 4 main metrics
  });

  test('shows real-time updates', async ({ page }) => {
    const initialValue = await page.locator('[data-testid="metric-value"]').first().textContent();
    
    // Simulate WebSocket metric update
    await page.evaluate(() => {
      const wsEvent = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'metrics',
          content: {
            activeAgents: 5,
            completedTasks: 100,
            averageResponseTime: '2.5s',
            successRate: '95%'
          }
        })
      });
      window.dispatchEvent(wsEvent);
    });

    // Wait for value to update
    await expect(page.locator('[data-testid="metric-value"]').first()).not.toHaveText(initialValue || '');
  });

  test('shows connection status indicator', async ({ page }) => {
    const statusIndicator = page.locator('[data-testid="connection-status"]');
    await expect(statusIndicator).toBeVisible();
    await expect(statusIndicator).toHaveText(/Connected|Connecting|Disconnected/);
  });

  test('displays loading state', async ({ page }) => {
    // Simulate loading state
    await page.evaluate(() => {
      window.localStorage.setItem('isLoading', 'true');
      window.dispatchEvent(new Event('storage'));
    });

    const loadingIndicator = page.locator('[data-testid="loading-indicator"]');
    await expect(loadingIndicator).toBeVisible();
  });

  test('shows error state on connection failure', async ({ page }) => {
    // Simulate WebSocket error
    await page.evaluate(() => {
      const wsEvent = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'error',
          content: 'Connection failed'
        })
      });
      window.dispatchEvent(wsEvent);
    });

    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('Connection failed');
  });
}); 