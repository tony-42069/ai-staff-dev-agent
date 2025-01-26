import { test, expect } from '@playwright/test'
import type { Page } from '@playwright/test'

test.describe('MonitoringDashboard Integration', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage()
    await page.goto('/monitoring')
  })

  test('loads initial metrics data', async () => {
    // Wait for metrics to load
    await page.waitForSelector('[data-testid="metric-card"]')
    const cards = await page.locator('[data-testid="metric-card"]').count()
    expect(cards).toBeGreaterThan(0)
  })

  test('receives real-time metric updates', async () => {
    // Wait for initial load
    await page.waitForSelector('[data-testid="metric-value"]')
    const initialValue = await page.locator('[data-testid="metric-value"]').first().textContent()

    // Wait for WebSocket update
    await page.waitForFunction((oldValue) => {
      const newValue = document.querySelector('[data-testid="metric-value"]')?.textContent
      return newValue !== oldValue
    }, initialValue)

    const updatedValue = await page.locator('[data-testid="metric-value"]').first().textContent()
    expect(updatedValue).not.toBe(initialValue)
  })

  test('displays historical data charts', async () => {
    // Wait for charts to load
    await page.waitForSelector('[data-testid="historical-chart"]')
    
    // Check chart elements
    await expect(page.locator('[data-testid="historical-chart"]')).toBeVisible()
    await expect(page.locator('text="Historical Trends"')).toBeVisible()
  })

  test('updates queue status in real-time', async () => {
    // Wait for queue status section
    await page.waitForSelector('[data-testid="queue-status"]')
    
    // Get initial queue sizes
    const initialSizes = await page.evaluate(() => {
      const elements = document.querySelectorAll('[data-testid="queue-size"]')
      return Array.from(elements).map(el => el.textContent)
    })

    // Wait for update
    await page.waitForTimeout(5000) // Wait for potential updates

    // Get updated sizes
    const updatedSizes = await page.evaluate(() => {
      const elements = document.querySelectorAll('[data-testid="queue-size"]')
      return Array.from(elements).map(el => el.textContent)
    })

    // Compare sizes
    expect(updatedSizes).not.toEqual(initialSizes)
  })

  test('handles system alerts', async () => {
    // Wait for initial load
    await page.waitForSelector('[data-testid="system-status"]')

    // Simulate system alert via WebSocket
    await page.evaluate(() => {
      const wsEvent = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'alert',
          content: {
            level: 'warning',
            message: 'High CPU usage detected'
          }
        })
      })
      window.dispatchEvent(wsEvent)
    })

    // Check alert appears
    await expect(page.locator('[data-testid="alert-message"]')).toContainText('High CPU usage')
  })

  test('maintains connection status', async () => {
    // Check initial connection
    await page.waitForSelector('[data-testid="connection-status"]')
    await expect(page.locator('[data-testid="connection-status"]')).toHaveText('Connected')

    // Simulate connection loss
    await page.evaluate(() => {
      window.dispatchEvent(new Event('offline'))
    })
    await expect(page.locator('[data-testid="connection-status"]')).toHaveText('Disconnected')

    // Restore connection
    await page.evaluate(() => {
      window.dispatchEvent(new Event('online'))
    })
    await expect(page.locator('[data-testid="connection-status"]')).toHaveText('Connected')
  })

  test('handles error states gracefully', async () => {
    // Wait for initial load
    await page.waitForSelector('[data-testid="system-status"]')

    // Simulate error response
    await page.route('**/api/v1/metrics/current', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })

    // Trigger refresh
    await page.reload()

    // Check error state
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Error loading metrics')
  })

  test('updates performance metrics periodically', async () => {
    // Wait for initial metrics
    await page.waitForSelector('[data-testid="performance-metrics"]')
    
    const initialMetrics = await page.evaluate(() => {
      const elements = document.querySelectorAll('[data-testid="performance-value"]')
      return Array.from(elements).map(el => el.textContent)
    })

    // Wait for automatic update
    await page.waitForTimeout(5000)

    const updatedMetrics = await page.evaluate(() => {
      const elements = document.querySelectorAll('[data-testid="performance-value"]')
      return Array.from(elements).map(el => el.textContent)
    })

    expect(updatedMetrics).not.toEqual(initialMetrics)
  })
}) 