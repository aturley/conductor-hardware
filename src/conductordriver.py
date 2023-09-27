from machine import Pin, Timer
import time

class ConductorDriver:
    def __init__(self, conductor, event_pins, pot_adcs):
        self.grain_timer = None
        self.pot_timer = None
        self.conductor = conductor

        self.event_pins = event_pins[:]
        self.pot_adcs = pot_adcs[:]

        for ep in self.event_pins:
            ep.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: self.conductor.add_trigger([self.event_pins.index(p), 1]))

    def play_grain(self, t):
        self.conductor.button_states = [int(not ep.value()) for ep in self.event_pins]
        t.init(period=self.conductor.generate_timing(time.ticks_ms()), mode=Timer.ONE_SHOT, callback=self.play_grain)
        self.conductor.grain(time.ticks_ms())

    def start(self):
        if self.grain_timer:
            self.grain_timer.deinit()
            self.grain_timer.init(period=0, mode=Timer.ONE_SHOT, callback=self.play_grain)
        else:
            self.grain_timer = Timer(period=0, mode=Timer.ONE_SHOT, callback=self.play_grain)

        if self.pot_timer:
            self.pot_timer.deinit()
            self.pot_timer.init(period=31, mode=Timer.PERIODIC, callback=lambda t: self.conductor.set_pot_states([adc.read_u16() >> 6 for adc in self.pot_adcs]))
        else:
            self.pot_timer = Timer(period=31, mode=Timer.PERIODIC, callback=lambda t: self.conductor.set_pot_states([adc.read_u16() >> 6 for adc in self.pot_adcs]))

    def stop(self):
        self.grain_timer.deinit()
        self.pot_timer.deinit()
