from machine import I2C
import time

class i2c_class:
    i2c_instance = None
    i2c_freq = None
    scl_pin = None
    sda_pin = None
    i2c_address = None
    i2c_address_width = None
    led_state = 0

    def __init__(self, i2c_address=None, i2c_address_width=8, scl_pin=None, sda_pin=None, i2c_freq=None):
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.i2c_address = i2c_address
        self.i2c_freq = i2c_freq
        self.i2c_address_width = i2c_address_width
        self.initiate_i2c()

    def initiate_i2c(self):
        if(self.scl_pin == None):
            return
        if(self.sda_pin == None):
            return
        if(self.i2c_freq == None):
            return
        self.i2c_instance = I2C(0, scl=self.scl_pin, sda=self.sda_pin, freq=self.i2c_freq)

    def reg_write(self, reg, data):
        if(self.i2c_instance == None):
            return
        #Write bytes to the specified register.
        # Construct message
        msg = bytearray()
        msg.append(data)
        # Write out message to register
        self.i2c_instance.writeto_mem(self.i2c_address, reg, msg, addrsize=self.i2c_address_width)
    
    def reg_read(self, reg, num_bytes=1):
        if(self.i2c_instance == None):
            return None
        #Read byte(s) from specified register. If nbytes > 1, read from consecutive registers.
        # Check to make sure caller is asking for 1 or more bytes
        if num_bytes < 1:
            return bytearray()    
        # Request data from specified register(s) over I2C
        data = self.i2c_instance.readfrom_mem(self.i2c_address, reg, num_bytes, addrsize=self.i2c_address_width)
        return data

    def list_reg_writes(self, reg_list):
        if(self.i2c_instance == None):
            return
        for register in reg_list:                
            self.reg_write(register[0], register[1])
            print(register[0], register[1])
            time.sleep(0.35)