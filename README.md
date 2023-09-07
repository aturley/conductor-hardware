# Conductor

## Overview

Conductor is a hardware device that uses the [Korg Volca Sample
2(https://www.korg.com/us/products/dj/volca_sample2/) as a granular
synthesizer. It treats the sample playback engine as a grain
generator, allowing bulk control over sample parameters and automating
control of individual sample playback.

Conductor uses MIDI to control Volca Sample 2; the [MIDI
implementation is documented on Korg's
website](https://cdn.korg.com/us/support/download/files/c19d48a599794ff64a25b553e951c2fb.pdf).

Conductor is based on the [Rasperry Pi
Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/), an
embedded development platorm.