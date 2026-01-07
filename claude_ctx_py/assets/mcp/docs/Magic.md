# Magic MCP Server

**Purpose**: Modern UI component generation from 21st.dev patterns and design systems

## Triggers
- UI component requests: `/ui`, `/21` commands
- Design system queries and implementations
- Frontend development with modern frameworks
- Component library creation or usage
- Beautiful, accessible UI needs
- Rapid prototyping of interfaces

## Choose When
- **Over manual coding**: When 21st.dev has proven patterns
- **Over generic solutions**: When design consistency matters
- **For modern UI**: React, Vue, Svelte, Tailwind projects
- **For accessibility**: When WCAG compliance is required
- **For speed**: Rapid UI development with quality
- **For consistency**: Maintaining design system standards

## Works Best With
- **Context7**: Magic generates UI → Context7 validates framework usage
- **Sequential**: Sequential designs UX → Magic implements components
- **Super Saiyan**: Magic provides structure → Super Saiyan adds polish

## Core Capabilities
- **Component generation**: Pre-built, accessible UI components
- **Design system integration**: Consistent with 21st.dev patterns
- **Framework adaptation**: React, Vue, Svelte, vanilla JS
- **Accessibility built-in**: WCAG 2.1 AA compliance by default
- **Responsive design**: Mobile-first, adaptive layouts
- **Dark mode support**: Automatic theme switching

## Available Patterns

### Layout Components
- Containers, grids, flex layouts
- Sidebar navigation, headers, footers
- Card layouts, masonry grids
- Split views, panels

### Interactive Components
- Buttons (primary, secondary, ghost, etc.)
- Forms (inputs, selects, checkboxes, radio)
- Modals, dialogs, drawers
- Dropdowns, menus, tooltips
- Tabs, accordions, carousels

### Data Display
- Tables (sortable, filterable, paginated)
- Lists (ordered, unordered, description)
- Charts and graphs
- Progress indicators, loaders
- Badges, tags, labels

### Feedback Components
- Toast notifications
- Alert banners
- Loading states
- Empty states
- Error boundaries

## Examples
```
"/ui button primary" → Magic (generates accessible button)
"create a user profile card" → Magic (21st.dev card pattern)
"build a data table with sorting" → Magic (complete table component)
"add dark mode toggle" → Magic (theme switching pattern)
"make a navigation sidebar" → Magic (responsive nav component)
"center this div" → Native CSS (simple styling, no component needed)
```

## Framework Support

### React
```jsx
import { Button, Card } from '@/components/ui'

<Button variant="primary">Click me</Button>
```

### Vue
```vue
<UiButton variant="primary">Click me</UiButton>
```

### Svelte
```svelte
<Button variant="primary">Click me</Button>
```

### Vanilla JS
```javascript
createButton({ variant: 'primary', text: 'Click me' })
```

## Accessibility Standards
All Magic components include:
- ✅ Proper ARIA labels
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Focus management
- ✅ Color contrast (4.5:1 minimum)
- ✅ Touch-friendly hit areas (44x44px minimum)

## Performance Considerations
- **Tree-shakeable**: Only import what you use
- **Lightweight**: Minimal runtime overhead
- **CSS optimized**: Scoped styles, no conflicts
- **Lazy loading**: Load components on demand

## Integration Patterns

### With Super Saiyan (Visual Excellence):
```
1. Magic: Generate base component structure
2. Super Saiyan: Add animations and polish
3. Magic: Ensure accessibility maintained
```

### With Sequential (UX Design):
```
1. Sequential: Reason about UX flow
2. Magic: Generate compliant components
3. Sequential: Validate against requirements
```

## Quality Gates
When using Magic, ensure:
- [ ] Component matches design system
- [ ] Accessibility standards met (WCAG 2.1 AA)
- [ ] Responsive behavior tested
- [ ] Dark mode works correctly
- [ ] Performance acceptable (Lighthouse >90)
- [ ] Framework integration clean
