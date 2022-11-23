import machine
import hm01b0
import time
import arducam

def main():
    led = machine.Pin("LED", machine.Pin.OUT)

    time.sleep(1)
    print("Starting picam")
    led.on()
    # time.sleep(5)
    # led.off()
    # time.sleep(5)

    print("creating arducam class")
    my_cam = arducam.arducam_class()
    my_cam.i2c_address = hm01b0.hm01b0_address
    my_cam.i2c_address_width = 16
    my_cam.i2c_freq = hm01b0.hm01b0_freq
    my_cam.scl_pin = machine.Pin(5)
    my_cam.sda_pin = machine.Pin(4)
    my_cam.vsync_pin = machine.Pin(16, machine.Pin.IN)
    my_cam.hsync_pin = machine.Pin(15, machine.Pin.IN)
    my_cam.pix_clk_pin = machine.Pin(14, machine.Pin.OUT)
    my_cam.data_pin = machine.Pin(6, machine.Pin.IN)
    side_pin = machine.Pin(17, machine.Pin.OUT)

    my_cam.pix_clk_freq = hm01b0.hm01b0_pix_clk_freq

    print("initializing camera i2c")
    my_cam.initiate_i2c()

    time.sleep(1)

    print("initializing camera pins")
    my_cam.initialize_pins()

    print("configuring camera over i2c")
    my_cam.i2c_instance.list_reg_writes(hm01b0.hm01b0_regs_init_324x244)

    print("starting pixel clock")
    my_cam.start_pix_clk()

    print("creating pio class")
    pio = hm01b0.cam_pio_class(0, 120_000_000, my_cam.data_pin, my_cam.vsync_pin, side_pin)
    time.sleep(1)

    print("starting pio for one frame")
    #pio.capture_frame()
    pio.get_frame(324, 244)
    print(pio.image_array)
    
    # print("getting frame data")
    # data = pio.get_frame_data()
    # print(data)

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
        
        time.sleep(2)
        led.on()
        time.sleep(2)
        led.off()
        pio.get_frame(324, 244)
        print(pio.image_array)

if __name__ == "__main__":
   main()