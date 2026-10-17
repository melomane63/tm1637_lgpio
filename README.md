# tm1637_lgpio

Python driver for **TM1637** 7-segment LED display modules on the Raspberry Pi, using the [`lgpio`](http://abyz.me.uk/lg/py_lgpio.html) library.

It is a port of [`raspberrypi-tm1637`](https://github.com/depklyon/raspberrypi-tm1637) (itself a port of [`micropython-tm1637`](https://github.com/mcauser/micropython-tm1637)) from `RPi.GPIO` to `lgpio`, which works on all Raspberry Pi models, including the **Pi 5**, where `RPi.GPIO` does not.

## Features

- Same API as the original libraries (`write`, `show`, `number`, `numbers`, `hex`, `temperature`, `scroll`, `brightness`...)
- Up to **6 digits** per `write()` (4-digit and 6-digit modules)
- `TM1637Decimal` class for modules with a decimal point after each digit
- Selectable GPIO chip (`chip` parameter)
- Correct **ACK** handling (see [Changes](#changes))
- Single file, no dependency except `lgpio`

## Installation

Install `lgpio`:

```sh
# Raspberry Pi OS
sudo apt install python3-lgpio
# or, in a virtual environment
pip install lgpio
```

Then copy `tm1637_lgpio.py` next to your script. It is a plain module, not a pip package.

## Wiring

| Module | Raspberry Pi |
|--------|--------------|
| VCC    | 3.3 V (recommended) |
| GND    | GND |
| CLK    | any GPIO (e.g. GPIO 23) |
| DIO    | any GPIO (e.g. GPIO 24) |

Power the module from **3.3 V** when possible. Some modules have pull-ups on CLK/DIO tied to VCC: at 5 V, those lines would sit at 5 V, above the tolerance of the Pi's GPIO pins.

## Usage

```python
from tm1637_lgpio import TM1637

tm = TM1637(clk=23, dio=24)          # chip=0 and brightness=7 by default

tm.show("1234")                      # text (4 characters max)
tm.number(-12)                       # integer, -999 .. 9999
tm.numbers(12, 34)                   # "12:34" with the colon
tm.hex(0xBEEF)
tm.brightness(2)                     # 0 .. 7
tm.scroll("HELLO", delay=200)

tm.write(tm.encode_string("ABC 42")) # raw write, up to 6 segments
```

Decimal-point modules:

```python
from tm1637_lgpio import TM1637Decimal

tm = TM1637Decimal(clk=23, dio=24)
tm.show("12.34")
```

Segment encoding: bit 7 (`0x80`) of a segment turns on the decimal point (or the colon on the 2nd digit of colon modules):

```python
segs = tm.encode_string("ABC 42")
segs[2] |= 0x80                      # decimal point on the 3rd digit
tm.write(segs)
```

### Digit order on 6-digit modules

On some 6-digit modules the digits are not wired in display order. If your text appears scrambled, reorder the segments before writing. For example, for a module where digits 1/3 and 4/6 are swapped:

```python
def swap(segs):
    if len(segs) in (4, 5):
        segs.extend(bytearray([0] * (6 - len(segs))))
    segs[0], segs[2] = segs[2], segs[0]
    segs[3], segs[5] = segs[5], segs[3]
    return segs

tm.write(swap(tm.encode_string("ABC 42")))
```

## Raspberry Pi 5 and the GPIO chip

`TM1637(..., chip=0)` opens `/dev/gpiochip0`, which is correct for the Pi 1 to 4.

On the Pi 5, the 40-pin header is driven by the RP1 chip. On recent Raspberry Pi kernels it is exposed as `gpiochip0`; on older kernels it can be `gpiochip4`. Check on your system:

```sh
ls -l /dev/gpiochip*
cat /sys/class/gpio/gpiochip*/label     # look for "pinctrl-rp1"
```

If `pinctrl-rp1` is not `gpiochip0`, pass the right number:

```python
tm = TM1637(clk=23, dio=24, chip=4)
```

Reported working on the Pi 5 with kernel 6.6.67 (piCorePlayer 10.0.0) using `chip=0`. With kernel 6.1.77 (piCorePlayer 9.x) the header is not on `gpiochip0`.

## Performance

The protocol is bit-banged from Python. On a Raspberry Pi running Raspberry Pi OS, a 6-segment `write()` takes about **18 ms**. This is fine for volume or status displays, but the call blocks: in an `asyncio` program it blocks the event loop for that time. If that matters, run display updates in a dedicated thread and keep every access to the display (`write` and `brightness`) inside that thread, so that bus sequences never interleave.

## Changes

Compared with the original `lgpio` port:

- **ACK handling.** After each byte, the TM1637 pulls DIO low to acknowledge. Previously the Pi kept DIO at the last bit sent, so when bit 7 was 1 (command bytes `0xC0` and `0x88`-`0x8F`, and any segment with its decimal point on) the Pi drove DIO high while the chip drove it low. Now DIO is driven low right after the 8th clock edge, so both sides agree. DIO always stays an output.
- **`chip` parameter** to choose the GPIO chip (default `0`, so existing code is unaffected).

## Testing

`test_tm1637.py` exercises text, decimal points, brightness and a stress test of random updates, with a known checkpoint frame every 500 updates. The result is checked by eye:

```sh
python3 test_tm1637.py              # 3000 updates by default
python3 test_tm1637.py -n 10000
python3 test_tm1637.py --chip 4
```

Stop any other program using the same GPIO pins first.

## License

MIT. See the header of `tm1637_lgpio.py`.

- Copyright (c) 2016-2018 Mike Causer, [micropython-tm1637](https://github.com/mcauser/micropython-tm1637)
- Python 3 port: [depklyon/raspberrypi-tm1637](https://github.com/depklyon/raspberrypi-tm1637)
- Copyright (c) 2025 Domenico Guerra, port to `lgpio`

The copyright notices must be kept in all copies of the file.
