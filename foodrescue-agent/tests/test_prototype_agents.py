import os
import tempfile
from memory import Memory
from prototype_agents import run_parallel_agents


def test_run_parallel_agents_creates_expected_keys(tmp_path):
    # Use a temporary data dir to avoid polluting workspace
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        os.makedirs('session_data', exist_ok=True)
        mem = Memory()
        # create a few donations
        sid = 'testsession'
        mem.save_donation('StoreA', 'Apples', 5.0, 'LocA', sid)
        mem.save_donation('StoreB', 'Bread', 3.2, 'LocA', sid)
        res = run_parallel_agents(mem, sid)
        assert res['success'] is True
        assert 'results' in res
        assert 'metrics' in res
        # results should include a summary and a report or allocations
        assert 'summary' in res['results'] or 'report' in res['results'] or 'allocations' in res['results']
    finally:
        os.chdir(cwd)
