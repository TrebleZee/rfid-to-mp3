# RFID To MP3
Part of my design and technology GCSE coursework, this is the code I created for an educational toy that aims to teach children about the shape of letters and how they sound.

## About
Courtesy of Daniel Perron, the MRFC522 class contains all the functions needed to control the RFID module. More info can be found here https://github.com/danjperron/micropython-mfrc522

Courtesy of Stewart Watkiss AKA PenguinTutor, the DFPlayerMini class contains the most useful functions to control the serial communication to the DFPlayer MP3 player module. More info can be found here https://github.com/penguintutor/dfplayermini-pico


## Parts List:

Rasberry Pi Pico 2

DFPlayer Mini (MP3 player)

MFRC-522 Module (RFID Scanner)

8 Ohm 0.5 Watt slim speaker

## Pinout:

**RFID (MFRC522) --> Raspberry Pi Pico (SPI)**

VCC -->	3.3V or breadboard power rail

GND	--> GND or breadboard ground rail

MISO --> GP4

MOSI --> GP7

SCK -->	GP6

RST -->	GP22

SDA(SS) --> GP5


**MP3 player (DFPlayer mini) --> Raspberry Pi Pico (UART)**

VCC --> VCC -->	3.3V or breadboard power rail

GND	--> GND or breadboard ground rail

RX --> GP12 

TX --> GP13


**MP3 player (DFPlayer mini) --> Speaker**

SPK1 --> +ive terminal

SPK2 --> -ive terminal
