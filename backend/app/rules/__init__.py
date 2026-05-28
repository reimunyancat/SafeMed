"""Rule-based interaction detection (Module 1)."""
from app.rules.dur import RuleFinding, Severity
from app.rules.engine import run_rules

__all__ = ["RuleFinding", "Severity", "run_rules"]
