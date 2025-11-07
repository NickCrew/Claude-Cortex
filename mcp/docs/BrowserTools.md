# BrowserTools MCP Server

**Purpose**: Browser automation, web scraping, and real-time web interaction

## Triggers
- Web scraping and data extraction needs
- Dynamic web content interaction
- Form filling and submission automation
- Screenshot and PDF generation
- Real-time web monitoring
- Content verification on live sites

## Choose When
- **Over WebSearch**: When you need to interact with pages, not just search
- **Over static analysis**: For dynamic JavaScript-rendered content
- **For automation**: Repetitive browser tasks
- **For testing**: Quick validation of live sites
- **For data extraction**: Scraping structured data from websites
- **For monitoring**: Checking site availability and content

## Works Best With
- **Playwright**: BrowserTools for quick tasks → Playwright for comprehensive testing
- **Sequential**: BrowserTools gathers data → Sequential analyzes findings
- **Quality Gates**: BrowserTools validates deployment → Reports to quality workstream

## Core Capabilities
- **Page navigation**: Visit URLs, follow links, handle redirects
- **Element interaction**: Click, type, select, scroll
- **Data extraction**: Scrape text, attributes, structured data
- **Screenshots**: Capture full page or specific elements
- **PDF generation**: Convert pages to PDF documents
- **Form automation**: Fill and submit forms programmatically
- **Wait strategies**: Wait for elements, network idle, custom conditions

## Examples
```
"scrape product prices from this site" → BrowserTools (data extraction)
"check if homepage loads correctly" → BrowserTools (quick validation)
"fill out this contact form" → BrowserTools (form automation)
"take a screenshot of the dashboard" → BrowserTools (visual capture)
"monitor this page for changes" → BrowserTools (content monitoring)
"run E2E test suite" → Playwright (comprehensive testing, not BrowserTools)
```

## Common Operations

### Navigation
```python
# Visit page
browser.navigate('https://example.com')

# Wait for element
browser.wait_for_selector('#main-content')

# Click link
browser.click('a[href="/products"]')
```

### Data Extraction
```python
# Extract text
title = browser.get_text('h1.product-title')

# Extract attributes
price = browser.get_attribute('.price', 'data-price')

# Extract structured data
products = browser.query_all('.product-card')
```

### Screenshots
```python
# Full page screenshot
browser.screenshot('full-page.png')

# Element screenshot
browser.screenshot('hero.png', selector='.hero-section')

# PDF generation
browser.pdf('page.pdf')
```

### Form Automation
```python
# Fill form
browser.type('#email', 'user@example.com')
browser.type('#password', 'secure-password')
browser.click('button[type="submit"]')

# Select dropdown
browser.select('#country', 'United States')

# Check checkbox
browser.check('#terms-agreement')
```

## Wait Strategies

### Element Waiting
```python
# Wait for element to appear
browser.wait_for_selector('.dynamic-content')

# Wait for element to be visible
browser.wait_for_visible('.modal')

# Wait for network idle
browser.wait_for_network_idle()
```

### Custom Conditions
```python
# Wait for specific condition
browser.wait_for_function('document.readyState === "complete"')

# Timeout control
browser.wait_for_selector('.loading', timeout=5000)
```

## Performance Considerations
- **Headless mode**: Faster execution without GUI
- **Resource limits**: Control memory and CPU usage
- **Timeouts**: Set appropriate wait times
- **Cleanup**: Close browser instances properly
- **Caching**: Reuse browser sessions when possible

## Integration Patterns

### With Sequential (Data Analysis):
```
1. BrowserTools: Scrape competitor pricing
2. Sequential: Analyze pricing patterns
3. BrowserTools: Verify analysis on live sites
```

### With Playwright (Quick Check → Full Test):
```
1. BrowserTools: Quick validation of fix
2. If issues: Playwright for comprehensive testing
3. Quality gate reports results
```

### With Quality Gates (Deployment Validation):
```
1. Deploy to staging
2. BrowserTools: Validate key pages load
3. Report to quality workstream
4. Approve/reject deployment
```

## Safety Considerations

### Rate Limiting
- Respect robots.txt
- Add delays between requests
- Don't overwhelm servers
- Use ethical scraping practices

### Error Handling
```python
try:
    browser.navigate(url)
    data = browser.get_text('.content')
except TimeoutError:
    # Handle timeout gracefully
    return None
except ElementNotFoundError:
    # Handle missing element
    return default_value
```

### Authentication
- Handle login flows securely
- Don't log sensitive credentials
- Use environment variables
- Clear session data after use

## Quality Gates
When using BrowserTools, ensure:
- [ ] Rate limiting respected
- [ ] Errors handled gracefully
- [ ] Timeouts set appropriately
- [ ] Browser instances cleaned up
- [ ] Screenshots/PDFs stored securely
- [ ] Sensitive data not logged
- [ ] robots.txt compliance verified
