# Code Quality Checklist

Use this checklist before committing code to ensure it meets RCL quality standards.

## Before Every Commit

### 1. Ghost Code Elimination
- [ ] No commented-out code blocks
- [ ] No unused imports or requires
- [ ] No dead code paths
- [ ] No temporary debug code
- [ ] Removed all `console.log()` used for debugging (unless intentional logging)

### 2. Clean Comments and Documentation
- [ ] Comments explain "why", not "what"
- [ ] No vague TODO/FIXME without issue numbers
- [ ] No placeholder comments like "// fix later"
- [ ] Updated relevant documentation
- [ ] JSDoc/docstrings for public APIs

### 3. Logic Separation
- [ ] No scattered feature flags
- [ ] Configuration centralized in `config/`
- [ ] Business logic separated from presentation
- [ ] Data access abstracted in repositories
- [ ] No hard-coded environment checks in business logic

### 4. Clean Extraction
- [ ] Duplicated code extracted into shared functions
- [ ] Functions are small and focused (< 50 lines ideally)
- [ ] Modules have single responsibility
- [ ] Clear, descriptive names for all functions/variables
- [ ] No "god objects" or overly complex classes

### 5. Testing
- [ ] Unit tests for new functionality
- [ ] Tests are isolated and independent
- [ ] Tests have clear, descriptive names
- [ ] Edge cases covered
- [ ] No test code in production files

### 6. Security
- [ ] No secrets or API keys in code
- [ ] Sensitive config in environment variables
- [ ] No SQL injection vulnerabilities
- [ ] Input validation present
- [ ] Error messages don't leak sensitive info

### 7. Style and Consistency
- [ ] Follows existing code style
- [ ] Consistent naming conventions
- [ ] Proper indentation
- [ ] No trailing whitespace
- [ ] Files end with newline

## Before Pull Request

### Code Review
- [ ] Self-reviewed all changes
- [ ] Verified changes are minimal and focused
- [ ] Checked for unintended file changes
- [ ] Ran linter (if available)
- [ ] Ran tests locally
- [ ] Built project successfully

### Documentation
- [ ] README updated if needed
- [ ] API docs updated
- [ ] Architecture docs reflect changes
- [ ] Added inline documentation for complex logic

### Git Hygiene
- [ ] Meaningful commit messages
- [ ] Logical commit grouping
- [ ] No merge commits in feature branch
- [ ] `.gitignore` updated for new file types

## Anti-Patterns Checklist

Ensure you're NOT doing any of these:

- [ ] ❌ Committing commented-out code "just in case"
- [ ] ❌ Adding TODOs without creating issues
- [ ] ❌ Copy-pasting code instead of extracting to shared function
- [ ] ❌ Hard-coding values that should be configurable
- [ ] ❌ Mixing multiple concerns in one function/module
- [ ] ❌ Creating deeply nested if/else chains (> 3 levels)
- [ ] ❌ Using unclear variable names (`data`, `temp`, `x`, etc.)
- [ ] ❌ Ignoring linter warnings without good reason
- [ ] ❌ Skipping tests because "it's just a small change"
- [ ] ❌ Committing WIP code to main branch

## Quick Reference

### Clean Code Example
```javascript
// ✅ Good: Clear, focused, well-named
export const calculateUserDiscount = (user, orderTotal) => {
  if (!user.isPremium) return 0;
  
  const baseDiscount = orderTotal * 0.1;
  const loyaltyBonus = user.yearsActive * 0.01 * orderTotal;
  
  return Math.min(baseDiscount + loyaltyBonus, orderTotal * 0.3);
};
```

### Messy Code Example (Don't Do This)
```javascript
// ❌ Bad: Unclear, mixed concerns, ghost code
export const calc = (u, t) => {
  // const oldCalc = t * 0.05; // old way
  // if (FEATURE_FLAG) {
    if (u.p) {
      let d = t * 0.1;
      // TODO fix this
      d = d + (u.y * 0.01 * t);
      return d > t * 0.3 ? t * 0.3 : d;
    }
  // }
  return 0;
};
```

---

**Remember:** Clean code today saves hours of debugging tomorrow!
