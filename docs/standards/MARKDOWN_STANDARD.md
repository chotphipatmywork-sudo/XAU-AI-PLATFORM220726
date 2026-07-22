# XAU AI PLATFORM — MARKDOWN STANDARD

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the Markdown writing standard
for all documentation files inside the XAU AI PLATFORM project.

The objective is to ensure:

* Consistent document structure.
* Better readability.
* Markdownlint compatibility.
* Reliable documentation management.

---

## Document Structure Rules

All documents must follow this structure:

```text
Document Title

        |

        v

Metadata Section

        |

        v

Purpose

        |

        v

Main Sections

        |

        v

Review / Result Section

        |

        v

Document End
```

Every document should maintain a predictable structure
for:

* Human Review.
* AI Coding Assistant Processing.
* Documentation Governance.

---

## Heading Rules

Requirements:

* One H1 heading per document.
* H1 must contain document title.
* H2 defines major sections.
* H3 defines subsections.
* Do not skip heading levels.

Example:

```markdown
# Document Title

## Section

### Sub Section
```

---

## Blank Line Rules

Requirements:

* One blank line between sections.
* No multiple consecutive blank lines.
* No unnecessary spacing.

Invalid:

```markdown
Section


Next Section
```

Valid:

```markdown
Section

Next Section
```

---

## Table Formatting Rules

All Markdown tables must use spaces
around pipes.

Required:

```markdown
| Column A | Column B |
| --- | --- |
| Value | Value |
```

Not allowed:

```markdown
|Column A|Column B|
|---|---|
```

---

## Code Block Rules

Requirements:

* Always use fenced code blocks.
* Specify language when applicable.
* Do not use hard tabs.
* Use spaces for indentation.

Example:

```text
Example Content
```

---

## Tab Character Rules

Hard tab characters are not allowed.

Required:

* Use spaces only.
* Convert tabs before commit.

Reason:

* Prevent MD010 violations.
* Maintain consistent formatting.

---

## File Ending Rules

Every Markdown file must:

* End with a single newline character.
* Have no trailing spaces.

Purpose:

* Prevent MD047 violations.
* Maintain clean file structure.

---

## Naming Convention

Documentation files should follow
consistent naming rules.

Recommended formats:

```text
PascalCase_With_Underscore.md

PascalCase.md
```

Examples:

```text
Architecture_Principles.md

MODULE_INTERFACE_CATALOG.md

IMPLEMENTATION_CHECKLIST.md

PackageBlueprint.md
```

Rules:

* File name must describe responsibility clearly.
* Avoid ambiguous names.
* Avoid duplicate documentation purpose.

---

## Version Format

All documents must define:

```text
Version: x.y.z

Status: <state>

Architecture Baseline: ABR-x.x
```

Version information must appear
near the document header.

---

## Markdownlint Compatibility

All documentation files should pass:

```text
Markdownlint

0 Errors

0 Warnings
```

Required checks:

* Single H1.
* Unique headings.
* Correct spacing.
* Valid tables.
* No hard tabs.
* Correct file ending.

---

## Review Checklist

Before committing a document:

| Check Item                 | Status   |
| -------------------------- | -------- |
| One H1 heading             | Required |
| Heading hierarchy correct  | Required |
| Tables formatted correctly | Required |
| No hard tabs               | Required |
| No trailing spaces         | Required |
| Markdownlint passed        | Required |

---

## Related Documents

* Coding_Standard.md
* DOCUMENTATION_GOVERNANCE.md
* PROJECT_STRUCTURE.md
* REVIEW_CHECKLIST.md

---

## Document Status

Document:

`MARKDOWN_STANDARD.md`

Document Type:

Documentation Standard Document

Review Phase:

Phase 0.3 — Foundation Standards Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Document Status:

Approved Documentation Standard

---

End of MARKDOWN_STANDARD.md
