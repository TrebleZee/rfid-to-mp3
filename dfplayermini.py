# A library to control the DFPlayer MP3 player
# Only partial implementation
# For more details of protocol see https://www.dfrobot.com/
# Created by Stewart Watkiss @PenguinTutor
# https://www.penguintutor.com 


from machine import UART, Pin
import time

class DFPlayerMini ():
    
    # how long to pause between read and write / subsequent reads
    sleep_time = 0.2
    debug = False
    
    sources = {
        'usb': 1,
        'sdcard': 2,
        'sd': 2,         # Allow sd as well as sd card
        'aux': 3,
        'sleep': 4,
        'flash': 5
        }
    
    def __init__ (self, uart_no, tx, rx):
        self.uart = UART(uart_no, baudrate=9600, tx=Pin(tx), rx=Pin(rx))
        self.uart.init(9600, bits=8, parity=None, stop=1)
        # Set to source when configured
        self.source = None
        # Keep track of if paused
        # Eg. allows resuming paused track when play is pressed
        self.paused = False
        
       
    # Simple check that looks for a standard 0x40 return code
    def check_return (self, byte_string):
        if byte_string[3] == 0x40:
            print ("Error receiving data")
            return False
        return True 
        
        
    # Send a byte string (bytes should alread be fully encoded)
    # then return the response
    def send_bytes (self, byte_string):
        sent_count = self.uart.write(byte_string)
        time.sleep(self.sleep_time)
        return self.read_reply()
        
    # Get a response - part of send_bytes, but also called seperately
    # where multiple replies are expected
    def read_reply (self):
        read_value = self.uart.read(10)
        if self.debug:
            if read_value == None:
                print ("None received")
                return None
            string_received = "".join([f"\\x{byte:02x}" for byte in read_value])
            print (f"Received {string_received}")
        return read_value
    
    
    def calc_checksum(self, data):
        # Data string
        sum = 0
        for byte in data:
            sum += byte
        #Convert to twos complement
        twos = (0xFFFF + 1 - sum)
        return twos
    
    def send_command (self, command, value=0, feedback=1):
        # Start = 7E
        # Version = FF
        # Len = 06
        # cmd
        # feedback = 1 or 0 (Whether response required) typically 1 for yes
        # para 1 (high data byte)
        # para 2 (low data byte)
        # checksum (from Version to para2) - 2 bytes
        # End = EF
        
        # Data without start, end or checksum
        data = b'\xFF\x06' + command.to_bytes(1) + feedback.to_bytes(1) + value.to_bytes(2)
        # Add checksum to data
        checksum = self.calc_checksum(data)
        data += checksum.to_bytes(2)
        # Add start and end bytes
        data_string = b'\x7E' + data + b'\xEF'
        string_sent = "".join([f"\\x{byte:02x}" for byte in data_string])
        if self.debug:
            print (f"Sending: {string_sent}")
        
        return self.send_bytes (data_string)
    
    def reset(self):
        self.paused = False
        #'reset' : b'\x7E\xFF\x06\x0C\x01\x00\x00\xFE\xEE\xEF'
        return_value = self.send_command(0x0C)
        #print (f"Return 1: {return_value}")
        # First return will be x41 with 0,0,0
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        # Reset wait 2 x sleep as sometimes needs to stabilise first
        time.sleep(self.sleep_time)
        time.sleep(self.sleep_time)
        # Next value should be x3f with 0,0,<response>
        return_value = self.read_reply()
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        #print (f"Return 2: {return_value}")
        # Now check for a valid return value - lower data byte = [6]
        # 0 = Timeout
        #string_recv = "".join([f"\\x{byte:02x}" for byte in return_value])
        if return_value[3] != 0x3f:
            # Expecting 3f - if not then just return false
            return False
        # 2 = Cardinserted, 4 = CardOnline, 7 = USBInserted, 9 = USBOnline, 10 = CardUSBOnline
        if return_value[6] in (0x02, 0x04, 0x07, 0x09, 0x10):
            return True
        # Any other value return False
        return False


    # Get number of files on card / disk / flash
    # If source is default or None then uses current source
    def query_num_files(self, source=None):
        query_code = None
        # If no source set use current, otherwise return false
        if source == None:
            if self.source == None:
                return False
            source = self.source

        # Now source is set from parameter or using defult
        # Different from datasheet which says x47 - TF card, x48 = U-disk
        if source in ('sdcard', 'sd'):
            query_code = 0x48
        elif source == 'usb':
            query_code = 0x47
        elif source == 'flash':
            query_code = 0x49
            
        
        return_value = self.send_command(query_code)
        print (f"query_num_files {return_value}")
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        time.sleep(self.sleep_time)
        # Now check for a valid return value - lower data byte = [6]
        return_value = self.read_reply()
        # Now check for a valid return value - lower data byte = [6]
        # 0 = Timeout
        #string_recv = "".join([f"\\x{byte:02x}" for byte in return_value])
        if return_value[3] != query_code:
            # Expecting 3f - if not then just return false
            return False

        # Return value of lower byte + upper byte x (FF+1)
        eval_value = (return_value[5] * 256) + return_value[6]
        print (f"Eval {eval_value}")
        return eval_value


    def get_volume(self):
        # eg.  b'\x7E\xFF\x06\x06\x01\x00\x0A\xFE\xEA\xEF' (10)
        return_value = self.send_command(0x43)
        # First return just confirm command
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            print(f"1{return_value}")
            return False
        time.sleep(self.sleep_time)
        # Retrieve actual value
        return_value = self.read_reply()
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            print(f"2{return_value}")
            return False
        if return_value[3] != 0x43:
            # Expecting 3f - if not then just return false
            print(f"3{return_value}")
            return False
        print(f"4{return_value}")
        return return_value[6]

    def set_volume(self, volume):
        # eg.  b'\x7E\xFF\x06\x06\x01\x00\x0A\xFE\xEA\xEF' (10)
        return_value = self.send_command(0x06, volume)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return self.check_return(return_value)
    
    def volume_up(self):
        return_value = self.send_command(0x04)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return self.check_return(return_value)

    def volume_down(self):
        return_value = self.send_command(0x05)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return self.check_return(return_value)


    # select source of audio - eg. "usb", "sdcard", "aux", "sleep", "flash"
    def select_source(self, source):
        self.paused = False
        #'sdcard' : b'\x7E\xFF\x06\x09\x01\x00\x02\xFE\xEF\xEF'
        return_value = self.send_command(0x09, self.sources[source])
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        self.source = source
        return True

    def stop(self):
        self.paused = False
        return_value = self.send_command(0x16)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return True
    
    def play (self, track_num):
        self.paused = False
        #'play1' : b'\x7E\xFF\x06\x03\x01\x00\x01\xFE\xF6\xEF',
        return_value = self.send_command(0x03, track_num)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return True
    
    def play_next (self):
        self.paused = False
        return_value = self.send_command(0x01)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return True
    
    def play_previous (self):
        self.paused = False
        return_value = self.send_command(0x02)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return True

    def play_loop (self, track_num):
        self.paused = False
        return_value = self.send_command(0x08, track_num)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return True

    def pause (self):
        self.paused = True
        return_value = self.send_command(0x0E)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return True
    
    # Play / resume if paused
    def start (self):
        self.paused = False
        return_value = self.send_command(0x0D)
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        return True
    
    # Returns False if out of sync / error, 0 if stopped, 1 if playing, 2 if paused
    def get_status(self):
        #print ("\nChecking status")
        return_value = self.send_command(0x42)
        # First return just confirm command
        # Check for no return value or length of value is not correct        
        if return_value == None or len(return_value) != 10:
            #print ("No response - retry")
            # First retry:
            return_value = self.read_reply()
            if return_value == None or len(return_value) != 10:
                # If still not a valid reply return without checking for a value
                return False
        #print (f"Pre-return value {return_value[3]} - {return_value[5]}:{return_value[6]}")
        time.sleep(self.sleep_time)
        # Retrieve actual value
        return_value = self.read_reply()
        # Check for no return value or length of value is not correct
        if return_value == None or len(return_value) != 10:
            # If so just return without checking for a value
            return False
        # If get a generic reply - then likely missed previously, so check again for the value reply
        if return_value[3] == 0x41:
            time.sleep(self.sleep_time)
            return_value = self.read_reply()
        #print (f"Return value {return_value[3]} - {return_value[5]}:{return_value[6]}")
        if return_value[3] != 0x42:
            # Expecting 42 - if not then just return false
            return False
        return return_value[6]
