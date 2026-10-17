#!/usr/bin/env python3
"""Test of tm1637_lgpio (ACK fix, option A).

Run it from the folder containing tm1637_lgpio.py, with the lybrica service
stopped (two processes cannot claim the same GPIO):

    python3 test_tm1637.py              # default: 3000 stress updates
    python3 test_tm1637.py -n 10000     # longer stress test
    python3 test_tm1637.py --chip 4     # other GPIO chip
"""
import argparse
import random
import time

from tm1637_lgpio import TM1637

CLK, DIO = 23, 24            # same pins as lybrica.py
ALPHABET = "0123456789ABCDEFGHIJLNOPRSTUY -"


def swap(segs):
    """Same reordering as lybrica.py (physical wiring of the display)."""
    length = len(segs)
    if length in (4, 5):
        segs.extend(bytearray([0] * (6 - length)))
    segs[0], segs[2] = segs[2], segs[0]
    if length >= 4:
        segs[3], segs[5] = segs[5], segs[3]
    return segs


def show(tm, text, dots=()):
    segs = tm.encode_string(text)
    for i in dots:
        segs[i] |= 0x80
    tm.write(swap(segs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=3000, help="stress test updates")
    ap.add_argument("--chip", type=int, default=0, help="GPIO chip number")
    args = ap.parse_args()

    tm = TM1637(clk=CLK, dio=DIO, chip=args.chip)

    try:
        print("1/5 Text: expect 'HELLO ' then '123456'")
        show(tm, "HELLO ")
        time.sleep(1.5)
        show(tm, "123456")
        time.sleep(1.5)

        print("2/5 Decimal points (bit 7 = 1, the case that used to conflict with the ACK)")
        show(tm, "888888", dots=range(6))
        time.sleep(2)
        for i in range(6):
            show(tm, "000000", dots=(i,))
            time.sleep(0.3)

        print("3/5 Brightness sweep 0..7")
        show(tm, "888888")
        for b in list(range(8)) + list(range(6, -1, -1)):
            tm.brightness(b)
            time.sleep(0.15)
        tm.brightness(7)

        print(f"4/5 Stress test: {args.n} random updates (watch for wrong or flickering segments)")
        checkpoint = "AbC 42"
        t0 = time.perf_counter()
        for k in range(1, args.n + 1):
            text = "".join(random.choice(ALPHABET) for _ in range(6))
            dots = [i for i in range(6) if random.random() < 0.3]
            show(tm, text, dots)
            if k % 500 == 0:
                # Known frame: it must be displayed exactly as written, every time
                show(tm, checkpoint, dots=(2, 3))
                print(f"   {k}/{args.n}: checkpoint frame 'ABC 42' with dots on chars 3 and 4")
                time.sleep(1.5)
        dt = time.perf_counter() - t0
        print(f"   average time per update: {dt / args.n * 1000:.1f} ms")

        print("5/5 Final frame (like lybrica): 'ABC 42', dots on chars 3 and 4")
        show(tm, checkpoint, dots=(2, 3))
        time.sleep(3)
        print("Done. If every checkpoint frame was correct, the module is OK.")
    finally:
        show(tm, "      ")


if __name__ == "__main__":
    main()
