from volcasample2 import MIDI

PARAM_DEFAULTS = {
    MIDI.LEVEL: 0,
    MIDI.PAN: 0,
    MIDI.START_POINT: 0,
    MIDI.LENGTH: 127,
    MIDI.HI_CUT: 127,
    MIDI.SPEED: 0,
    MIDI.PITCH_EG_INTENSITY: 63,
    MIDI.PITCH_EG_ATTACK: 0,
    MIDI.PITCH_EG_DECAY: 127,
    MIDI.AMP_EG_ATTACK: 0,
    MIDI.AMP_EG_DECAY: 0,
    MIDI.TRIGGER_DELAY: 0,
    MIDI.LOOP: 0,
    MIDI.REVERB: 0,
    MIDI.REVERSE: 0,
    MIDI.REVERB_MIX: 0
    }

class Conductor:
    def __init__(self, vs2, voices, param_gens, timing_fn=lambda s, rt, bs, ps: 100, param_base=PARAM_DEFAULTS):
        self.vs2 = vs2
        self.voices = voices
        self.next_voice_idx = 0
        self.step = 0
        self.param_gens = param_gens.copy()
        self.param_base = param_base.copy()
        self.recent_triggers = []
        self.button_states = [0, 0, 0, 0, 0]
        self.pot_states = [0, 0, 0]
        self.timing_fn = timing_fn

    def initialize(self):
        for p, v in self.param_base.items():
            self.vs2.set_param(self.voices, p, v)

    def clear_triggers(self):
        self.recent_triggers = []

    def add_trigger(self, trigger):
        self.recent_triggers.append(trigger)

    def set_pot_states(self, pot_states):
        self.pot_states = pot_states[:]

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

    def generate_timing(self, cur_time):
        return self.timing_fn(self.step,
                              cur_time,
                              self.recent_triggers,
                              self.button_states,
                              self.pot_states)

    def generate_params(self, cur_time):
        return [[p, self.param_base[p] +
                 v(self.step,
                   cur_time,
                   self.recent_triggers,
                   self.button_states,
                   self.pot_states)] for p, v in self.param_gens.items()]

    def grain(self, cur_time):
        self.play_next_with_param_values(self.generate_params(cur_time))
        self.clear_triggers()
        self.next_step()


class EnvelopeA:
    def __init__(self, attack_steps, max_value):
        self.attack_steps = attack_steps
        self.max_value = max_value
        self.steps_left = 0
        self.current_value = 0

    def __call__(self, steps, current_time, recent_triggers, button_states, pot_states):
        for rt in recent_triggers:
            if rt[0] == 1:
                self.steps_left = self.attack_steps
                self.current_value = 0

        if self.steps_left > 0:
            self.current_value = ((self.attack_steps - self.steps_left) * self.max_value) // self.attack_steps
            self.steps_left = self.steps_left - 1

        return self.current_value

     
class SuperAHR:
    """
    Super Attack, Hold, Release envelope.

    * trigger input (button number or None for retrigger)
    * bias
    * peak offset (peak - bias)
    * attack (ms)
    * hold (ms)
    * release (ms, NONE)
    * random (NONE, "+", "*")

    -  -  -  -  -   **peak**
    |             **|      |**
    peak_offset **  |      |  **
    |         **    |      |    **
    -*********      |      |      *****
    |        |  A   |   H  |   D  |
    bias     |
    |        |
    0--------|-----------------------
        trig>|

    """

    def __init__(self,
                 trigger_input,
                 bias,
                 peak_offset,
                 attack,
                 hold,
                 release,
                 rnd,
                 randint_fn):
        self.trigger_input = trigger_input
        self.bias = bias
        self.peak_offset = peak_offset
        self.attack = attack
        self.hold = hold
        self.next_hold = 0
        self.release = release
        if self.release == None:
            self.next_release = None
        else:
            self.next_release = 0
        self.next_end = 0
        self.rnd = rnd
        self.trigger_time = 0
        self.randint_fn = randint_fn

    def map_value(self, input_start, input_end, output_start, output_end, v_in):
        return (((v_in - input_start) / (input_end - input_start)) * (output_end - output_start)) + output_start

    def __call__(self, steps, cur_time, recent_triggers, button_states, pot_states):
        cur_offset = 0

        input_triggered = False

        if self.trigger_input is not None:
            for rt in recent_triggers:
                if rt[0] == self.trigger_input and rt[1] == 1:
                    input_triggered = True
                    break

        if (self.trigger_input is None) and (cur_time >= self.next_end):
            if self.next_end == 0:
                self.trigger_time = cur_time
            else:
                self.trigger_time = self.next_end
            did_trigger = True
        elif input_triggered:
            self.trigger_time = cur_time
            did_trigger = True
        else:
            did_trigger = False

        if did_trigger:
            self.next_hold = self.trigger_time + self.attack

            if self.release is not None:
                self.next_release = self.next_hold + self.hold
                self.next_end = self.next_release + self.release
            else:
                self.next_release = None
                self.next_end = self.next_hold + self.hold

        if (cur_time >= self.next_end):
            if self.release is None:
                cur_offset = self.peak_offset
            else:
                cur_offset = 0
        elif (self.next_release is not None) and (cur_time >= self.next_release):
            cur_offset = int(self.map_value(self.next_release, self.next_end, self.peak_offset, 0, cur_time))
        elif (cur_time >= self.next_hold):
            cur_offset = self.peak_offset
        elif (cur_time >= self.trigger_time):
            cur_offset = int(self.map_value(self.trigger_time, self.next_hold, 0, self.peak_offset, cur_time))

        if self.rnd == "+":
            cur_offset = self.randint_fn(min(cur_offset, 0), max(cur_offset, 0))
        elif self.rnd == "*":
            cur_offset = self.randint_fn(min(-cur_offset, cur_offset), max(-cur_offset, cur_offset))

        return cur_offset + self.bias
