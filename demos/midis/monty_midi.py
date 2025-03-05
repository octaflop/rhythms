import mido
import time

# Define the main melody notes of the Monty Python theme
# Using MIDI note numbers where 60 is middle C
notes = [
    72, 76, 79, 72, 76, 79,  # First phrase
    71, 74, 77, 71, 74, 77,  # Second phrase
    69, 72, 76, 69, 72, 76,  # Third phrase
    67, 71, 74, 67, 71, 74,  # Fourth phrase

    # Final descending run
    72, 71, 69, 67, 65, 64, 62, 60
]

# Note durations in seconds
durations = [
    0.2, 0.2, 0.2, 0.2, 0.2, 0.4,  # First phrase
    0.2, 0.2, 0.2, 0.2, 0.2, 0.4,  # Second phrase
    0.2, 0.2, 0.2, 0.2, 0.2, 0.4,  # Third phrase
    0.2, 0.2, 0.2, 0.2, 0.2, 0.4,  # Fourth phrase

    # Final descending run
    0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.4
]

def play_monty_python_theme():
    # Find the Korg device - it will appear in the list of output ports
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

    # Connect to the selected MIDI output
    print(f"Connecting to: {korg_port}")
    with mido.open_output(korg_port) as outport:
        # Use a bright brass or trumpet sound (MIDI program change 57)
        outport.send(mido.Message('program_change', program=56))

        # Play the melody
        for note, duration in zip(notes, durations):
            # Note on message, velocity 100 (moderately loud)
            outport.send(mido.Message('note_on', note=note, velocity=100))
            time.sleep(duration)
            # Note off
            outport.send(mido.Message('note_off', note=note, velocity=0))
            # Small gap between notes
            time.sleep(0.05)

if __name__ == "__main__":
    print("Playing the Monty Python theme (The Liberty Bell) on Korg device...")
    for i in range(3):
        play_monty_python_theme()