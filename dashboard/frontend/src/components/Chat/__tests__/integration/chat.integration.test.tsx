import { test, expect } from '@playwright/test'
import type { Page } from '@playwright/test'

test.describe('Chat Integration', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    // Start both frontend and backend
    page = await browser.newPage()
    await page.goto('/chat')
  })

  test('establishes WebSocket connection', async () => {
    // Wait for WebSocket connection
    await page.waitForSelector('[data-testid="connection-status"]')
    const status = await page.locator('[data-testid="connection-status"]')
    await expect(status).toHaveText('Connected')
  })

  test('sends message and receives response', async () => {
    // Wait for connection
    await page.waitForSelector('[data-testid="message-input"]')

    // Send a help message
    await page.locator('[data-testid="message-input"]').fill('help')
    await page.locator('[data-testid="send-button"]').click()

    // Check message appears and response is received
    await expect(page.locator('[data-testid="message"]:has-text("help")')).toBeVisible()
    await expect(page.locator('[data-testid="message"]')).toContainText('I can help you with')
  })

  test('executes commands and receives responses', async () => {
    // Wait for connection
    await page.waitForSelector('[data-testid="message-input"]')

    // Send help command
    await page.locator('[data-testid="message-input"]').fill('/help')
    await page.locator('[data-testid="send-button"]').click()

    // Check command appears and response is received
    await expect(page.locator('[data-testid="message"]:has-text("/help")')).toBeVisible()
    await expect(page.locator('[data-testid="message"]')).toContainText('Available commands')
  })

  test('handles agent capabilities', async () => {
    // Wait for connection
    await page.waitForSelector('[data-testid="message-input"]')

    // Request code review
    await page.locator('[data-testid="message-input"]').fill('Can you review my code?')
    await page.locator('[data-testid="send-button"]').click()

    // Check response includes capability information
    await expect(page.locator('[data-testid="message"]')).toContainText('code review')
  })

  test('maintains message history', async () => {
    // Wait for connection
    await page.waitForSelector('[data-testid="message-input"]')

    // Send multiple messages
    const messages = ['Hello', 'How are you?', '/status']
    for (const msg of messages) {
      await page.locator('[data-testid="message-input"]').fill(msg)
      await page.locator('[data-testid="send-button"]').click()
      await page.waitForSelector(`[data-testid="message"]:has-text("${msg}")`)
    }

    // Verify all messages are visible
    for (const msg of messages) {
      await expect(page.locator(`[data-testid="message"]:has-text("${msg}")`)).toBeVisible()
    }
  })

  test('handles connection interruptions', async () => {
    // Wait for initial connection
    await page.waitForSelector('[data-testid="connection-status"]')

    // Simulate network interruption
    await page.route('**/*', route => route.abort())
    await page.waitForSelector('[data-testid="connection-status"]:has-text("Disconnected")')

    // Restore connection
    await page.unroute('**/*')
    await page.waitForSelector('[data-testid="connection-status"]:has-text("Connected")')
  })

  test('processes complex interactions', async () => {
    // Wait for connection
    await page.waitForSelector('[data-testid="message-input"]')

    // Create a project
    await page.locator('[data-testid="message-input"]').fill('create a new project')
    await page.locator('[data-testid="send-button"]').click()

    // Check project creation response
    await expect(page.locator('[data-testid="message"]')).toContainText('create a new project')
    await expect(page.locator('[data-testid="message"]')).toContainText('Would you like to')

    // Provide project details
    await page.locator('[data-testid="message-input"]').fill('Test Project with TypeScript')
    await page.locator('[data-testid="send-button"]').click()

    // Verify project creation flow
    await expect(page.locator('[data-testid="message"]')).toContainText('project')
  })
}) 