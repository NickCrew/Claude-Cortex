---
name: react-performance-optimization
description: React performance optimization patterns using memoization, code splitting, and efficient rendering strategies. Use when optimizing slow React applications, reducing bundle size, or improving user experience with large datasets.
---

# React Performance Optimization

Expert guidance for optimizing React application performance through memoization, code splitting, virtualization, and efficient rendering strategies for building fast, responsive user interfaces.

## When to Use This Skill

- Optimizing slow-rendering React components
- Reducing bundle size for faster initial load times
- Improving responsiveness for large lists or data tables
- Preventing unnecessary re-renders in complex component trees
- Optimizing state management to reduce render cascades
- Improving perceived performance with code splitting
- Debugging performance issues with React DevTools Profiler

## Core Patterns

### 1. React.memo for Component Memoization

**Prevent unnecessary re-renders of functional components:**
```jsx
import React, { memo } from 'react';

const ExpensiveComponent = memo(({ data, onAction }) => {
  console.log('Rendering ExpensiveComponent');

  return (
    <div>
      <h3>{data.title}</h3>
      <p>{data.description}</p>
      <button onClick={onAction}>Action</button>
    </div>
  );
});

// Custom comparison for complex props
const UserCard = memo(
  ({ user, settings }) => (
    <div>
      <h2>{user.name}</h2>
      <span>{user.email}</span>
    </div>
  ),
  (prevProps, nextProps) => {
    // Return true if props are equal (skip render)
    return prevProps.user.id === nextProps.user.id &&
           prevProps.settings.theme === nextProps.settings.theme;
  }
);
```

**When to use:**
- Component renders with same props frequently
- Expensive rendering logic (complex JSX, heavy computations)
- Child components in frequently updating parent
- List items with stable props

**When NOT to use:**
- Props change on every render (comparison overhead)
- Simple, fast-rendering components (unnecessary optimization)

### 2. useMemo for Expensive Computations

**Cache expensive calculation results:**
```jsx
import { useMemo } from 'react';

function DataAnalyzer({ items, filters }) {
  // Recalculates only when items or filters change
  const filteredAndSorted = useMemo(() => {
    console.log('Computing filtered data');

    return items
      .filter(item => filters.categories.includes(item.category))
      .filter(item => item.price >= filters.minPrice)
      .sort((a, b) => b.score - a.score);
  }, [items, filters]);

  const statistics = useMemo(() => {
    return {
      total: filteredAndSorted.length,
      average: filteredAndSorted.reduce((sum, item) => sum + item.price, 0) /
               filteredAndSorted.length,
      maxPrice: Math.max(...filteredAndSorted.map(item => item.price))
    };
  }, [filteredAndSorted]);

  return (
    <div>
      <p>Total items: {statistics.total}</p>
      <p>Average price: ${statistics.average.toFixed(2)}</p>
    </div>
  );
}
```

**Use cases:**
- Expensive array operations (filter, map, sort, reduce)
- Complex mathematical calculations
- Data transformations and aggregations
- Creating derived data structures

**Performance impact:**
- Without useMemo: Computation runs every render
- With useMemo: Computation runs only when dependencies change

### 3. useCallback for Stable Function References

**Prevent child re-renders caused by function reference changes:**
```jsx
import { useState, useCallback, memo } from 'react';

const ListItem = memo(({ item, onDelete, onEdit }) => {
  console.log('Rendering ListItem:', item.id);
  return (
    <div>
      <span>{item.name}</span>
      <button onClick={() => onEdit(item.id)}>Edit</button>
      <button onClick={() => onDelete(item.id)}>Delete</button>
    </div>
  );
});

function ItemList({ items }) {
  const [selectedId, setSelectedId] = useState(null);

  // Stable function reference across renders
  const handleDelete = useCallback((id) => {
    console.log('Deleting:', id);
    // API call to delete
  }, []); // No dependencies = never recreated

  const handleEdit = useCallback((id) => {
    setSelectedId(id);
    // Open edit modal
  }, [setSelectedId]); // Recreated only if setSelectedId changes

  return (
    <div>
      {items.map(item => (
        <ListItem
          key={item.id}
          item={item}
          onDelete={handleDelete}
          onEdit={handleEdit}
        />
      ))}
    </div>
  );
}
```

**Critical rule:**
- Use `useCallback` when passing functions to memoized child components
- Without it, new function reference on every render defeats memo optimization

### 4. Code Splitting with React.lazy and Suspense

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

### 5. Virtualization for Large Lists

**Render only visible items to handle thousands of rows:**
```jsx
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style} className="list-item">
      <h4>{items[index].title}</h4>
      <p>{items[index].description}</p>
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}

// Variable size list (different heights)
import { VariableSizeList } from 'react-window';

function DynamicList({ items }) {
  const getItemSize = (index) => {
    return items[index].type === 'header' ? 60 : 40;
  };

  return (
    <VariableSizeList
      height={600}
      itemCount={items.length}
      itemSize={getItemSize}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{items[index].content}</div>
      )}
    </VariableSizeList>
  );
}
```

**Performance impact:**
- Traditional list with 10,000 items: 10,000 DOM nodes
- Virtualized list: ~20 DOM nodes (only visible + buffer)
- Result: 500x reduction in DOM nodes

**Libraries:**
- `react-window`: Lightweight, simple API (recommended)
- `react-virtualized`: Feature-rich, larger bundle
- `@tanstack/react-virtual`: Modern, headless virtualization

### 6. Key Optimization for Lists

**Proper keys prevent unnecessary re-renders:**
```jsx
// BAD: Index as key (breaks when reordering/filtering)
{items.map((item, index) => (
  <Item key={index} data={item} />
))}

// BAD: Random keys (forces complete re-render every time)
{items.map(item => (
  <Item key={Math.random()} data={item} />
))}

// GOOD: Stable unique identifier
{items.map(item => (
  <Item key={item.id} data={item} />
))}

// GOOD: Composite key when no unique ID exists
{items.map(item => (
  <Item key={`${item.userId}-${item.timestamp}`} data={item} />
))}
```

**Why keys matter:**
- React uses keys to track element identity
- Stable keys enable efficient diffing and reconciliation
- Index keys break when list order changes
- Missing keys force React to destroy/recreate components

## Advanced Patterns

### 7. State Management for Performance

**Optimize state structure to minimize re-renders:**
```jsx
import { useState, createContext, useContext } from 'react';

// BAD: Single large state object causes many re-renders
function BadApp() {
  const [state, setState] = useState({
    user: {},
    settings: {},
    data: [],
    ui: { modal: false, sidebar: true }
  });

  // Changing modal state re-renders entire tree
  const toggleModal = () => setState(prev => ({
    ...prev,
    ui: { ...prev.ui, modal: !prev.ui.modal }
  }));
}

// GOOD: Split state by update frequency
function GoodApp() {
  const [user, setUser] = useState({});
  const [settings, setSettings] = useState({});
  const [data, setData] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);

  // Only components using modalOpen re-render
}

// BEST: Context splitting for shared state
const UserContext = createContext();
const DataContext = createContext();

function App() {
  const [user, setUser] = useState({});
  const [data, setData] = useState([]);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <DataContext.Provider value={{ data, setData }}>
        <Dashboard />
      </DataContext.Provider>
    </UserContext.Provider>
  );
}

// Components only subscribe to needed context
function UserProfile() {
  const { user } = useContext(UserContext); // Only re-renders on user change
  return <div>{user.name}</div>;
}
```

**State management strategies:**
- Local state first (useState, useReducer)
- Context for shared state (split by update frequency)
- External state managers for complex apps (Zustand, Jotai, Redux)
- Server state libraries (React Query, SWR) for API data

### 8. Bundle Optimization

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

**Bundle analysis tools:**
```bash
# Webpack Bundle Analyzer
npm install --save-dev webpack-bundle-analyzer

# Vite Bundle Visualizer
npm install --save-dev rollup-plugin-visualizer

# Analyze bundle composition
npm run build -- --stats
npx webpack-bundle-analyzer dist/stats.json
```

### 9. React DevTools Profiler

**Identify and diagnose performance bottlenecks:**
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

**DevTools Profiler workflow:**
1. Open React DevTools → Profiler tab
2. Start recording → Interact with app → Stop recording
3. Analyze flame graph for slow components
4. Check "Ranked" view to find most expensive renders
5. Investigate components with yellow/red bars
6. Look for unnecessary renders (same props/state)

### 10. Concurrent Features (React 18+)

**Leverage concurrent rendering for better responsiveness:**
```jsx
import { useState, useTransition, useDeferredValue } from 'react';

// useTransition: Mark non-urgent updates
function SearchApp() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (value) => {
    setQuery(value); // Urgent: Update input immediately

    startTransition(() => {
      // Non-urgent: Can be interrupted
      setResults(searchItems(value));
    });
  };

  return (
    <div>
      <input value={query} onChange={(e) => handleSearch(e.target.value)} />
      {isPending && <Spinner />}
      <ResultsList results={results} />
    </div>
  );
}

// useDeferredValue: Defer expensive renders
function FilteredList({ items, searchTerm }) {
  const deferredSearchTerm = useDeferredValue(searchTerm);

  // Filters using deferred value (doesn't block typing)
  const filteredItems = useMemo(() => {
    return items.filter(item =>
      item.name.toLowerCase().includes(deferredSearchTerm.toLowerCase())
    );
  }, [items, deferredSearchTerm]);

  return (
    <div>
      <p>Showing {filteredItems.length} results</p>
      {filteredItems.map(item => <Item key={item.id} data={item} />)}
    </div>
  );
}
```

**Concurrent features benefits:**
- Keeps UI responsive during expensive operations
- Automatically prioritizes user interactions
- Enables smooth transitions without blocking

## Performance Best Practices

### 1. Profiling Before Optimizing

**Measure first, optimize second:**
```jsx
// Use React DevTools Profiler to find actual bottlenecks
// Don't guess - measure!

// Browser Performance API for custom measurements
performance.mark('render-start');
// ... component render logic ...
performance.mark('render-end');
performance.measure('component-render', 'render-start', 'render-end');

const measure = performance.getEntriesByName('component-render')[0];
console.log(`Render took: ${measure.duration}ms`);
```

### 2. Avoid Premature Optimization

**Optimization hierarchy:**
```
1. Make it work (correctness first)
2. Measure performance (identify real bottlenecks)
3. Optimize hot paths (only slow parts)
4. Measure again (verify improvement)
```

**Common pitfalls:**
- Overusing memo/useMemo/useCallback (added complexity, marginal gains)
- Optimizing components that render quickly
- Adding memoization without measuring impact

### 3. Optimize Dependencies

**Control re-computation with proper dependencies:**
```jsx
// BAD: Missing dependencies (stale closures)
const fetchData = useCallback(() => {
  fetch(`/api/data?filter=${filter}`);
}, []); // Missing filter dependency

// BAD: Object/array dependencies (always new reference)
const config = { url: '/api', filter };
useEffect(() => {
  fetchData(config);
}, [config]); // New object every render

// GOOD: Primitive dependencies
useEffect(() => {
  fetchData({ url: '/api', filter });
}, [filter, fetchData]);

// GOOD: Stable reference with useMemo
const config = useMemo(() => ({ url: '/api', filter }), [filter]);
```

### 4. Image Optimization

**Lazy load images and use modern formats:**
```jsx
// Native lazy loading
function ImageGallery({ images }) {
  return (
    <div>
      {images.map(img => (
        <img
          key={img.id}
          src={img.url}
          loading="lazy"
          alt={img.alt}
          decoding="async"
        />
      ))}
    </div>
  );
}

// Intersection Observer for custom loading
import { useEffect, useRef, useState } from 'react';

function LazyImage({ src, alt }) {
  const [isLoaded, setIsLoaded] = useState(false);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsLoaded(true);
          observer.disconnect();
        }
      },
      { rootMargin: '50px' }
    );

    if (imgRef.current) observer.observe(imgRef.current);

    return () => observer.disconnect();
  }, []);

  return (
    <img
      ref={imgRef}
      src={isLoaded ? src : '/placeholder.jpg'}
      alt={alt}
    />
  );
}
```

## Common Pitfalls

### 1. Inline Object/Array Props
```jsx
// BAD: New object every render defeats memo
<Component config={{ theme: 'dark' }} />

// GOOD: Stable reference
const config = useMemo(() => ({ theme: 'dark' }), []);
<Component config={config} />

// BEST: Extract to constant if truly static
const CONFIG = { theme: 'dark' };
<Component config={CONFIG} />
```

### 2. Anonymous Functions in JSX
```jsx
// BAD: New function every render
<button onClick={() => handleClick(id)}>Click</button>

// GOOD: useCallback with stable reference
const handleButtonClick = useCallback(() => handleClick(id), [id]);
<button onClick={handleButtonClick}>Click</button>

// ACCEPTABLE: For top-level handlers (not passed to memoized children)
<button onClick={(e) => console.log(e.target.value)}>Click</button>
```

### 3. Deriving State Unnecessarily
```jsx
// BAD: Duplicate state causes sync issues
const [items, setItems] = useState([]);
const [itemCount, setItemCount] = useState(0);

// GOOD: Derive during render
const [items, setItems] = useState([]);
const itemCount = items.length; // Always in sync
```

### 4. Over-Memoization
```jsx
// BAD: Unnecessary memoization adds overhead
const SimpleComponent = memo(({ text }) => <span>{text}</span>);

// GOOD: Only memoize if expensive or frequently re-rendered with same props
const ExpensiveComponent = memo(({ data }) => {
  // Complex rendering logic
  return <ComplexVisualization data={processData(data)} />;
});
```

## Resources

- **React Docs - Performance**: https://react.dev/learn/render-and-commit
- **React DevTools**: Chrome/Firefox extension for profiling
- **react-window**: https://github.com/bvaughn/react-window
- **Million.js**: Compiler for faster React (drop-in optimization)
- **Bundle analyzers**: webpack-bundle-analyzer, vite-bundle-visualizer
- **Lighthouse**: Automated performance auditing in Chrome DevTools

## Best Practices Summary

1. Profile with React DevTools before optimizing
2. Use React.memo for expensive components with stable props
3. Apply useMemo for costly computations, not cheap operations
4. Combine useCallback with memo for passing functions to children
5. Implement code splitting for routes and heavy components
6. Use virtualization for lists with >100 items
7. Provide stable keys for list items (never use index for dynamic lists)
8. Split state by update frequency to minimize re-renders
9. Leverage concurrent features (useTransition, useDeferredValue) for responsiveness
10. Measure optimization impact - verify improvements with profiling
