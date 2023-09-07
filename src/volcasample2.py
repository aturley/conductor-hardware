class MIDI:
    SAMPLE_NO_MSB = 3
    SAMPLE_NO_LSB = 35
    LEVEL = 7
    PAN = 10
    START_POINT = 40
    LENGTH = 41
    HI_CUT = 42
    SPEED = 43
    CHROMATIC_SPEED = 49
    PITCH_EG_INTENSITY = 44
    PITCH_EG_ATTACK = 45
    PITCH_EG_DECAY = 46
    AMP_EG_ATTACK = 47
    AMP_EG_DECAY = 48
    TRIGGER_DELAY = 50
    LOOP = 68
    REVERB = 70
    REVERSE = 75
    REVERB_MIX = 91

    def __init__(self, uart):
        self.uart = uart

    def set_param(self, voices, param, value):
        for v in voices:
            _ = self.uart.write(bytes([0xB0 + v, param, value]))

    def note_on(self, voices):
        for v in voices:
            _ = self.uart.write(bytes([0x90 + v, 0x01, 0x01]))

class VolcaSample2:
    def __init__(self, midi):
        self.midi = midi

    def trigger(self, voices):
        self.midi.note_on(voices)

    def set_sample(self, voices, sample):
        sample_msb = sample // 100
        sample_lsb = sample % 100
        self.midi.set_param(voices, self.midi.SAMPLE_NO_MSB, sample_msb)
        self.midi.set_param(voices, self.midi.SAMPLE_NO_LSB, sample_lsb)

    def set_param(self, voices, param, value):
        self.midi.set_param(voices, param, value)

    
        
    
