#!/usr/bin/env python3
"""Run the plane-window scan for the ALPHA channel only (sailboat anti-alias edge).

The alpha channel has continuous pencil-sketch values; we scan every 8-bit plane and
2/4/8-bit windows exactly as done for grayscale.
"""
import importlib.util, multiprocessing as mp, os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("p", os.path.join(HERE, "plane_window_scan.py"))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

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
