from concurrent.futures import ThreadPoolExecutor
from prthinker.backends.base import ThreadLocalUsage, Usage


def test_usage_is_request_thread_scoped():
    state = ThreadLocalUsage()

    def worker(value):
        state.set(Usage(value, value + 1))
        return state.get()

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(worker, range(20)))
    assert results == [Usage(i, i + 1) for i in range(20)]
