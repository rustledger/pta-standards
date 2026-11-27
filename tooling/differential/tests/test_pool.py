import os
import signal
import time

from ptadiff.pool import Crash, run_forked


def _fn(payload):
    if payload == "segv":
        os.kill(os.getpid(), signal.SIGSEGV)
    if payload == "raise":
        raise ValueError("nope")
    if payload == "exit":
        os._exit(7)
    if payload == "hang":
        time.sleep(30)
    return payload.upper()


def test_run_forked_results_independent_of_jobs():
    items = [(str(i), f"x{i}") for i in range(40)]
    one = run_forked(items, _fn, jobs=1)
    many = run_forked(items, _fn, jobs=7)
    assert one == many == {str(i): f"X{i}" for i in range(40)}


def test_run_forked_crash_loses_only_that_input():
    items = [("a", "a"), ("b", "segv"), ("c", "c"), ("d", "raise"), ("e", "exit"), ("f", "f")]
    got = run_forked(items, _fn, jobs=1)
    assert got["a"] == "A" and got["c"] == "C" and got["f"] == "F"
    assert got["b"] == Crash("killed by SIGSEGV")
    assert got["d"] == Crash("raised ValueError: nope")
    assert got["e"] == Crash("exited 7")


def test_run_forked_timeout_is_a_crash():
    got = run_forked([("h", "hang"), ("z", "z")], _fn, jobs=1, timeout=1)
    assert got == {"h": Crash("killed by SIGALRM"), "z": "Z"}


def test_run_forked_empty():
    assert run_forked([], _fn, jobs=4) == {}
