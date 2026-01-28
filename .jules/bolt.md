## 2026-01-28 - Anti-pattern: Dynamic loading for small collections
**Learning:** The codebase heavily used `lazy='dynamic'` for relationships like `project.plans` (which are typically small collections), leading to N+1 queries because templates were calling `.count()` before iterating.
**Action:** Default to standard lazy loading (`lazy=True` or default) for small collections and check for emptiness using list truthiness (`{% if project.plans %}`) instead of `.count()`.
