# Concurrent Features (React 18+)

## useTransition

**Mark non-urgent updates for better responsiveness:**
```jsx
import { useState, useTransition } from 'react';

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
```

**When to use:**
- Search filtering with live results
- Tab switching with heavy content
- Any UI update that can be delayed for responsiveness

## useDeferredValue

**Defer expensive renders without explicit transitions:**
```jsx
import { useState, useDeferredValue, useMemo } from 'react';

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

**Difference from useTransition:**
- `useTransition`: You control when to defer (wrap updates)
- `useDeferredValue`: React controls when to defer (wrap values)

## Concurrent Rendering Benefits

### Interruptible Rendering
- React can pause expensive work
- Prioritizes user interactions (clicks, typing)
- Resumes work when browser is idle

### Automatic Prioritization
- Urgent updates (user input) render immediately
- Non-urgent updates (filtering, sorting) can wait
- Smoother user experience without manual debouncing

### Better Loading States
```jsx
function App() {
  const [tab, setTab] = useState('home');
  const [isPending, startTransition] = useTransition();

  const handleTabChange = (newTab) => {
    startTransition(() => {
      setTab(newTab);
    });
  };

  return (
    <div>
      <Tabs
        activeTab={tab}
        onChange={handleTabChange}
        isPending={isPending}
      />
      <TabContent tab={tab} />
    </div>
  );
}
```

## Migration Guide

### Before React 18
```jsx
// Manual debouncing for performance
const debouncedSearch = debounce((value) => {
  setResults(searchItems(value));
}, 300);

<input onChange={(e) => debouncedSearch(e.target.value)} />
```

### With React 18
```jsx
// Automatic prioritization with useTransition
const handleSearch = (value) => {
  setQuery(value); // Immediate
  startTransition(() => {
    setResults(searchItems(value)); // Deferred
  });
};

<input onChange={(e) => handleSearch(e.target.value)} />
```

## Performance Comparison

**Without concurrent features:**
- User types → UI freezes during expensive filter
- Perceived lag and unresponsiveness
- Manual debouncing required

**With concurrent features:**
- User types → Input updates immediately
- Filter runs in background
- UI stays responsive
- No manual optimization needed
