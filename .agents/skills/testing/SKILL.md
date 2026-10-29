---
name: testing
description: Reviews or designs a testing strategy, applying the test pyramid and requirement-driven coverage. Activates when explicitly asked to review test coverage, design a test plan, or audit missing edge cases — not run automatically on every edit.
applies_to: always
---

This is an on-demand deep review — the baseline expectations this project's tests should already meet come from `AGENTS.md` (the `testing` rule).

**Test Pyramid**
- Unit tests: largest layer — fast, isolated, no I/O
- Integration tests: test real collaborators (DB, queue, HTTP client against real service)
- E2E tests: smallest layer — full user journey through the deployed application

**Coverage Requirements**
- Map tests to requirements: each acceptance criterion → at least one test
- Happy path: normal use case executes successfully and returns correct result
- Edge cases: empty input, single item, max size, boundary values
- Error paths: invalid input, downstream failure, auth failure, concurrent modification
- State transitions: every valid state change covered (especially for state machines)

**Unit Tests**
- Each test covers exactly one behavior (single assertion or tightly related group)
- Arrange–Act–Assert (AAA) structure, always
- Test the public interface, not internal implementation
- Mock only external I/O (HTTP, DB, time, random); never mock the class under test
- Parameterized tests for multiple input variants of the same scenario

**Integration Tests**
- Use a real database (in-memory or containerized), not mocks
- Test the repository layer directly with known data
- Test the service layer against a real repository (not mocked)
- Reset state between tests; use transactions rolled back after each test or truncate tables

**Naming**
- `should_returnOrderTotal_whenAllItemsValid` or `givenEmptyCart_whenCheckout_thenThrowException`
- Test file colocated with source file, or in a parallel `test/` tree mirroring `src/`

**What NOT to test**
- Don't test framework behavior (ORM SQL generation, DI container wiring)
- Don't test trivial getters/setters with no logic
- Don't test private methods directly — test through the public interface

**Quality Gates**
- CI enforces a minimum coverage threshold for business-logic layers
- Flaky tests tracked and fixed within one sprint, never silently skipped

Produce: test coverage gaps, missing edge cases, anti-patterns found, and a suggested test matrix.
