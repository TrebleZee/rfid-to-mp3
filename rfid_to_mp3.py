from mfrc522 import MFRC522
from machine import Pin
from dfplayermini import DFPlayerMini as DFPlayer
import utime

# Initialize RFID reader (SPI)
rfid = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)

# Initialize DFPlayer Mini (UART)
dfplayer = DFPlayer(0, 12, 13)

# Initialise board LED (Pin)
LED = Pin(25,Pin.OUT)

# Dictionary mapping RFID tag IDs to sound file numbers
tag_to_sound = {
    3801826825: 1,  # Replace with actual tag ID
    30289113: 2,
    51533627: 3
}
# Main function to scan for RFID tags and play the corresponding audio
def DetectAndPlay(sleepTime):  # Set a time(s) so sleep after
    
    while True:    # Loops until MP3 player successfully resets
        print ("Reset")
        if dfplayer.reset() == True:
            break
    
    # Initialise SD card
    print ("Set SD Card")
    read_value = dfplayer.select_source('sdcard')
    print (f"Source set: {read_value}")
    
    # Set volume /30
    print ("Set Volume 20")
    read_value = dfplayer.set_volume(20)
    
    print("Place a block on the reader...")

    detect = 0
    notFoundCounter = 0
    idleTime = 0

    while True:
        if idleTime >= sleepTime:
            break
        LED.value(0)
        (stat, tag_type) = rfid.request(rfid.REQIDL)	#
        
        if stat == rfid.OK:
            (stat, uid) = rfid.SelectTagSN()
            
            if stat == rfid.OK:
                tag_id = int.from_bytes(bytes(uid), "little")
                print(f"Detected Tag ID: {tag_id}")
                notFoundCounter = 0
                LED.value(1)
                if tag_id != detect:
                    if tag_id in tag_to_sound:
                        print(f"Playing sound {tag_to_sound[tag_id]}.mp3")
                        dfplayer.play(tag_to_sound[tag_id])
                        print(detect)
                        detect = tag_id
                        print(detect)
                        runTime = 0
                         
                    else:
                        print("Unknown tag. Please assign it a sound.")
                        detect = 0
                else:
                    print("waiting for new block")
            else:
                detect = 0
                print("tag id not found")
        else:
            print(f"no block found. Status: {stat}")
            notFoundCounter += 1
            if notFoundCounter >= 3:
                detect = 0
        utime.sleep(1)  # Small delay before next scan
        idleTime += 1
