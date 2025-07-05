# tm1637_lgpio

TM1637 7-segment LED display driver using the `lgpio` library on Raspberry Pi.

## Installation

```bash
pip3 install git+https://github.com/melomane63/tm1637_lgpio.git
```

## Example

```python
from tm1637_lgpio import TM1637
from time import sleep

display = TM1637(clk=17, dio=27)
display.show("1234")
sleep(2)
display.number(42)
```

## License

MIT © 2025 Domenico Guerra
