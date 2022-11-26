from machine import Pin
import hm01b0
import time
import my_i2c

width=324
height=324
bits = 8

def main():
    led = Pin("LED", Pin.OUT)

    time.sleep(1)
    print("Starting picam")
    led.on()
    # time.sleep(5)
    # led.off()
    # time.sleep(5)

    print("creating arducam class")
    my_cam = my_i2c.i2c_class()
    my_cam.i2c_address = hm01b0.hm01b0_address
    my_cam.i2c_address_width = 16
    i2c_freq = hm01b0.hm01b0_freq
    scl_pin = Pin(5)
    sda_pin = Pin(4)
    vsync_pin = Pin(16, Pin.IN)
    hsync_pin = Pin(15, Pin.IN)
    # my_cam.pix_clk_pin = Pin(14, Pin.OUT)
    # pix_clk_pin = Pin(14, Pin.IN, pull=None)
    data_pin = Pin(6, Pin.IN)
    #side_pin = Pin(17, Pin.OUT)

    #my_cam.pix_clk_freq = hm01b0.hm01b0_pix_clk_freq

    print("initializing camera i2c")
    my_cam.initiate_i2c(scl_pin, sda_pin, i2c_freq)

    time.sleep(1)

    # print("initializing camera pins")
    # my_cam.initialize_pins()
    
    # print("starting pixel clock")
    #my_cam.start_pix_clk()

    # time.sleep(1)
    
    print("configuring camera over i2c")
    my_cam.list_reg_writes(hm01b0.hm01b0_regs_init_324x244)

    print("creating pio class")
    pio = hm01b0.cam_pio_class(vsync_pin, 0, 125_000_000, data_pin)
    time.sleep(1)

    print("starting pio for one frame")
    #pio.capture_frame()
    #pio.get_frame(324, 244)
    #print(bytes(pio.image_array))
    
    # print("getting frame data")
    # data = pio.get_frame_data()
    # print(data)

    #pio.get_pixel_line_count(width, height, 120_000_000, my_cam.data_pin, my_cam.hsync_pin, side_pin)
    #pio.get_total_count(width, height, 120_000_000, my_cam.data_pin, my_cam.hsync_pin, side_pin)
    time.sleep(2)

    while(1):
        #hsync = my_cam.hsync_pin.value()
        #vsync = my_cam.vsync_pin.value()
        # if(hsync):
        #     print("got hsync")
        # if(vsync):
        #     print("got vsync")
        # for register in hm01b0.hm01b0_regs_init_324x244:
        #     data = my_cam.i2c_instance.reg_read(register[0])
        #     print(register[0], data)
        #     time.sleep(0.5)
        
        # data = pio.get_data(4)
        # print(data)
        
        pio.get_frame(width, height, bits, 125_000_000, data_pin, vsync_pin)
        print(pio.image_array)
        #pio.get_pixel_line_count(width, height, 125_000_000, my_cam.data_pin, my_cam.hsync_pin, side_pin)
        #pio.get_total_count(width, height, 125_000_000, my_cam.data_pin, my_cam.hsync_pin, side_pin)

        time.sleep(5)
        #pio.get_line_count(324,244, 120_000_000, data_pin, hsync_pin)
        led.on()
        time.sleep(5)
        #pio.get_pixel_count(324,244, 120_000_000, data_pin, hsync_pin)
        led.off()

if __name__ == "__main__":
   main()