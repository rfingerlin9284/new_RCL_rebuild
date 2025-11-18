# Tests Directory

This directory contains all test files for the RCL project.

## Structure

Organize tests to mirror the source code structure:
- Unit tests for individual components
- Integration tests for feature workflows
- End-to-end tests for complete user scenarios

## Naming Convention

- Test files should end with `.test.*` or `.spec.*`
- Test names should clearly describe what they're testing
- Group related tests together

## Guidelines

- Tests should be isolated and independent
- Avoid test dependencies or execution order requirements
- Clean up test data and state after each test
- No production code in test files
