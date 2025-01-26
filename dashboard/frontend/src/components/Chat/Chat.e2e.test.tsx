import { test, expect } from '@playwright/test';

test.describe('Chat Component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('shows connection status', async ({ page }) => {
    const statusIndicator = page.locator('[data-testid="connection-status"]');
    await expect(statusIndicator).toBeVisible();
    await expect(statusIndicator).toHaveText(/Connected|Connecting|Disconnected/);
  });

  test('sends and receives messages', async ({ page }) => {
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    const testMessage = 'Hello, agent!';

    await messageInput.fill(testMessage);
    await sendButton.click();

    const sentMessage = page.locator(`[data-testid="message"]:has-text("${testMessage}")`);
    await expect(sentMessage).toBeVisible();
    await expect(sentMessage).toHaveAttribute('data-sender', 'user');
  });

  test('handles command messages', async ({ page }) => {
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    const testCommand = '/help';

    await messageInput.fill(testCommand);
    await sendButton.click();

    const commandMessage = page.locator(`[data-testid="message"]:has-text("${testCommand}")`);
    await expect(commandMessage).toBeVisible();
    await expect(commandMessage).toHaveAttribute('data-type', 'command');
  });

  test('shows message status indicators', async ({ page }) => {
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    const testMessage = 'Test status message';

    await messageInput.fill(testMessage);
    await sendButton.click();

    const messageStatus = page.locator('[data-testid="message-status"]').last();
    await expect(messageStatus).toBeVisible();
    await expect(messageStatus).toHaveText(/sent|delivered|error/);
  });

  test('shows typing indicator when agent is typing', async ({ page }) => {
    // Simulate agent typing event through WebSocket
    await page.evaluate(() => {
      const wsEvent = new MessageEvent('message', {
        data: JSON.stringify({ type: 'status', content: 'typing', sender: 'agent' })
      });
      window.dispatchEvent(wsEvent);
    });

    const typingIndicator = page.locator('[data-testid="typing-indicator"]');
    await expect(typingIndicator).toBeVisible();
  });
}); 