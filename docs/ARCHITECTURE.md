# Architecture Overview

## Design Philosophy

The RCL Rebuild follows a clean architecture approach with clear separation of concerns to prevent:

1. **Ghost Code**: Commented-out or unused code
2. **Embedded Prompts**: Unclear TODO comments and development notes
3. **Conflicting Logic**: Feature flags and conditional logic scattered throughout the codebase
4. **Poor Extraction**: Duplicated or poorly organized code

## Architectural Layers

### 1. Presentation Layer (UI/API)
- Handles user interaction or API requests
- No business logic
- Delegates to service layer

### 2. Service Layer (Business Logic)
- Implements business rules and workflows
- Coordinates between different modules
- No direct data access (uses repositories)

### 3. Data Access Layer
- Repository pattern for data operations
- Abstracts data source details
- Provides clean interface to services

### 4. Configuration Layer
- Centralized configuration management
- Environment-based settings
- No scattered feature flags

## Module Organization

```
src/
├── core/           # Core business logic and entities
├── services/       # Business services and workflows
├── repositories/   # Data access layer
├── api/           # API endpoints and controllers (if applicable)
├── utils/         # Shared utilities (pure functions)
└── types/         # Type definitions (if using TypeScript)
```

## Key Principles

### Single Responsibility
Each module, class, and function should have one clear purpose.

### Dependency Injection
Dependencies should be injected, not created within modules. This makes code:
- Testable
- Flexible
- Easier to understand

### Clean Abstractions
Avoid leaky abstractions. Each layer should hide implementation details.

### No Circular Dependencies
Organize code to prevent circular imports/requires.

## Testing Strategy

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interactions between modules
- **E2E Tests**: Test complete user workflows

## Configuration Management

Instead of scattered `if (config.featureEnabled)` checks:

```javascript
// config/features.js
export const createFeatureManager = (config) => ({
  isEnabled: (featureName) => config.features[featureName] === true,
  getImplementation: (featureName) => {
    return isEnabled(featureName) 
      ? implementations.modern[featureName]
      : implementations.legacy[featureName];
  }
});
```

## Code Organization Guidelines

### Good Practice ✅
- One class/module per file
- Clear, descriptive names
- Small, focused functions
- Consistent error handling
- Proper logging

### Avoid ❌
- Large, monolithic files
- Mixed concerns in one module
- Global state
- Hard-coded values
- Commented-out code

## Evolution and Maintenance

When adding new features:

1. Consider which layer it belongs to
2. Create new modules rather than expanding existing ones
3. Update tests alongside code
4. Document architectural decisions
5. Review for adherence to principles

## References

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Coding standards
- [API.md](./API.md) - API documentation
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
