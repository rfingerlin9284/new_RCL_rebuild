# Source Code Directory

This directory contains the main source code for the RCL (Rick Clean Live) project.

## Structure Guidelines

- Keep code organized by feature or module
- Avoid mixing different concerns in the same file
- No embedded prompts or comments that don't serve documentation purposes
- Clear separation between:
  - Core functionality
  - Configuration logic
  - Data processing
  - UI/presentation layers

## Best Practices

1. **No Ghost Code**: Remove commented-out code blocks. Use version control instead.
2. **Clear Logic**: Avoid conflicting conditional logic or gated features without proper documentation.
3. **Single Responsibility**: Each file/module should have a clear, single purpose.
4. **Clean Extraction**: Extract reusable components into separate, well-named modules.
