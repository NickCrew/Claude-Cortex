# Performance Optimization Flags

Flags for performance analysis, profiling, and optimization workflows.

**Estimated tokens: ~180**

---

**--perf / --optimize-performance**
- Trigger: Slow response times, high resource usage, scale problems, performance SLAs
- Behavior: Enable performance-first mindset with profiling and optimization
- Auto-enables: performance-engineer agent, profiling tools, benchmarking capabilities
- Focuses: Hot paths, memory leaks, algorithm complexity, caching strategies, database queries
- Methodology: Measure → Analyze → Optimize → Validate (no premature optimization)
- Reports: Performance metrics, bottleneck analysis, optimization recommendations

**--profile-first**
- Trigger: "Make it faster" requests, performance issues without clear root cause
- Behavior: Measure before optimizing - require profiling data before suggesting changes
- Enforces: Data-driven optimization (no guessing about bottlenecks)
- Requires: Baseline metrics collection, profiling tool setup, measurement methodology
- Reports: Baseline metrics → Proposed changes → Expected impact → Post-change validation
- Prevents: Premature optimization, cargo cult performance fixes, unmeasured changes
- Tools: cProfile, py-spy (Python), perf, flamegraphs (systems), Chrome DevTools (web)

**--benchmark**
- Trigger: Performance-critical code, SLA requirements, before/after comparisons
- Behavior: Generate benchmarks for all changes with statistical significance
- Auto-creates: Benchmark suite, before/after performance comparisons, regression tests
- Ensures: No performance regressions introduced, improvements are measurable
- Reports: P50/P95/P99 latencies, throughput, resource utilization, comparison charts
- Validates: Statistical significance (not noise), consistent test environment
- Formats: pytest-benchmark, JMH (Java), Criterion (Rust), console.time (JS)

**--cache-strategy**
- Trigger: Repeated expensive operations, database query optimization, API rate limits
- Behavior: Design and implement intelligent caching strategies
- Analyzes: Cache hit rates, invalidation patterns, memory usage, staleness tolerance
- Suggests: Cache levels (in-memory, Redis, CDN), eviction policies (LRU, TTL), cache keys
- Validates: Cache coherence, thundering herd prevention, cache warming strategies
- Patterns: Read-through, write-through, write-behind, cache-aside

**--scale-ready**
- Trigger: Anticipated load increases, capacity planning, production scaling
- Behavior: Ensure code is ready for horizontal and vertical scaling
- Analyzes: Stateless design, database connection pooling, shared nothing architecture
- Validates: No race conditions, no memory leaks, efficient resource cleanup
- Considers: Load balancing, auto-scaling triggers, graceful degradation
- Reports: Scalability bottlenecks, resource requirements per RPS, scaling cost estimates
