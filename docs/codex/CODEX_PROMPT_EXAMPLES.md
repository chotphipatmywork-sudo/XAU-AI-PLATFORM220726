# XAU AI PLATFORM

## CODEX PROMPT EXAMPLES

Version : 1.0.0

---

## Purpose

This document contains standard prompt templates for working with Codex.

Always combine these prompts with:

- CODEX_RULES.md
- CODEX_TASK_TEMPLATE.md

---

## 1. Implement Module

Implement the assigned module.

Requirements:

- Follow CodingStandard.md
- Follow ProjectStructure.md
- Preserve architecture
- Do not modify unrelated files
- Keep backward compatibility
- No placeholder implementation
- Return modified files only

---

## 2. Bug Fix

Fix the reported bug.

Requirements:

- Minimize code changes
- Preserve existing behavior
- Do not redesign architecture
- Explain root cause
- Verify compile status

---

## 3. Refactor

Refactor the assigned files.

Requirements:

- Improve readability
- Reduce duplication
- Preserve behavior
- No public API changes
- Keep architecture unchanged

---

## 4. Performance Optimization

Optimize performance.

Requirements:

- Do not change functionality
- Explain optimization
- Avoid premature optimization
- Preserve readability

---

## 5. Documentation

Generate or update documentation.

Requirements:

- Keep documentation consistent
- Follow project terminology
- Do not invent features
- Match implementation

---

## 6. Unit Test

Create or update unit tests.

Requirements:

- Cover success cases
- Cover failure cases
- Cover edge cases
- Keep tests isolated

---

## 7. Compile Review

Review the project before compilation.

Verify:

- Include paths
- Missing dependencies
- Duplicate classes
- Syntax errors
- Compile warnings

Return a complete report.

---

## 8. Code Review

Review the assigned code.

Evaluate:

- Architecture
- SOLID
- Naming
- Readability
- Maintainability
- Performance
- Potential bugs
- Security concerns

Provide improvement suggestions only.
Do not modify code unless requested.

---

## 9. Generate New Module

Generate a new module.

Requirements:

- Follow project architecture
- One class per file
- Header comment required
- Include guard required
- Follow naming convention
- No placeholder methods

---

## 10. Safe Edit

Modify only the specified files.

Requirements:

- Do not touch unrelated files
- Preserve public interfaces
- Keep behavior unchanged
- Explain every modification

---

End of Document
