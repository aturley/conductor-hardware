from machine import Timer

class ConductorDriver:
    def __init__(self, conductor):
        self.tim = None
        self.conductor = conductor

    def start(self, interval):
        if self.tim:
            self.tim.deinit()
            self.tim.init(period=interval, mode=Timer.PERIODIC, callback=lambda t: self.conductor.grain())
        else:
            self.tim = Timer(period=interval, mode=Timer.PERIODIC, callback=lambda t: self.conductor.grain())

    def stop(self):
        self.tim.deinit()
