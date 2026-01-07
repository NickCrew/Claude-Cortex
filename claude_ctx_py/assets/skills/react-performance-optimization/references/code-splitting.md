# Code Splitting Patterns

## React.lazy and Suspense

**Load components on demand for smaller initial bundles:**
```jsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Lazy-loaded route components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Reports = lazy(() => import('./pages/Reports'));
const Settings = lazy(() => import('./pages/Settings'));

// Component-level code splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

function DataVisualization({ data, showChart }) {
  return (
    <div>
      <h2>Data Overview</h2>
      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <HeavyChart data={data} />
        </Suspense>
      )}
    </div>
  );
}
```

**Benefits:**
- Reduces initial bundle size (faster First Contentful Paint)
- Loads code only when needed (better caching)
- Route-based splitting: Users only download visited pages

**Best practices:**
- Split by routes first (biggest impact)
- Split heavy components (charts, editors, modals)
- Provide meaningful loading fallbacks
- Preload critical routes with `<link rel="preload">`

## Bundle Optimization

**Reduce bundle size with smart imports and tree shaking:**
```jsx
// BAD: Imports entire library
import _ from 'lodash';
import { Button, Modal, Table, Form } from 'antd';

// GOOD: Import only needed functions
import debounce from 'lodash/debounce';
import groupBy from 'lodash/groupBy';

// GOOD: Tree-shakeable imports (if library supports it)
import { Button } from 'antd/es/button';
import { Modal } from 'antd/es/modal';

// Dynamic imports for heavy libraries
const PDFViewer = lazy(() => import('react-pdf-viewer'));
const CodeEditor = lazy(() => import('@monaco-editor/react'));

// Conditional polyfill loading
async function loadPolyfills() {
  if (!window.IntersectionObserver) {
    await import('intersection-observer');
  }
}
```

## Bundle Analysis Tools

```bash
# Webpack Bundle Analyzer
npm install --save-dev webpack-bundle-analyzer

# Vite Bundle Visualizer
npm install --save-dev rollup-plugin-visualizer

# Analyze bundle composition
npm run build -- --stats
npx webpack-bundle-analyzer dist/stats.json
```

**Analysis workflow:**
1. Generate production build with stats
2. Open bundle visualizer
3. Identify large dependencies
4. Check for duplicate code
5. Find optimization opportunities (lazy loading, tree shaking)
6. Measure improvement after changes
