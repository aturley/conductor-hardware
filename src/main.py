"""
"""

from machine import Pin, UART

from volcasample2 import VolcaSample2, MIDI
from conductor import Conductor

def midi_uart_config():
    return UART(0, baudrate=31250, tx=Pin(12), rx=Pin(13))

def conductor_builder():
    uart = midi_uart_config()
    midi = MIDI(uart)
    vs2 = VolcaSample2(midi)
    return Conductor(vs2, [x for x in range(0, 8)])

def main():
    uart = midi_uart_config()
    midi = MIDI(uart)
    vs2 = VolcaSample2(midi)
    cnd = Conductor(vs2, [x for x in range(0, 8)])
    pass

if __name__ == "__main__":
    main()
