"""
"""

from machine import Pin, UART, ADC
import random

from volcasample2 import VolcaSample2, MIDI
from conductor import Conductor, EnvelopeA, SuperAHR
from conductordriver import ConductorDriver

def midi_uart_config():
    return UART(0, baudrate=31250, tx=Pin(12), rx=Pin(13))

def x():
    uart = midi_uart_config()
    midi = MIDI(uart)
    vs2 = VolcaSample2(midi)
    return Conductor(vs2, [x for x in range(0, 8)],
                     {MIDI.LEVEL: EnvelopeA(100, 64),
                      MIDI.SPEED: SuperAHR(0, 64, 40, 500, 1000, 500, "*", random.randint),
                      MIDI.START_POINT: SuperAHR(None, 0, 120, 1000, 0, 0, None, random.randint)},
                      lambda s, ct, rt, bs, ps: min(1000, max(40, (ps[0] + (random.randint(-(ps[1]), ps[1]))) * bs[1])))

def y(c):
    return ConductorDriver(c,
                           [Pin(x, machine.Pin.IN, machine.Pin.PULL_UP) for x in range(0, 4)],
                           [ADC(26), ADC(27), ADC(28)])

def main():
    uart = midi_uart_config()
    midi = MIDI(uart)
    vs2 = VolcaSample2(midi)
    cnd = Conductor(vs2, [x for x in range(0, 8)])
    pass

if __name__ == "__main__":
    main()
