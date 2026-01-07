# Playwright MCP Server

**Purpose**: Comprehensive E2E testing, visual validation, and accessibility auditing

## Triggers
- End-to-end test suite development
- Visual regression testing needs
- Accessibility compliance auditing
- Cross-browser testing requirements
- Complex user journey validation
- Performance testing and monitoring

## Choose When
- **Over BrowserTools**: When you need structured test suites, not quick automation
- **Over manual testing**: For repeatable, automated test scenarios
- **For E2E**: Complete user journey validation
- **For regression**: Prevent bugs from reappearing
- **For accessibility**: WCAG compliance verification
- **For visual testing**: Detect UI regressions automatically

## Works Best With
- **Sequential**: Sequential designs test strategy → Playwright implements tests
- **Magic**: Magic generates UI → Playwright validates components
- **Code Review**: Playwright tests → Review validates coverage

## Core Capabilities
- **Multi-browser testing**: Chromium, Firefox, WebKit (Safari)
- **Test generation**: Record user actions, generate test code
- **Visual regression**: Screenshot comparison, pixel-perfect diffs
- **Accessibility auditing**: Automated WCAG 2.1 checks
- **Network mocking**: Intercept and mock API calls
- **Parallel execution**: Run tests concurrently
- **Test reporting**: HTML reports, traces, videos

## Test Types

### Functional Tests
- User authentication flows
- Form submissions and validation
- Navigation and routing
- Data CRUD operations
- Search and filtering
- Error handling scenarios

### Visual Tests
- Screenshot comparison
- Layout regression detection
- Responsive design validation
- Theme consistency checks
- Cross-browser rendering

### Accessibility Tests
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader compatibility
- Color contrast ratios
- Focus management
- ARIA attribute validation

### Performance Tests
- Page load times
- Time to interactive
- Lighthouse score validation
- Core Web Vitals monitoring
- API response times

## Examples
```
"write E2E test for login flow" → Playwright (structured test suite)
"validate checkout process" → Playwright (multi-step user journey)
"check accessibility compliance" → Playwright (automated WCAG audit)
"detect visual regressions" → Playwright (screenshot comparison)
"test across browsers" → Playwright (cross-browser suite)
"just check if page loads" → BrowserTools (quick validation)
```

## Test Structure

### Basic Test
```typescript
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  // Navigate
  await page.goto('https://app.example.com/login')

  // Interact
  await page.fill('#email', 'user@example.com')
  await page.fill('#password', 'secure-password')
  await page.click('button[type="submit"]')

  // Assert
  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('.welcome-message')).toBeVisible()
})
```

### Visual Regression Test
```typescript
test('homepage layout unchanged', async ({ page }) => {
  await page.goto('https://example.com')

  // Take screenshot and compare
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100 // Allow minor differences
  })
})
```

### Accessibility Test
```typescript
import { injectAxe, checkA11y } from 'axe-playwright'

test('page is accessible', async ({ page }) => {
  await page.goto('https://example.com')
  await injectAxe(page)

  // Check WCAG 2.1 AA compliance
  await checkA11y(page, null, {
    detailedReport: true,
    detailedReportOptions: { html: true }
  })
})
```

### API Mocking Test
```typescript
test('handles API errors gracefully', async ({ page }) => {
  // Mock API to return error
  await page.route('**/api/users', route => {
    route.fulfill({
      status: 500,
      body: 'Internal Server Error'
    })
  })

  await page.goto('https://app.example.com/users')

  // Verify error handling
  await expect(page.locator('.error-message')).toBeVisible()
  await expect(page.locator('.error-message')).toContainText(
    'Failed to load users'
  )
})
```

## Advanced Features

### Test Generation (Codegen)
```bash
# Record user actions, generate test code
npx playwright codegen https://example.com
```

### Trace Viewer (Debug Tests)
```typescript
test('complex flow', async ({ page }) => {
  // Trace will be saved on failure
  await page.goto('...')
  // ... test steps
})
// View trace: npx playwright show-trace trace.zip
```

### Parallel Execution
```typescript
// playwright.config.ts
export default {
  workers: 4, // Run 4 tests in parallel
  fullyParallel: true
}
```

### Cross-Browser Testing
```typescript
// playwright.config.ts
export default {
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } }
  ]
}
```

## Performance Considerations
- **Parallel execution**: Utilize all CPU cores
- **Headless mode**: 30% faster than headed mode
- **Reuse contexts**: Share browser context between tests
- **Selective testing**: Run only affected tests
- **Sharding**: Distribute tests across machines

## Integration Patterns

### With Magic (Component Testing):
```
1. Magic: Generate new UI component
2. Playwright: Create test suite for component
3. Magic: Adjust component based on test findings
```

### With Sequential (Test Strategy):
```
1. Sequential: Analyze app flows
2. Sequential: Design test coverage strategy
3. Playwright: Implement test suite
4. Sequential: Validate coverage completeness
```

### With Code Review (Quality Assurance):
```
1. Playwright: Run full test suite
2. Code Review: Analyze test coverage
3. Playwright: Add missing test cases
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Playwright tests
  run: npx playwright test

- name: Upload test results
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: playwright-report
    path: playwright-report/
```

### Test Reporting
- HTML reports with screenshots
- Video recordings of failures
- Trace files for debugging
- JUnit XML for CI integration

## Quality Gates
When using Playwright, ensure:
- [ ] Tests cover critical user journeys
- [ ] Accessibility tests pass (WCAG 2.1 AA)
- [ ] Visual regression tests have baselines
- [ ] Tests run in CI/CD pipeline
- [ ] Flaky tests identified and fixed
- [ ] Test execution time acceptable (<10 min)
- [ ] Cross-browser coverage adequate
- [ ] Test reports reviewed regularly
