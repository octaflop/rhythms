import mido
import time
from mido import Message, MidiTrack


def find_volca_port():
    available_ports = mido.get_output_names()
    print("Available MIDI output ports:")
    for i, port in enumerate(available_ports):
        print(f"{i}: {port}")

    # Look for the Korg device
    korg_port = None
    for port in available_ports:
        if 'volca' in port.lower():
            korg_port = port
            break

    if not korg_port:
        print("Korg volca device not found. Please select a port number from the list above:")
        port_index = int(input())
        korg_port = available_ports[port_index]

    return korg_port


def play_liberty_bell():
    korg_port = find_volca_port()
    print(f"Connecting to: {korg_port}")

    with mido.open_output(korg_port) as outport:
        # Setup initial program changes
        outport.send(Message('program_change', channel=0, program=56))  # Trumpet
        outport.send(Message('program_change', channel=1, program=60))  # French horn
        outport.send(Message('program_change', channel=9, program=14))  # Tubular bells

        # Transposed F major notes
        notes = [
            65, 69, 72, 65, 69, 72,  # F-A-C
            64, 67, 71, 64, 67, 71,  # E-G-B♭
            62, 65, 69, 62, 65, 69,  # D-F-A
            60, 64, 67, 60, 64, 67,  # C-E-G
            65, 64, 62, 60, 58, 57, 55, 53  # Descending
        ]

        # Convert PPQN-based durations to seconds (at 120 BPM)
        seconds_per_beat = 60 / 120  # At 120 BPM
        base_duration = 0.2  # roughly equivalent to eighth note at 120 BPM

        # Main loop
        for i, note in enumerate(notes):
            # Main trumpet
            outport.send(Message('note_on', note=note, velocity=100, channel=0))
            # Harmony (French horn)
            outport.send(Message('note_on', note=note - 7, velocity=80, channel=1))

            # Add tubular bells every 6 notes
            if i % 6 == 0:
                outport.send(Message('note_on', note=77, velocity=100, channel=9))

            # Duration logic
            if i < len(notes) - 8:  # Main melody
                if i % 2 == 0:
                    time.sleep(base_duration * 1.5)  # Dotted eighth
                else:
                    time.sleep(base_duration)  # Eighth note
            else:  # Final descending run
                time.sleep(base_duration)

            # Note offs
            outport.send(Message('note_off', note=note, velocity=0, channel=0))
            outport.send(Message('note_off', note=note - 7, velocity=0, channel=1))
            if i % 6 == 0:
                outport.send(Message('note_off', note=77, velocity=0, channel=9))

            time.sleep(0.05)  # Small gap between notes


if __name__ == "__main__":
    print("Playing The Liberty Bell March on Korg device...")
    for i in range(3):
        play_liberty_bell()
        time.sleep(1)  # Pause between repetitions
