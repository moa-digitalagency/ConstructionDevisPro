## 2024-10-26 - Interaction Models
**Learning:** Hover-based dropdowns exclude keyboard and touch users.
**Action:** Always implement dropdowns with click handlers and proper ARIA state (`aria-expanded`) to ensure universal access. Remove `tabindex="-1"` from menu items if arrow-key navigation is not implemented.
