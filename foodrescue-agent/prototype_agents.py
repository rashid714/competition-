import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional

from observability import incr, timing, gauge

logger = logging.getLogger(__name__)


class SummarizerAgent:
    """Summarizes donations for a session."""
    def __init__(self, memory):
        self.memory = memory

    def run(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        start = time.time()
        donations = self.memory.get_donations(session_id)
        total = sum(d.get('weight', 0) for d in donations)
        stores = sorted({d.get('store', 'unknown') for d in donations})
        summary = {
            'donation_count': len(donations),
            'total_weight': float(total),
            'stores': stores
        }
        elapsed = time.time() - start
        logger.info(f"SummarizerAgent completed in {elapsed:.3f}s")
        return {'summary': summary, 'duration': elapsed}


class AllocatorAgent:
    """Allocates donations to recipient organizations (simple heuristic)."""
    def __init__(self, memory):
        self.memory = memory

    def run(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        start = time.time()
        donations = self.memory.get_donations(session_id)
        # very small heuristic: group by store and produce allocation percentages
        totals = {}
        for d in donations:
            store = d.get('store', 'unknown')
            totals[store] = totals.get(store, 0) + float(d.get('weight', 0))

        total_weight = sum(totals.values()) or 1.0
        allocations = {s: round(w / total_weight, 2) for s, w in totals.items()}
        elapsed = time.time() - start
        logger.info(f"AllocatorAgent completed in {elapsed:.3f}s")
        incr('agent.allocator.runs')
        timing('agent.allocator.duration', elapsed)
        return {'allocations': allocations, 'duration': elapsed}


class ReporterAgent:
    """Generates a human-friendly impact report (uses memory.generate_impact_report)."""
    def __init__(self, memory):
        self.memory = memory

    def run(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        start = time.time()
        try:
            report = self.memory.generate_impact_report(session_id)
        except Exception as e:
            logger.error(f"ReporterAgent failed: {e}")
            report = f"Report generation failed: {str(e)}"
        elapsed = time.time() - start
        logger.info(f"ReporterAgent completed in {elapsed:.3f}s")
        incr('agent.reporter.runs')
        timing('agent.reporter.duration', elapsed)
        return {'report': report, 'duration': elapsed}


class GeminiReporterAgent:
    """Attempts to generate an impact report using Gemini (if configured)."""
    def __init__(self, memory):
        self.memory = memory

    def run(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        start = time.time()
        used = False
        try:
            cfg = getattr(self.memory, 'config', None)
            if cfg and hasattr(cfg, 'ensure_model') and cfg.ensure_model():
                # call the existing generate_impact_report path which will use Gemini
                metrics = self.memory.get_metrics(session_id)
                report = cfg.generate_impact_report(metrics['total_weight'], metrics['total_meals'], metrics['store_count'])
                used = cfg.gemini_ready
            else:
                report = "Gemini not configured; fallback report used"
        except Exception as e:
            logger.error(f"GeminiReporterAgent error: {e}")
            report = f"GeminiReporterAgent failed: {str(e)}"

        elapsed = time.time() - start
        incr('agent.gemini_reporter.runs')
        timing('agent.gemini_reporter.duration', elapsed)
        gauge('agent.gemini_reporter.used', 1.0 if used else 0.0)
        logger.info(f"GeminiReporterAgent completed in {elapsed:.3f}s (used={used})")
        return {'report': report, 'duration': elapsed, 'gemini_used': used}


def run_parallel_agents(memory, session_id: Optional[str] = None, timeout: float = 5.0) -> Dict[str, Any]:
    """Run a small set of agents in parallel and return merged results and simple observability metrics.

    This function uses CPU-threading to simulate parallel agents and records simple metrics.
    """
    agents = [SummarizerAgent(memory), AllocatorAgent(memory), ReporterAgent(memory), GeminiReporterAgent(memory)]
    results = {}
    metrics = {'agents_run': 0, 'successes': 0, 'failures': 0, 'durations': {}}

    with ThreadPoolExecutor(max_workers=4) as ex:
        future_to_name = {ex.submit(agent.run, session_id): agent.__class__.__name__ for agent in agents}
        for fut in as_completed(future_to_name, timeout=timeout):
            name = future_to_name.get(fut, 'unknown')
            metrics['agents_run'] += 1
            try:
                res = fut.result(timeout=0)
                # merge results
                results.update(res)
                metrics['successes'] += 1
                # store duration if present
                if 'duration' in res:
                    metrics['durations'][name] = float(res['duration'])
            except Exception as e:
                metrics['failures'] += 1
                logger.error(f"Agent {name} failed: {e}")

    return {'success': True, 'session_id': session_id, 'results': results, 'metrics': metrics}
