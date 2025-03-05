import mido
import numpy as np
import sounddevice as sd
import threading


class MinimalFMSynth:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.active_notes = {}  # note number -> phase

        # Fixed FM synthesis parameters
        self.carrier_freq_ratio = 1.0
        self.modulator_freq_ratio = 2.0
        self.modulation_index = 5.0

        # Start audio stream
        self.stream = sd.OutputStream(
            channels=1,
            samplerate=sample_rate,
            callback=self._audio_callback
        )
        self.stream.start()

        # Auto-select first available MIDI port
        available_ports = mido.get_input_names()
        if available_ports:
            self.port_name = available_ports[0]
            print(f"Connected to MIDI port: {self.port_name}")

            # Start MIDI processing thread
            self.midi_thread = threading.Thread(target=self._midi_loop)
            self.midi_thread.daemon = True
            self.midi_thread.start()
        else:
            print("No MIDI ports available")

    def _midi_loop(self):
        """Process incoming MIDI messages"""
        with mido.open_input(self.port_name) as inport:
            for msg in inport:
                if msg.type == 'note_on' and msg.velocity > 0:
                    self.active_notes[msg.note] = 0.0  # Initialize phase
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in self.active_notes:
                        del self.active_notes[msg.note]

    def _midi_to_freq(self, note_num):
        """Convert MIDI note number to frequency in Hz"""
        return 440 * 2 ** ((note_num - 69) / 12)

    def _audio_callback(self, outdata, frames, time, status):
        """Generate audio samples"""
        t = np.arange(frames) / self.sample_rate
        output = np.zeros(frames)

        for note, phase in list(self.active_notes.items()):
            freq = self._midi_to_freq(note)
            carrier_freq = freq * self.carrier_freq_ratio
            modulator_freq = freq * self.modulator_freq_ratio

            # Simple FM synthesis
            modulator = np.sin(2 * np.pi * modulator_freq * t + phase)
            carrier = np.sin(2 * np.pi * carrier_freq * t +
                             self.modulation_index * modulator)

            output += carrier * 0.1  # Reduce amplitude to prevent clipping

            # Update phase for next buffer
            self.active_notes[note] = phase + 2 * np.pi * modulator_freq * frames / self.sample_rate

        outdata[:, 0] = output


if __name__ == "__main__":
    synth = MinimalFMSynth()
    print("Minimal FM Synth running. Press Ctrl+C to stop.")

    try:
        # Keep program running until keyboard interrupt
        while True:
            input()
    except KeyboardInterrupt:
        print("Synth stopped")
    finally:
        if hasattr(synth, 'stream'):
            synth.stream.stop()