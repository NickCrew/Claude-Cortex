# Progressive Disclosure & Dynamic Loading

**Goal:** Minimize initial payload and load complexity only when needed.

## Strategies

### 1. Component Lazy Loading
- **React:** Use `React.lazy` and `Suspense` for all non-critical routes and heavy modals.
- **Next.js:** Use `dynamic()` imports.
- **Pattern:**
  ```tsx
  const HeavyChart = dynamic(() => import('./HeavyChart'), {
    loading: () => <Skeleton />,
    ssr: false
  });
  ```

### 2. Interaction-Based Loading
- Defer loading of components until the user interacts with a trigger.
- **Example:** Don't load the `SettingsModal` code until the user hovers over the "Settings" button.

### 3. Visibility-Based Loading
- Use `IntersectionObserver` to load components only when they scroll into view.
- **Example:** Below-the-fold content, image galleries, comment sections.

### 4. Progressive Disclosure UI
- **Summary First:** Show high-level stats/summary.
- **Details on Demand:** Reveal complex data tables or forms only upon user action (click/expand).
- **Optimistic UI:** Show the "success" state immediately while the async operation completes.

## Performance Metrics
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms
- **CLS (Cumulative Layout Shift):** < 0.1
