# rfid-to-mp3
Part of my design and technology GCSE coursework, this is an educational toy that aims to teach children about the shape of letters and how they sound.

**Parts List**
Rasberry Pi Pico 2
DFPlayer Mini (MP3 player)
MFRC-522 Module (RFID Scanner)
8 Ohm 0.5 Watt slim speaker

**Pin Out**
RFID (MFRC522) --> Raspberry Pi Pico (SPI)
VCC -->	3.3V or breadboard power rail
GND	--> GND or breadboard ground rail
MISO --> GP16
MOSI --> GP15
SCK -->	GP14
RST -->	GP13
SDA(SS) --> GP17
