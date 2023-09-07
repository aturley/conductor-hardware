from volcasample2 import MIDI

PARAM_DEFAULTS = {
    MIDI.LEVEL: 127,
    MIDI.PAN: 63,
    MIDI.START_POINT: 0,
    MIDI.LENGTH: 127,
    MIDI.HI_CUT: 127,
    MIDI.SPEED: 63,
    MIDI.PITCH_EG_INTENSITY: 63,
    MIDI.PITCH_EG_ATTACK: 0,
    MIDI.PITCH_EG_DECAY: 0,
    MIDI.AMP_EG_ATTACK: 0,
    MIDI.AMP_EG_DECAY: 127,
    MIDI.TRIGGER_DELAY: 0,
    MIDI.LOOP: 0,
    MIDI.REVERB: 0,
    MIDI.REVERSE: 0,
    MIDI.REVERB_MIX: 0
    }

class Conductor:
    def __init__(self, vs2, voices, param_gens, param_base=PARAM_DEFAULTS):
        self.vs2 = vs2
        self.voices = voices
        self.next_voice_idx = 0
        self.step = 0
        self.param_gens = param_gens.copy()
        self.param_base = param_base.copy()

    def initialize(self):
        for p, v in self.param_base.items():
            self.vs2.set_param(self.voices, p, v)

    def set_param_gens(self, param_gens):
        self.param_gens = param_gens[:]

    def set_sample(self, sample):
        self.vs2.set_sample(self.voices, sample)

    def play_next_with_param_values(self, param_values):
        voice = self.voices[self.next_voice_idx]
        for pv in param_values:
            self.vs2.set_param([voice], pv[0], pv[1])
        self.vs2.trigger([voice])

        self.next_voice_idx = self.next_voice_idx + 1

        if self.next_voice_idx == len(self.voices):
            self.next_voice_idx = 0

    def next_step(self):
        self.step = self.step + 1

    def generate_params(self):
        return [[p, self.param_base[p] + v(self.step)] for p, v in self.param_gens.items()]

    def grain(self):
        self.play_next_with_param_values(self.generate_params())
        self.next_step()
