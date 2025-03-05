import mido
import time
from typing import List, Tuple


class MidiPlayer:
    def __init__(self):
        # Default melody (simplified Monty Python theme)
        self.default_melody: List[Tuple[int, float]] = [
            (72, 0.2), (76, 0.2), (79, 0.4),  # First phrase
            (71, 0.2), (74, 0.2), (77, 0.4),  # Second phrase
            (69, 0.2), (72, 0.2), (76, 0.4),  # Third phrase
        ]
        self.recorded_melody: List[Tuple[int, float]] = []
        self.port_name = self._select_midi_port()

    def _select_midi_port(self) -> str:
        """Select MIDI output port"""
        available_ports = mido.get_output_names()
        print("Available MIDI output ports:")
        for i, port in enumerate(available_ports):
            print(f"{i}: {port}")

        port_index = int(input("Select port number: "))
        return available_ports[port_index]

    def play_melody(self, melody: List[Tuple[int, float]]):
        """Play a melody from a list of (note, duration) tuples"""
        with mido.open_output(self.port_name) as outport:
            for note, duration in melody:
                outport.send(mido.Message('note_on', note=note, velocity=100))
                time.sleep(duration)
                outport.send(mido.Message('note_off', note=note, velocity=0))
                time.sleep(0.05)

    def record_melody(self):
        """Record a melody from MIDI input"""
        self.recorded_melody = []
        print("Recording... Press Ctrl+C to stop")

        try:
            with mido.open_input() as inport:
                start_time = time.time()
                last_note_time = start_time
                current_note = None

                for msg in inport:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        if current_note:
                            duration = time.time() - last_note_time
                            self.recorded_melody.append((current_note, duration))
                        current_note = msg.note
                        last_note_time = time.time()

                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        if current_note == msg.note:
                            duration = time.time() - last_note_time
                            self.recorded_melody.append((current_note, duration))
                            current_note = None

        except KeyboardInterrupt:
            print("\nRecording stopped")


def main():
    player = MidiPlayer()

    while True:
        print("\n1. Play default melody")
        print("2. Record new melody")
        print("3. Play recorded melody")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            player.play_melody(player.default_melody)
        elif choice == '2':
            player.record_melody()
        elif choice == '3':
            if player.recorded_melody:
                player.play_melody(player.recorded_melody)
            else:
                print("No recorded melody available")
        elif choice == '4':
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()