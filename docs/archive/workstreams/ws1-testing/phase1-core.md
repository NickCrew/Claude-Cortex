# Phase 1: Core Module Testing

## Objective
Establish comprehensive test coverage for critical business logic and core modules, achieving 40% overall coverage.

## Timeline
- **Start**: Nov 27, 2025
- **Target End**: Dec 11, 2025 (2 weeks)
- **Status**: 🟡 In Progress

## Coverage Targets

### Overall Target: 40% Coverage

### Per-Module Targets (Minimum 60% each)

| Module | Current | Target | Priority | Status |
|--------|---------|--------|----------|--------|
| `core/agents.py` | TBD | 70% | P0 | 🔴 Not Started |
| `core/base.py` | TBD | 70% | P0 | 🔴 Not Started |
| `intelligence.py` | ~40% | 80% | P0 | 🟡 Partial |
| `metrics.py` | ~30% | 70% | P1 | 🟡 Partial |
| `cli.py` | TBD | 60% | P1 | 🔴 Not Started |
| `analytics.py` | TBD | 70% | P1 | 🔴 Not Started |
| `versioner.py` | ~25% | 65% | P2 | 🟡 Partial |
| `core/composer.py` | TBD | 65% | P2 | 🔴 Not Started |
| `core/config.py` | TBD | 70% | P2 | 🔴 Not Started |

## High-Priority Modules (P0)

### 1. core/agents.py - Agent System Backbone
**Test File**: `tests/unit/core/test_agents_comprehensive.py`
**Current Coverage**: Unknown
**Target**: 70%

**Critical Test Areas**:
- [ ] Agent lifecycle (initialization, activation, deactivation)
- [ ] Agent configuration loading and validation
- [ ] Agent state management
- [ ] Agent communication protocols
- [ ] Agent error handling and recovery
- [ ] Agent metadata and capabilities
- [ ] Concurrent agent operations
- [ ] Agent discovery and registration

**Test Scenarios**:
```python
# Core functionality
- test_agent_initialization()
- test_agent_activation()
- test_agent_deactivation()
- test_agent_config_load()
- test_agent_config_validation()
- test_agent_state_transitions()

# Error handling
- test_agent_invalid_config()
- test_agent_activation_failure()
- test_agent_concurrent_operations()
- test_agent_state_corruption_recovery()

# Edge cases
- test_agent_multiple_activations()
- test_agent_missing_dependencies()
- test_agent_circular_dependencies()
```

**Acceptance Criteria**:
- [ ] All public methods tested
- [ ] Error paths covered
- [ ] State transitions validated
- [ ] Concurrent operations safe
- [ ] Configuration validated

---

### 2. core/base.py - Base Classes & Utilities
**Test File**: `tests/unit/core/test_base_comprehensive.py`
**Current Coverage**: Unknown
**Target**: 70%

**Critical Test Areas**:
- [ ] Base class initialization
- [ ] Abstract method enforcement
- [ ] Utility function correctness
- [ ] Type validation and coercion
- [ ] Error handling patterns
- [ ] Common patterns and mixins
- [ ] Serialization/deserialization

**Test Scenarios**:
```python
# Base classes
- test_base_class_instantiation()
- test_abstract_method_enforcement()
- test_inheritance_patterns()
- test_mixin_composition()

# Utilities
- test_utility_functions()
- test_type_validation()
- test_type_coercion()
- test_serialization()
- test_deserialization()

# Error handling
- test_invalid_types()
- test_missing_required_fields()
- test_validation_errors()
```

**Acceptance Criteria**:
- [ ] All base classes tested
- [ ] All utility functions tested
- [ ] Type safety validated
- [ ] Error messages clear
- [ ] Serialization round-trips

---

### 3. intelligence.py - AI Intelligence Layer
**Test File**: `tests/unit/test_intelligence_comprehensive.py`
**Current Coverage**: ~40% (existing tests)
**Target**: 80%

**Critical Test Areas**:
- [x] SessionContext creation and validation (existing)
- [x] AgentRecommendation logic (existing)
- [ ] WorkflowPrediction accuracy
- [ ] PatternLearner training and prediction
- [ ] ContextDetector detection logic
- [ ] IntelligentAgent orchestration
- [ ] Pattern storage and retrieval
- [ ] Learning algorithm validation

**Additional Test Scenarios Needed**:
```python
# Pattern learning
- test_pattern_learner_training()
- test_pattern_learner_prediction()
- test_pattern_learner_model_persistence()
- test_pattern_learner_incremental_learning()

# Context detection
- test_context_detector_file_patterns()
- test_context_detector_directory_analysis()
- test_context_detector_framework_detection()
- test_context_detector_confidence_scoring()

# Integration
- test_intelligent_agent_recommendation_flow()
- test_intelligent_agent_workflow_prediction()
- test_intelligent_agent_pattern_application()
```

**Acceptance Criteria**:
- [ ] All dataclasses tested
- [ ] Pattern learning validated
- [ ] Context detection accurate
- [ ] Recommendations sensible
- [ ] Performance acceptable

---

## Medium-Priority Modules (P1)

### 4. metrics.py - Metrics Collection
**Test File**: `tests/unit/test_metrics_comprehensive.py`
**Current Coverage**: ~30% (existing tests)
**Target**: 70%

**Critical Test Areas**:
- [x] Basic metric collection (existing)
- [ ] Metric aggregation and rollups
- [ ] Metric persistence and retrieval
- [ ] Metric export formats
- [ ] Performance metric calculation
- [ ] Metric validation and sanitization

**Additional Test Scenarios**:
```python
- test_metric_collection_aggregation()
- test_metric_persistence()
- test_metric_export_json()
- test_metric_export_prometheus()
- test_performance_metric_calculation()
- test_metric_validation()
- test_concurrent_metric_updates()
```

---

### 5. cli.py - CLI Command Handlers
**Test File**: `tests/unit/test_cli_comprehensive.py`
**Current Coverage**: Unknown
**Target**: 60%

**Critical Test Areas**:
- [ ] Command parsing and validation
- [ ] Command execution flow
- [ ] Error handling and user feedback
- [ ] Help text generation
- [ ] Command composition
- [ ] Flag/option handling
- [ ] Interactive prompts

**Test Scenarios**:
```python
- test_command_parsing()
- test_command_execution()
- test_invalid_command_handling()
- test_help_text_generation()
- test_flag_handling()
- test_option_validation()
- test_interactive_prompt()
- test_command_chaining()
```

---

### 6. analytics.py - Analytics Engine
**Test File**: `tests/unit/test_analytics_comprehensive.py`
**Current Coverage**: Unknown
**Target**: 70%

**Critical Test Areas**:
- [ ] Event tracking
- [ ] Usage pattern analysis
- [ ] Performance analysis
- [ ] Report generation
- [ ] Data aggregation
- [ ] Privacy and sanitization

**Test Scenarios**:
```python
- test_event_tracking()
- test_usage_pattern_detection()
- test_performance_analysis()
- test_report_generation()
- test_data_aggregation()
- test_privacy_sanitization()
- test_analytics_export()
```

---

## Lower-Priority Modules (P2)

### 7. versioner.py - Version Management
**Test File**: `tests/unit/test_versioner.py` (expand existing)
**Current Coverage**: ~25%
**Target**: 65%

**Additional Coverage Needed**:
- [ ] Version comparison logic
- [ ] Migration handling
- [ ] Compatibility checking
- [ ] Version constraints
- [ ] Upgrade/downgrade paths

---

### 8. core/composer.py - Component Composition
**Test File**: `tests/unit/core/test_composer_comprehensive.py`
**Current Coverage**: Unknown
**Target**: 65%

**Critical Test Areas**:
- [ ] Component registration
- [ ] Dependency resolution
- [ ] Composition validation
- [ ] Lifecycle management

---

### 9. core/config.py - Configuration Management
**Test File**: `tests/unit/core/test_config_comprehensive.py`
**Current Coverage**: Unknown
**Target**: 70%

**Critical Test Areas**:
- [ ] Config loading from files
- [ ] Config validation
- [ ] Config merging
- [ ] Environment variable handling
- [ ] Default values

---

## Test Infrastructure Setup

### Required Test Directories
```bash
tests/unit/core/          # Core module tests
tests/unit/core/__init__.py
tests/unit/core/test_agents_comprehensive.py
tests/unit/core/test_base_comprehensive.py
tests/unit/core/test_composer_comprehensive.py
tests/unit/core/test_config_comprehensive.py
```

### Shared Fixtures (tests/conftest.py)
- [ ] Mock agent configurations
- [ ] Temporary file system fixtures
- [ ] Mock intelligence patterns
- [ ] Performance timing fixtures
- [ ] Mock CLI environments

### Test Utilities Needed
```python
# tests/utils/test_helpers.py
- create_mock_agent()
- create_mock_session_context()
- create_temp_workspace()
- assert_metric_valid()
- assert_coverage_threshold()
```

---

## Immediate Actions (This Session)

### 1. Fix Test Collection Error
**Priority**: P0
**Status**: 🔴 Blocked
```bash
# Current error: 1 error in test collection
# Action: Identify and fix collection error
pytest --collect-only tests/ 2>&1 | grep -A 10 "ERROR"
```

### 2. Create Core Test Directory Structure
**Priority**: P0
**Status**: 🔴 Not Started
```bash
mkdir -p tests/unit/core
touch tests/unit/core/__init__.py
touch tests/unit/core/.gitkeep
```

### 3. Create Skeleton Test Files
**Priority**: P0
**Status**: 🔴 Not Started
- `tests/unit/core/test_agents_comprehensive.py`
- `tests/unit/core/test_base_comprehensive.py`
- `tests/unit/core/test_config_comprehensive.py`

### 4. Baseline Coverage Measurement
**Priority**: P1
**Status**: 🔴 Not Started
```bash
# Run coverage for each core module
pytest --cov=claude_ctx_py.core.agents --cov-report=term-missing
pytest --cov=claude_ctx_py.core.base --cov-report=term-missing
pytest --cov=claude_ctx_py.intelligence --cov-report=term-missing
```

---

## Quality Gates (Phase 1 Exit Criteria)

### Coverage Gates
- [ ] Overall coverage ≥40%
- [ ] Core modules (P0) ≥70% each
- [ ] Medium priority (P1) ≥60% each
- [ ] No module <50% coverage

### Test Quality Gates
- [ ] All tests passing (100% pass rate)
- [ ] No flaky tests (3 consecutive runs)
- [ ] Test execution time <2 minutes
- [ ] No test collection errors

### Code Quality Gates
- [ ] All new test code type-checked (mypy)
- [ ] All new test code linted (ruff)
- [ ] Test code follows patterns
- [ ] Test code documented

### Documentation Gates
- [ ] All test modules have docstrings
- [ ] Complex test scenarios documented
- [ ] Test data and fixtures documented
- [ ] Coverage gaps documented

---

## Progress Tracking

### Daily Metrics
Track daily:
- Overall coverage %
- Module-specific coverage %
- Test count
- Pass rate
- Execution time

### Weekly Review
Review weekly:
- Progress vs targets
- Blockers and risks
- Adjust priorities
- Plan next week

---

## Risk & Mitigation

### Risk: Low Baseline Coverage
**Impact**: More work than estimated
**Mitigation**: Focus on P0 first, extend timeline if needed

### Risk: Test Collection Error
**Impact**: Blocks new test creation
**Mitigation**: Fix immediately, high priority

### Risk: Complex Modules Hard to Test
**Impact**: Lower coverage than target
**Mitigation**: Use mocking, focus on critical paths

### Risk: Performance Degradation
**Impact**: Slow test suite
**Mitigation**: Monitor execution time, optimize slow tests

---

**Status**: 🟡 Phase 1 In Progress
**Last Updated**: Nov 27, 2025
**Next Review**: Dec 4, 2025
