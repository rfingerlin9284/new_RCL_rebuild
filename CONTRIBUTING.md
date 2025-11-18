# Contributing to RCL Rebuild

Thank you for contributing! This document outlines the standards and practices for maintaining a clean, organized codebase.

## Code Quality Standards

### 1. No Ghost Code

**Ghost code** refers to commented-out code, unused imports, or dead code paths.

❌ **Don't:**
```javascript
// const oldFunction = () => {
//   console.log("This used to do something");
// };

function newFunction() {
  console.log("Current implementation");
}
```

✅ **Do:**
```javascript
function newFunction() {
  console.log("Current implementation");
}
```

**Rationale:** Use git history to track old code. Commented code clutters the codebase and creates confusion.

### 2. No Embedded Prompts or Unclear Comments

❌ **Don't:**
```javascript
// TODO: fix this later
// HACK: temporary solution
// ???: why does this work?
```

✅ **Do:**
```javascript
// Issue #123: Implement proper error handling
// Workaround for API limitation documented in docs/API.md#known-issues
```

**Rationale:** Comments should add value. Link to issues/documentation for context.

### 3. Separated and Clear Logic

**Avoid conflicting or gated logic without proper abstraction.**

❌ **Don't:**
```javascript
function processData(data) {
  if (FEATURE_FLAG_A && !FEATURE_FLAG_B) {
    // path 1
  } else if (FEATURE_FLAG_B || LEGACY_MODE) {
    // path 2
  } else {
    // path 3
  }
}
```

✅ **Do:**
```javascript
// config/features.js
export const getProcessingStrategy = () => {
  return config.useNewProcessor 
    ? new ModernProcessor() 
    : new LegacyProcessor();
};

// src/processor.js
function processData(data) {
  const processor = getProcessingStrategy();
  return processor.process(data);
}
```

**Rationale:** Strategy pattern or dependency injection makes logic testable and maintainable.

### 4. Clean Code Extraction

Extract reusable logic into well-named, single-purpose modules.

❌ **Don't:**
```javascript
function doEverything(user, data, options) {
  // 100 lines of mixed concerns
  const validated = /* validation logic */;
  const transformed = /* transformation logic */;
  const result = /* business logic */;
  /* logging */;
  /* error handling */;
  return result;
}
```

✅ **Do:**
```javascript
// src/validation/userValidator.js
export const validateUser = (user) => { /* ... */ };

// src/transform/dataTransformer.js
export const transformData = (data) => { /* ... */ };

// src/services/userService.js
export const processUserData = (user, data, options) => {
  const validatedUser = validateUser(user);
  const transformedData = transformData(data);
  return applyBusinessLogic(validatedUser, transformedData, options);
};
```

**Rationale:** Small, focused modules are easier to test, understand, and maintain.

## File Organization

### Directory Structure

- **`src/`**: All production source code
  - Organize by feature or domain, not by file type
  - Example: `src/users/`, `src/orders/` (not `src/models/`, `src/controllers/`)

- **`tests/`**: All test files
  - Mirror the `src/` structure
  - Name tests clearly: `userService.test.js`

- **`docs/`**: All documentation
  - Keep documentation close to the code but separate
  - Update docs with code changes

- **`config/`**: Configuration files only
  - No business logic in config files
  - Use environment variables for deployment-specific values

### Naming Conventions

- **Files**: `camelCase.js` or `kebab-case.js` (be consistent)
- **Classes**: `PascalCase`
- **Functions**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE`

## Pull Request Guidelines

1. **Small, focused changes**: One feature or fix per PR
2. **No unrelated changes**: Don't mix refactoring with features
3. **Tests required**: All new code must have tests
4. **Documentation**: Update relevant docs
5. **Clean commits**: Clear commit messages, logical grouping

## Code Review Checklist

Before submitting, verify:

- [ ] No commented-out code (ghost code)
- [ ] No TODO/FIXME without issue numbers
- [ ] No conflicting feature flags or gated logic without abstraction
- [ ] Reusable code extracted into appropriate modules
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No secrets or credentials committed
- [ ] Code follows existing style conventions

## Anti-Patterns to Avoid

1. **God Objects**: Classes/modules that do too much
2. **Magic Numbers**: Unexplained constants in code
3. **Deep Nesting**: More than 3 levels of indentation
4. **Long Functions**: Keep functions under 50 lines
5. **Unclear Names**: Variables named `data`, `temp`, `x`, `foo`

## Getting Help

- Check existing documentation in `docs/`
- Review similar implementations in the codebase
- Ask questions in issues or pull request comments
- Follow the existing code style and patterns

---

**Remember**: Clean code is not about being perfect—it's about being clear, maintainable, and respectful to future developers (including yourself).
