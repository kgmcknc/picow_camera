import machine
import hm01b0
import time
import arducam

def main():
    led = machine.Pin("LED", machine.Pin.OUT)

    time.sleep(1)
    print("Starting picam")
    led.on()
    time.sleep(5)
    led.off()
    time.sleep(5)

    print("creating arducam class")
    my_cam = arducam.arducam_class()
    my_cam.i2c_address = hm01b0.hm01b0_address
    my_cam.i2c_address_width = 16
    my_cam.i2c_freq = hm01b0.hm01b0_freq
    my_cam.scl_pin = machine.Pin(5)
    my_cam.sda_pin = machine.Pin(4)
    my_cam.data_pin = machine.Pin(6, machine.Pin.IN)
    my_cam.pix_clk_pin = machine.Pin(14, machine.Pin.OUT)
    my_cam.hsync_pin = machine.Pin(15, machine.Pin.IN)
    my_cam.vsync_pin = machine.Pin(16, machine.Pin.IN)

    my_cam.pix_clk_freq = hm01b0.hm01b0_pix_clk_freq
    time.sleep(1)

    print("initializing camera i2c")
    my_cam.initiate_i2c()

    time.sleep(1)

    list = my_cam.i2c_instance.i2c_instance.scan()
    print(list)

    time.sleep(1)

    print("initializing camera pins")
    my_cam.initialize_pins()

    time.sleep(1)

    print("configuring camera over i2c")
    my_cam.i2c_instance.list_reg_writes(hm01b0.hm01b0_regs_init_324x244)

    print("starting pixel clock")
    my_cam.start_pix_clk()
    time.sleep(1)

    print("done")
    time.sleep(1)

    print("creating pio class")
    pio = hm01b0.cam_pio_class(0, 60000000, my_cam.data_pin)
    time.sleep(1)

    print("starting pio")
    pio.start()

    print("capturing frames for 5 seconds")
    time.sleep(5)

    print("stopping pio")
    pio.stop()
    
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
        time.sleep(2)
        led.on()
        time.sleep(2)
        led.off()

if __name__ == "__main__":
   main()