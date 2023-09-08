from machine import Pin, Timer

class ConductorDriver:
    def __init__(self, conductor, event_pins, pot_adcs):
        self.grain_timer = None
        self.pot_timer = None
        self.conductor = conductor

        self.pot_adcs = pot_adcs[:]

        eps = event_pins[:]

        for ep in event_pins:
            ep.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: self.conductor.add_trigger([eps.index(p), 1]))

    def start(self, interval):
        if self.grain_timer:
            self.grain_timer.deinit()
            self.grain_timer.init(period=interval, mode=Timer.PERIODIC, callback=lambda t: self.conductor.grain())
        else:
            self.grain_timer = Timer(period=interval, mode=Timer.PERIODIC, callback=lambda t: self.conductor.grain())

        if self.pot_timer:
            self.pot_timer.deinit()
            self.pot_timer.init(period=31, mode=Timer.PERIODIC, callback=lambda t: self.conductor.set_pot_states([adc.read_u16() >> 6 for adc in self.pot_adcs]))
        else:
            self.pot_timer = Timer(period=31, mode=Timer.PERIODIC, callback=lambda t: self.conductor.set_pot_states([adc.read_u16() >> 6 for adc in self.pot_adcs]))

    def stop(self):
        self.grain_timer.deinit()
        self.pot_timer.deinit()
