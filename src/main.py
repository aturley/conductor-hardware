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
                     {MIDI.LEVEL: SuperAHR(0, 60, 50, 200, 1000, 200, None, random.randint),
                      MIDI.PITCH_EG_INTENSITY: SuperAHR(1, 63, 5, 500, 2000, 5000, "*", random.randint),
                      MIDI.SPEED: lambda s, ct, rt, bs, ps: min(127, ps[1] >> 3),
                      MIDI.AMP_EG_ATTACK: lambda s, ct, rt, bs, ps: min(127, ps[2] >> 5),
                      MIDI.AMP_EG_DECAY: lambda s, ct, rt, bs, ps: min(127, ps[2] >> 5),
                      MIDI.PAN: SuperAHR(1, 63, 50, 2800, 100, 100, "*", random.randint),
                      MIDI.START_POINT: lambda s, ct, rt, bs, ps: min(127, ps[0] >> 3)},
                      SuperAHR(1, 20, 40, 1000, 2000, 1000, "+", random.randint))

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
