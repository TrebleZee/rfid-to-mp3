# Newcomer Guide

This project runs on a Raspberry Pi Pico (MicroPython) and plays MP3 files when specific RFID tags are scanned.

## High-level flow

1. `main.py` calls `DetectAndPlay(180)` in `rfid_to_mp3.py`.
2. `rfid_to_mp3.py` initializes:
   - RFID reader (`MFRC522`) over SPI
   - MP3 module (`DFPlayerMini`) over UART
   - On-board LED for activity indication
3. During runtime, the loop scans for RFID tags once per second.
4. If a known tag is detected, it maps UID -> track number and sends a play command to DFPlayer.
5. If no activity occurs for `sleepTime` seconds, the loop exits.

## File map

- `main.py`: Tiny entrypoint; sets the idle timeout.
- `rfid_to_mp3.py`: Application logic (device setup, scan loop, tag mapping, playback behavior).
- `data_read.py`: Helper script to print RFID tag IDs so you can populate mappings.
- `dfplayermini.py`: Driver for DFPlayer serial protocol.
- `mfrc522.py`: Driver for MFRC522 RFID module and card operations.
- `README.md`: Hardware context and wiring/pinout.

## What to edit first

Most first-time changes happen in `rfid_to_mp3.py`:

- Change `tag_to_sound` to your own card IDs and MP3 track numbers.
- Adjust `DetectAndPlay(sleepTime)` timeout and behavior.
- Tune volume (`set_volume(20)`) and scan cadence (`utime.sleep(1)`).

## Important implementation details

- UID conversion uses little-endian bytes (`int.from_bytes(bytes(uid), "little")`). Keep this consistent when comparing IDs.
- Re-trigger protection uses the `detect` variable; the same tag must be removed/re-seen before replaying.
- `notFoundCounter` resets `detect` after a few misses to avoid sticky state.
- DFPlayer reset and source selection are required before playback.

## Operational assumptions

- This code is written for MicroPython (`machine`, `utime`) and cannot run directly in CPython.
- Hardware pin numbers in code should match your Pico wiring.
- Track numbers passed to DFPlayer (`play(n)`) correspond to files on the SD card as expected by DFPlayer naming/order rules.

## Suggested learning path

1. **Run `data_read.py`** to gather real UID values from your tags.
2. **Populate `tag_to_sound`** and verify each tag plays expected audio.
3. **Read `DetectAndPlay` end-to-end** to understand state handling (`detect`, `notFoundCounter`, `idleTime`).
4. **Study drivers lightly**:
   - `dfplayermini.py`: command frame building + replies
   - `mfrc522.py`: anti-collision/select flow for UIDs
5. **Then add one feature at a time**, e.g. unknown-tag feedback sound, per-tag volume, or debounce timing.
