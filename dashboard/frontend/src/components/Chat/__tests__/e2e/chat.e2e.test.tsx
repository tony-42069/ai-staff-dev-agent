import { test, expect } from '@playwright/test'

test.describe('Chat Component', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to chat page
    await page.goto('/chat')
  })

  test('should show connection status', async ({ page }) => {
    // Initially shows connecting state
    await expect(page.getByPlaceholder('Connecting...')).toBeVisible()

    // After connection, shows ready state
    await expect(page.getByPlaceholder('Type your message or /command...')).toBeVisible()
  })

  test('should send and receive messages', async ({ page }) => {
    // Wait for connection
    await page.waitForSelector('input:not([disabled])')

    // Send a message
    await page.getByPlaceholder('Type your message or /command...').fill('Hello agent')
    await page.getByRole('button', { name: 'Send message' }).click()

    // Check message appears in chat
    await expect(page.getByText('Hello agent')).toBeVisible()

    // Check for agent response
    await expect(page.getByText(/Agent is typing.../)).toBeVisible()
    await expect(page.getByText(/Hello! How can I help/)).toBeVisible()
  })

  test('should handle commands', async ({ page }) => {
    // Wait for connection
    await page.waitForSelector('input:not([disabled])')

    // Send a command
    await page.getByPlaceholder('Type your message or /command...').fill('/help')
    await page.getByRole('button', { name: 'Send message' }).click()

    // Check command appears with correct styling
    await expect(page.getByText('/help')).toBeVisible()
    await expect(page.getByText('Command')).toBeVisible()

    // Check for command response
    await expect(page.getByText(/Available commands/)).toBeVisible()
  })

  test('should handle connection loss', async ({ page }) => {
    // Wait for initial connection
    await page.waitForSelector('input:not([disabled])')

    // Simulate connection loss
    await page.evaluate(() => {
      // Close WebSocket connection
      const ws = (window as any).mockWebSocket
      if (ws) ws.close()
    })

    // Check disconnection message
    await expect(page.getByText('Disconnected')).toBeVisible()
    await expect(page.getByText('Lost connection to chat server')).toBeVisible()

    // Check input is disabled
    await expect(page.getByPlaceholder('Connecting...')).toBeDisabled()
  })

  test('should show message status indicators', async ({ page }) => {
    // Wait for connection
    await page.waitForSelector('input:not([disabled])')

    // Send a message
    await page.getByPlaceholder('Type your message or /command...').fill('Test message')
    await page.getByRole('button', { name: 'Send message' }).click()

    // Check sending indicator
    await expect(page.getByRole('status')).toBeVisible()

    // Check sent status
    await expect(page.getByText('Test message')).toBeVisible()
    await expect(page.getByRole('status')).not.toBeVisible()
  })
}) 