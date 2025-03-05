from pathlib import Path
from typing import Optional

import mido


def load_midi_file(midi_path: Path) -> Optional[mido.MidiFile]:
    """
    Load a MIDI file from the given path.

    Args:
        midi_path (Path): Path to the MIDI file

    Returns:
        Optional[mido.MidiFile]: The loaded MIDI file object or None if loading fails

    Raises:
        FileNotFoundError: If the MIDI file doesn't exist
        mido.MidiFileError: If the file is not a valid MIDI file
    """
    try:
        if not midi_path.exists():
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")

        midi_file = mido.MidiFile(str(midi_path))
        return midi_file

    except mido.MidiFileError as e:
        print(f"Error loading MIDI file: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error loading MIDI file: {e}")
        return None


def get_midi_info(midi_file: mido.MidiFile) -> dict:
    """
    Get basic information about the MIDI file.

    Args:
        midi_file (mido.MidiFile): The loaded MIDI file object

    Returns:
        dict: Dictionary containing MIDI file information
    """
    return {
        'type': midi_file.type,
        'ticks_per_beat': midi_file.ticks_per_beat,
        'length_seconds': midi_file.length,
        'number_of_tracks': len(midi_file.tracks)
    }


def get_korg_port():
    """
    Find and return the Korg Volca MIDI port.

    Returns:
        str: Selected MIDI port name
    """
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


def play_midi_file(midi_file: mido.MidiFile):
    """
    Play the MIDI file on the Korg Volca device.

    Args:
        midi_file (mido.MidiFile): The MIDI file to play
    """
    korg_port = get_korg_port()
    print(f"Connecting to: {korg_port}")

    with mido.open_output(korg_port) as outport:
        # Reset all controllers
        outport.send(mido.Message('control_change', control=121, value=0))

        print(f"Playing MIDI file...")
        for msg in midi_file.play():
            # Filter out messages we want to send
            if msg.type in ['note_on', 'note_off', 'program_change', 'control_change']:
                outport.send(msg)


if __name__ == "__main__":
    # Example usage
    midi_path = Path("example.mid")
    midi_file = load_midi_file(midi_path)

    if midi_file:
        info = get_midi_info(midi_file)
        print("MIDI File Information:")
        for key, value in info.items():
            print(f"{key}: {value}")

        # Play the MIDI file
        play_midi_file(midi_file)
