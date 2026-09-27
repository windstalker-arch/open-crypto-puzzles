#!/usr/bin/env python3
"""Run the plane-window scan for the ALPHA channel only (real-module import)."""
import multiprocessing as mp, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import plane_window_scan as p  # noqa

A = p.A.flatten()


def run():
    configs = []
    for plane in range(8):
        configs.append((plane, 1, False))
    for bw in (2, 4, 8):
        configs.append((0, bw, False))
        configs.append((0, bw, True))
    for plane, bw, lsbf in configs:
        label = f"A p{plane} bw{bw} lsbf{int(lsbf)}"
        data = p.make_stream(A, plane, bw, lsbf)
        print(f"scan {label} stream={len(data)}B", flush=True)
        p.run_stream(data, label)
    print("ALPHA DONE", flush=True)


if __name__ == "__main__":
    mp.set_start_method("forkserver")
    run()
