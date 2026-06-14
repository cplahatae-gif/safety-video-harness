from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor


RoleEvaluator = tuple[str, Callable[[], dict]]


def run_role_evaluators_parallel(evaluators: list[RoleEvaluator]) -> list[dict]:
    if not evaluators:
        return []
    with ThreadPoolExecutor(max_workers=len(evaluators)) as executor:
        futures = [executor.submit(fn) for _, fn in evaluators]
        reviews = [future.result() for future in futures]
    return [_with_parallel_metadata(name, review) for (name, _), review in zip(evaluators, reviews, strict=True)]


def _with_parallel_metadata(name: str, review: dict) -> dict:
    enriched = dict(review)
    enriched["role"] = str(enriched.get("role", name))
    enriched["execution_mode"] = "parallel_role_evaluator"
    return enriched
