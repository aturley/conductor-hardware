from machine import Pin, Timer

class ConductorDriver:
    def __init__(self, conductor, event_pins):
        self.tim = None
        self.conductor = conductor

        eps = event_pins[:]

        for ep in event_pins:
            ep.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: self.conductor.add_trigger([eps.index(p), 1]))

    def start(self, interval):
        if self.tim:
            self.tim.deinit()
            self.tim.init(period=interval, mode=Timer.PERIODIC, callback=lambda t: self.conductor.grain())
        else:
            self.tim = Timer(period=interval, mode=Timer.PERIODIC, callback=lambda t: self.conductor.grain())

    def stop(self):
        self.tim.deinit()
