"""A process pool that moves no number, and the scratch directory that lets
a subprocess-driven instrument run inside it.

Three instruments carried their own copy of this, and the copies had
diverged: `noise_floor` sized its pool by `os.cpu_count()`, which reports
the machine and not the share of it a container was given, and collected
every result in a list before folding; `matching` read the affinity mask
but not the cgroup quota; `warp_families` read both and yielded results as
they arrived. This is the last of the three, once, for all of them.

The argument that a pool moves no number is the caller's to make, and every
caller makes it in its own docstring: the work each task does is a pure
function of its input and the frozen binaries, every draw from a random
generator is made in the parent in the order a sequential run makes it, and
results are delivered in task order and merged in task order. What this
module guarantees is the last of those - `pool.imap` delivers in order - and
the escape hatch: with the caller's serial variable set in the environment,
the same tasks run in the parent, one after another, and return the same
bytes, which is the check each caller's record performs.
"""
import multiprocessing
import os


def scratch(work):
    """A directory under `work` that this process owns, named by its pid.

    Tools that write their outputs by fixed names - `mindtct` writes
    `<root>.xyt`, `<root>.min` and six more beside it - cannot share one
    directory between two processes: the second write lands between the
    first's write and read. One directory per process keeps fixed names
    safe, and the caller deletes what it wrote when it is done."""
    d = os.path.join(work, str(os.getpid()))
    os.makedirs(d, exist_ok=True)
    return d


def cpus():
    """How many workers this process may actually run at once.

    `os.cpu_count()` reports the machine, not the share of it a container was
    given, and a pool sized to the machine inside a quota of four cores
    thrashes. The affinity mask catches cpuset and taskset; the cgroup v2 and
    v1 quota files catch `--cpus`. None of this reaches a number - the output
    does not depend on the worker count - so a bad reading costs speed and
    nothing else."""
    try:
        n = len(os.sched_getaffinity(0))
    except AttributeError:
        n = os.cpu_count() or 1
    for path, sep in (("/sys/fs/cgroup/cpu.max", " "),
                      ("/sys/fs/cgroup/cpu/cpu.cfs_quota_us", None)):
        try:
            with open(path) as fp:
                text = fp.read().split()
        except OSError:
            continue
        try:
            if sep is None:
                quota = int(text[0])
                with open("/sys/fs/cgroup/cpu/cpu.cfs_period_us") as fp:
                    period = int(fp.read())
            else:
                if text[0] == "max":
                    continue
                quota, period = int(text[0]), int(text[1])
        except (OSError, ValueError, IndexError):
            continue
        if quota > 0 and period > 0:
            n = min(n, max(1, quota // period))
        break
    return max(1, n)


def run(tasks, fn, serial_var):
    """Yield `fn(task)` for each task, in order, from a fork pool when one is
    worth starting and in this process otherwise.

    `serial_var` names the environment variable that forces the sequential
    path; each instrument has its own, named in its record, so that a reader
    reproducing that record can force it without touching another's.

    Results are yielded as they arrive rather than collected, so the caller
    folds each into its accumulators and the parent never holds more than a
    chunk of them. The chunk is a quarter of a worker's even share, capped
    at thirty-two: the cap binds only once there are more than 128 tasks per
    worker, and above it the tail of a long run is a chunk and not hundreds
    of tasks one worker finishes alone."""
    n = cpus()
    if n < 2 or len(tasks) < 2 or os.environ.get(serial_var):
        for t in tasks:
            yield fn(t)
        return
    ctx = multiprocessing.get_context("fork")
    chunk = max(1, min(len(tasks) // (n * 4), 32))
    with ctx.Pool(n) as workers:
        for out in workers.imap(fn, tasks, chunksize=chunk):
            yield out
