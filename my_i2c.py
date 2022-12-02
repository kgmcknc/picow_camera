from machine import I2C
import time

class i2c_class:
    def __init__(self, scl_pin=None, sda_pin=None, i2c_freq=None, i2c_address=None, i2c_address_width=None):
        self.i2c_instance = None
        self.i2c_address = i2c_address
        self.i2c_address_width = i2c_address_width
        self.initiate_i2c(scl_pin, sda_pin, i2c_freq)

    def initiate_i2c(self, scl_pin=None, sda_pin=None, i2c_freq=None, i2c_address=None, i2c_address_width=None):
        if(scl_pin == None):
            return
        if(sda_pin == None):
            return
        if(i2c_freq == None):
            return
        if(not(i2c_address == None)):
            self.i2c_address = i2c_address
        if(not(i2c_address_width == None)):
            self.i2c_address_width = i2c_address_width
        self.i2c_instance = I2C(0, scl=scl_pin, sda=sda_pin, freq=i2c_freq)

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

    def list_reg_writes(self, reg_list, delay=0.0):
        if(self.i2c_instance == None):
            return
        for register in reg_list:                
            self.reg_write(register[0], register[1])
            print(register[0], register[1])
            if(delay > 0):
                time.sleep(delay)