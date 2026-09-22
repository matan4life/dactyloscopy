"""The shared process pool, held to the one thing it guarantees: results come
back in task order, from the pool and from the sequential path alike.

Every instrument that uses `pool.run` folds results in task order and says
in its own docstring why its tasks are pure; what none of them can check is
that the pool keeps the order when tasks finish out of it. The tasks below
finish in reverse - the first sleeps longest - so an ordered result is a
result the pool ordered.
"""

import os
import time

import pytest

from implementation.library import pool

SERIAL = "TEST_POOL_SERIAL"


def slow_square(task):
    i, n = task
    time.sleep(0.02 * (n - i))
    return (i, i * i, os.getpid())


def test_cpus_is_at_least_one_and_at_most_the_machine():
    n = pool.cpus()
    assert 1 <= n <= (os.cpu_count() or 1)


def test_results_come_back_in_task_order_from_the_pool():
    if pool.cpus() < 2:
        pytest.skip("one worker: the pool is never started")
    os.environ.pop(SERIAL, None)
    tasks = [(i, 8) for i in range(8)]
    out = list(pool.run(tasks, slow_square, SERIAL))
    assert [(i, sq) for i, sq, _ in out] == [(i, i * i) for i in range(8)]
    assert len({pid for _, _, pid in out}) > 1, "no task left this process"


def test_serial_variable_runs_every_task_in_this_process():
    os.environ[SERIAL] = "1"
    try:
        tasks = [(i, 8) for i in range(8)]
        out = list(pool.run(tasks, slow_square, SERIAL))
    finally:
        del os.environ[SERIAL]
    assert [(i, sq) for i, sq, _ in out] == [(i, i * i) for i in range(8)]
    assert {pid for _, _, pid in out} == {os.getpid()}


def test_scratch_is_one_directory_per_process(tmp_path):
    d = pool.scratch(str(tmp_path))
    assert os.path.isdir(d)
    assert os.path.basename(d) == str(os.getpid())
    assert pool.scratch(str(tmp_path)) == d
