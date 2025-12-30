# Profiling and Debugging

## React DevTools Profiler

**Identify and diagnose performance bottlenecks:**

### Programmatic Profiling
```jsx
import { Profiler } from 'react';

function onRenderCallback(
  id,        // Component being profiled
  phase,     // "mount" or "update"
  actualDuration,  // Time spent rendering
  baseDuration,    // Estimated time without memoization
  startTime,       // When render started
  commitTime,      // When committed to DOM
  interactions     // Set of interactions
) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);

  // Send to analytics
  if (actualDuration > 16) { // More than one frame (60fps)
    sendToAnalytics({ id, phase, actualDuration });
  }
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
      <Profiler id="Sidebar" onRender={onRenderCallback}>
        <Sidebar />
      </Profiler>
    </Profiler>
  );
}
```

### DevTools Profiler Workflow

**Step 1: Record a profile**
1. Open React DevTools → Profiler tab
2. Click record button (red circle)
3. Interact with your app (click, type, navigate)
4. Click stop button

**Step 2: Analyze flame graph**
- Yellow/red bars = slow components
- Bar width = time spent rendering
- Click bar to see component details
- Look for unexpected renders

**Step 3: Check ranked view**
- Components sorted by render time
- Identify most expensive renders
- Focus optimization efforts here

**Step 4: Investigate renders**
- Why did this component render?
- Did props/state actually change?
- Is memo/useMemo working correctly?

**Step 5: Compare profiles**
- Record baseline profile
- Apply optimizations
- Record new profile
- Compare improvements

## Browser Performance API

**Custom performance measurements:**
```jsx
// Measure component render time
performance.mark('render-start');
// ... component render logic ...
performance.mark('render-end');
performance.measure('component-render', 'render-start', 'render-end');

const measure = performance.getEntriesByName('component-render')[0];
console.log(`Render took: ${measure.duration}ms`);

// Measure async operations
async function fetchData() {
  performance.mark('fetch-start');
  const data = await fetch('/api/data');
  performance.mark('fetch-end');
  performance.measure('data-fetch', 'fetch-start', 'fetch-end');
}
```

## Why Did You Render

**Debug unnecessary re-renders in development:**
```bash
npm install --save-dev @welldone-software/why-did-you-render
```

```jsx
// wdyr.js
import React from 'react';

if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = require('@welldone-software/why-did-you-render');
  whyDidYouRender(React, {
    trackAllPureComponents: true,
    trackHooks: true,
    logOnDifferentValues: true,
  });
}
```

```jsx
// Component.jsx
function MyComponent(props) {
  // ...
}

MyComponent.whyDidYouRender = true;

export default MyComponent;
```

## Chrome DevTools Performance Tab

**Identify non-React performance issues:**

1. Open Chrome DevTools → Performance tab
2. Click record → Interact with app → Stop
3. Analyze timeline:
   - **Scripting** (yellow): JavaScript execution
   - **Rendering** (purple): Style calculations, layout
   - **Painting** (green): Pixel painting
   - **System** (gray): Browser overhead

**Look for:**
- Long tasks (>50ms) blocking the main thread
- Excessive layout recalculations
- Forced synchronous layout (layout thrashing)
- Large JavaScript bundles

## Lighthouse Performance Audit

**Automated performance analysis:**
```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://your-app.com --view

# CI integration
lighthouse https://your-app.com --output json --output-path ./report.json
```

**Key metrics:**
- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Total Blocking Time (TBT)**: < 200ms
- **Cumulative Layout Shift (CLS)**: < 0.1

## Performance Monitoring in Production

**Real User Monitoring (RUM):**
```jsx
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Report Web Vitals
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(sendToAnalytics);
      getFID(sendToAnalytics);
      getFCP(sendToAnalytics);
      getLCP(sendToAnalytics);
      getTTFB(sendToAnalytics);
    });
  }, []);

  return <div>...</div>;
}

function sendToAnalytics({ name, value, id }) {
  // Send to analytics service (Google Analytics, Datadog, etc.)
  gtag('event', name, {
    event_category: 'Web Vitals',
    value: Math.round(value),
    event_label: id,
    non_interaction: true,
  });
}
```

## Common Performance Patterns to Look For

### 1. Unnecessary Re-renders
- Component renders but props/state unchanged
- Parent re-renders causing child cascade
- Missing memo on expensive child components

### 2. Expensive Computations
- Complex calculations on every render
- Missing useMemo for derived data
- Sorting/filtering large arrays without memoization

### 3. Memory Leaks
- Event listeners not cleaned up
- Timers not cleared
- Subscriptions not unsubscribed

### 4. Bundle Size Issues
- Large dependencies imported unnecessarily
- Missing code splitting
- Duplicate dependencies in bundle
