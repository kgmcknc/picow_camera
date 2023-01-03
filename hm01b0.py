from micropython import const
from rp2 import PIO
from rp2 import StateMachine
from rp2 import asm_pio
from array import array
import my_dma
from math import ceil

hm01b0_i2c_address = 0x24
hm01b0_i2c_freq = 400000
hm01b0_reg_address_width = 16
hm01b0_i2c_delay = 0.5

@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32)
def full_frame_toggle_test():
    set(x, 31)
    set(y, 1)
    label("top")
    wait(1, pin, 9)
    wait(1, pin, 8)
    jmp(x_dec,"x1")
    jmp("x0")
    
    label("x1")
    #set(x, 0)
    set(y, 1)
    in_(y, 1)
    # in_(y, 1)
    wait(0, pin, 8)
    jmp("top")

    label("x0")
    set(x, 31)
    in_(null, 1)
    # in_(y, 1)
    wait(0, pin, 8)
    jmp("top")
    # in_(pins, 1)

@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32)
def hm01b0_get_line_count():
    set(y,0)
    
    label("top")
    wait(1, pin, 10)
    wait(1, pin, 9)
    mov(y, invert(y))
    jmp(y_dec, "y_sub")
    label("y_sub")
    mov(y, invert(y))
    in_(y, 32)
    wait(0, pin, 9) .delay(30)
    jmp("top")

@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32)
def hm01b0_get_pixel_count():
    set(x, 0)
    
    label("top")
    wait(1, pin, 9)
    wait(1, pin, 8)
    mov(x, invert(x))
    jmp(x_dec, "x_sub")
    label("x_sub")
    mov(x, invert(x))
    wait(0, pin, 8) .delay(10)
    jmp(pin, "top")
    in_(x,32)
    set(x,0)
    jmp("top")

@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32, sideset_init=PIO.OUT_LOW)
def hm01b0_get_pixel_line_count():
    set(x, 0)
    set(y, 0)
    
    label("top")
    wait(1, pin, 9)
    wait(1, pin, 8) .side(1)
    mov(x, invert(x))
    jmp(x_dec, "x_sub")
    label("x_sub")
    mov(x, invert(x))
    wait(0, pin, 8) .delay(4)
    jmp(pin, "top") .side(0)
    in_(x,32)
    set(x,0)
    mov(y, invert(y))
    jmp(y_dec, "y_sub")
    label("y_sub")
    mov(y, invert(y))
    in_(y, 32)
    jmp("top")


@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32)
def hm01b0_get_total_count():
    set(x, 0)
    mov(x, invert(x))
    
    label("top")
    #wait(1, pin, 9)
    wait(1, pin, 8)
    #wait(0, pin, 8)
    jmp(x_dec, "top")
    # label("x_sub")
    # wait(0, pin, 8)
    # jmp(pin, "top")

@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32)
def hm01b0_run():
    wrap_target()
    wait(1, pin, 9)
    wait(1, pin, 8)
    in_(pins, 1)
    wait(0, pin, 8)
    wrap()

@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32)
def hm01b0_get_frame_with_lines():
    # init line counter y to 0
    set(y, 0)
    # put y in the isr and push
    mov(isr, y)
    push()
    # invert for next add
    mov(y, invert(y))

    # wait for frame start
    wait(1, pin, 10)
    wait(1, pin, 9)

    label("top")
    # this will continue to top while hsync is high
    jmp(pin, "get_line")
    # when it's low, we go here which is end of line
    # if vsync still high
    # increment line counter and write in and then wait for hsync to be high
    # make sure frame is still high before writing next line number
    wait(1, pin, 10)
    # y already inverted, so dec to add one
    jmp(y_dec, "y_add")
    label("y_add")
    # invert back to have the line number
    mov(y, invert(y))
    # copy y to isr and push
    mov(isr, y)
    push()
    # invert for next add time
    mov(y, invert(y))
    # continue to get next line
    wait(1, pin, 9)
    label("get_line")
    wait(1, pin, 8)
    in_(pins, 1)
    wait(0, pin, 8)
    jmp("top")

@asm_pio(autopush=True, fifo_join=PIO.JOIN_RX, in_shiftdir=PIO.SHIFT_RIGHT, out_shiftdir=PIO.SHIFT_RIGHT, push_thresh=32)
def hm01b0_get_frame():
    # vsync,hsync,pix_clk,d0

    irq(clear, 0)    # clear irq if it's somehow set...
    # set(y, 1)        # set initial line number to 1
    # mov(y, isr)      # write line number isr
    # push()    # push line number to rx_fifo
    
    wait(0, pin, 10) # wait for vsync 0 (not processing frame)
    wait(1, pin, 10) # wait for vsync being high to start frame

    label("process_frame")   # create lable for processing the frame

    wait(1, pin, 9) # wait hsync high
    label("process_line")
    wait(1, pin, 8) # wait pix clk high
    #in_(pins, 1)    # get data from pins
    set(x, 1)
    in_(x, 1)
    #push()
    wait(0, pin, 8) # wait pix clk low
    jmp(pin, "process_line")

    #line is done
    # nop()
    # nop()
    # nop()
    # nop()

    push()      # push any leftover bits in isr
    # set(y, y+1) # increment line counter
    # mov(y, isr) # write line number isr
    # push()      # push line number to rx_fifo

    mov(osr, pins)
    out(x, 9)
    mov(x, osr)

    jmp(x, "process_frame")

    irq(0)                # set irq to go high in system
    label("loop_forever") # create label to loop forever
    nop()# .delay(20)     # nop and delay number of cycles
    jmp("loop_forever")   # go to label to loop forever

    # irq(clear, 0)    # clear irq if it's somehow set...
    # set(y, 1)        # set initial line number to 1
    # mov(y, isr)      # write line number isr
    # push()           # push line number to rx_fifo
    
    # wait(0, pin, 0) # wait for vsync 0 (not processing frame)
    # wait(1, pin, 0) # wait for vsync being high to start frame

    # label("process_frame")   # create lable for processing the frame
    # jmp(1, "process_line")   # process line if hsync high
    # jmp(0, "process_frame")  # if vsync still high, process frame
    # irq(0)                # set irq to go high in system
    # jmp("loop_forever")
    # jmp("frame_done")        # else, vsync low, frame is done

    # label("process_line")    # create label for processing line of pixels
    # jmp(2, "get_pixel")      # get pixel if pix clk high
    # jmp(1, "process_line")   # continue on line if hsync high
    # jmp("line_done")         # else, hsync low, line is done

    # label("get_pixel")
    # in_(pins, 4)             # get data from pins
    # wait(0, pin, 2)          # wait pix clk low
    # jmp("process_line")      # go back to check line

    # # line is done
    # label("line_done")
    # #push()      # push any leftover bits in isr
    # #set(y, y+1) # increment line counter
    # #mov(y, isr) # write line number isr
    # #push()      # push line number to rx_fifo
    # jmp("process_frame")
    
    # label("frame_done")   # label we go to when frame is done
    # irq(0)                # set irq to go high in system
    # label("loop_forever") # create label to loop forever
    # nop()# .delay(20)     # nop and delay number of cycles
    # jmp("loop_forever")   # go to label to loop forever
    
class cam_pio_class:
    vsync_pin = None
    hsync_pin = None
    base_pin = None
    jmp_pin = None
    sm_freq = None
    sm_id = None
    sm_inst = None
    processing_frame = 0
    frame_done = 0
    dma_inst = None
    image_array = None
    x_res = None
    y_res = None

    def __init__(self, vsync_pin = None, hsync_pin = None, sm_id=None, freq=None, base_pin=None, jmp_pin=None):
        self.vsync_pin = vsync_pin
        self.hsync_pin = hsync_pin
        self.base_pin = base_pin
        self.jmp_pin = jmp_pin
        self.sm_freq = freq
        self.sm_id = sm_id
        self.processing_frame = 0
        self.frame_done = 0
        self.dma_inst = my_dma.my_dma_class()
        # PIO(0).irq(self.stop)

    def set_frame_size(self, x_res, y_res, bpp):
        test_array = array('B')
        #byte_size = self.dma_inst.BytesPerItem(test_array)
        byte_size = 1
        bit_size = byte_size * 8
        line_number_bytes = 4
        line_number_elements = line_number_bytes * y_res * bit_size
        elements = ceil(((x_res*y_res*bpp)+line_number_elements)/bit_size)
        # self.image_array = array('B', (0 for _ in range(elements)))
        self.image_array = b'\0' * elements

    def get_frame(self, x_res, y_res, bits, freq=None, base_pin=None, jmp_pin=None):
        if(not(freq == None)):
            self.sm_freq = freq
        if(not(base_pin == None)):
            self.base_pin = base_pin
        if(not(jmp_pin == None)):
            self.jmp_pin = jmp_pin
        # self.sm_inst = StateMachine(self.sm_id, hm01b0_run, freq=self.sm_freq, in_base=self.base_pin)
        self.sm_inst = StateMachine(self.sm_id, hm01b0_get_frame_with_lines, freq=self.sm_freq, in_base=self.base_pin, jmp_pin=self.hsync_pin)
        #self.sm_inst = StateMachine(self.sm_id, full_frame_toggle_test, freq=self.sm_freq, in_base=self.base_pin)
        #self.sm_inst = StateMachine(self.sm_id, hm01b0_get_frame, freq=self.sm_freq, in_base=self.base_pin, jmp_pin=self.jmp_pin)
        if(self.image_array == None):
            self.set_frame_size(x_res, y_res, bits)
        self.dma_inst.configure_dma(self.image_array, self.sm_id)
        while(self.sm_inst.rx_fifo() > 0):
            self.sm_inst.get()
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            pass
        self.dma_inst.start_dma_transfer()
        self.sm_inst.active(1)
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            pass
        self.sm_inst.active(0)
        self.sm_inst.exec("push()")

    def get_line_count(self, x_res, y_res, bits, freq=None, base_pin=None, jmp_pin=None):
        if(not(freq == None)):
            self.sm_freq = freq
        if(not(base_pin == None)):
            self.base_pin = base_pin
        if(not(jmp_pin == None)):
            self.jmp_pin = jmp_pin
        self.sm_inst = StateMachine(self.sm_id, hm01b0_get_line_count, freq=self.sm_freq, in_base=self.base_pin, jmp_pin=self.jmp_pin)
        self.set_frame_size(x_res, y_res, bits)
        while(self.sm_inst.rx_fifo() > 0):
            self.sm_inst.get()
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            pass
        self.sm_inst.active(1)
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            while(self.sm_inst.rx_fifo() > 0):
                line_count = self.sm_inst.get()
                print(line_count)
        self.sm_inst.active(0)

    def get_pixel_count(self, x_res, y_res, bits, freq=None, base_pin=None, jmp_pin=None):
        if(not(freq == None)):
            self.sm_freq = freq
        if(not(base_pin == None)):
            self.base_pin = base_pin
        if(not(jmp_pin == None)):
            self.jmp_pin = jmp_pin
        self.sm_inst = StateMachine(self.sm_id, hm01b0_get_pixel_count, freq=self.sm_freq, in_base=self.base_pin, jmp_pin=self.jmp_pin)
        self.set_frame_size(x_res, y_res, bits)
        while(self.sm_inst.rx_fifo() > 0):
            self.sm_inst.get()
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            pass
        self.sm_inst.active(1)
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            while(self.sm_inst.rx_fifo() > 0):
                pixel_count = self.sm_inst.get()
                print(pixel_count)
        self.sm_inst.active(0)

    def get_pixel_line_count(self, x_res, y_res, bits, freq=None, base_pin=None, jmp_pin=None, side_pin=None):
        if(not(freq == None)):
            self.sm_freq = freq
        if(not(base_pin == None)):
            self.base_pin = base_pin
        if(not(jmp_pin == None)):
            self.jmp_pin = jmp_pin
        self.sm_inst = StateMachine(self.sm_id, hm01b0_get_pixel_line_count, freq=self.sm_freq, in_base=self.base_pin, jmp_pin=self.jmp_pin, sideset_base=side_pin)
        self.set_frame_size(x_res, y_res, bits)
        while(self.sm_inst.rx_fifo() > 0):
            self.sm_inst.get()
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            pass
        self.sm_inst.active(1)
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            while(self.sm_inst.rx_fifo() > 0):
                counts = self.sm_inst.get()
                print(counts)
        self.sm_inst.active(0)
    
    def get_total_count(self, x_res, y_res, bits, freq=None, base_pin=None, jmp_pin=None, side_pin=None):
        if(not(freq == None)):
            self.sm_freq = freq
        if(not(base_pin == None)):
            self.base_pin = base_pin
        if(not(jmp_pin == None)):
            self.jmp_pin = jmp_pin
        self.sm_inst = StateMachine(self.sm_id, hm01b0_get_total_count, freq=self.sm_freq, in_base=self.base_pin, jmp_pin=self.jmp_pin, sideset_base=side_pin)
        self.set_frame_size(x_res, y_res, bits)
        while(self.sm_inst.rx_fifo() > 0):
            self.sm_inst.get()
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            pass
        self.sm_inst.active(1)
        while(self.vsync_pin.value() == 0):
            pass
        while(self.vsync_pin.value() == 1):
            pass
        self.sm_inst.exec("in_(x, 32)")
        self.sm_inst.active(0)
        while(self.sm_inst.rx_fifo() > 0):
                total_count = self.sm_inst.get()
                print(total_count)

    def start(self):
        # drain fifo if not empty
        while(self.sm_inst.rx_fifo() > 0):
            self.sm_inst.get()
        self.processing_frame = 1
        print("pio active")
        self.sm_inst.active(1)
        self.dma_inst.start_dma_transfer()

    def stop(self, value):
        print("Frame irq triggered!")
        self.frame_done = 1
        self.processing_frame = 0
        self.sm_inst.active(0)

    def capture_frame(self):
        print("starting frame")
        self.start()
        print("waiting for frame done")
        self.wait_frame_done()
        
        while(self.processing_frame):
            pix_data = bytearray()
            if(self.sm_inst.rx_fifo() > 0):
                print("got data")
                pix_data.append(self.sm_inst.get() & 0xff)
            else:
                print("no data")
        while(self.sm_inst.rx_fifo() > 0):
            print("finish data")
            pix_data.append(self.sm_inst.get() & 0xff)
        self.frame_done = 0
        return pix_data

    def wait_frame_done(self):
        while(not self.frame_done):
            pass
        self.frame_done = 0

    def get_frame_data(self):
        pix_data = bytearray()
        while(self.sm_inst.rx_fifo() > 0):
            pix_data.append(self.sm_inst.get() & 0xff)
        return pix_data

hm01b0_regs_init_324x324_serial = [
    (0x0100, 0x00), # set to standby mode
    (0x0101, 0x01), # set to flip image vertical
    (0x0103, 0x00), # sw reset off
    #(0x0104, 0x01), # group param hold...? idk what this is. maybe holds registers until all applied?
    (0x0104, 0x00), # group param hold...? idk what this is. maybe holds registers until all applied?
    (0x0340, 0x02), # v res top       #017A bad # 0232 good
    (0x0341, 0x32), # v res bottom
    (0x0342, 0x0A), # h res top       #0177 bad # 0172
    (0x0343, 0x50), # h res bottom
    (0x0350, 0x7F), # not defined in spec?
    (0x0383, 0x01), # x bining
    (0x0387, 0x01), # y bining
    (0x0390, 0x00), # bining mode
    # (0x0383, 0x03), # x 1/4 bining
    # (0x0387, 0x03), # y 1/4 bining
    # (0x0390, 0x03), # mode 1/4 binning
    # (0x0601, 0x00), # test pattern select
    # (0x1000, 0x43), # black level config
    # (0x1001, 0x40), # idk
    # (0x1002, 0x32), # idk
    # (0x1003, 0x08), # black level control target value
    # (0x1006, 0x01), # bli en
    # (0x1007, 0x08), # blc2 target set to same as blc target
    (0x1008, 0x00), # dead pixel correction control
    # (0x1009, 0xA0), # idk
    # (0x100A, 0x60), # idk
    (0x100B, 0x90), # single hot pixel thresh
    (0x100C, 0x40), # single cold pixel thresh
    (0x1012, 0x01), # vsync,hsync and pixel shift (idk what this does...) 
    #{0x1012, 0x03), # another option in defaults with bining...
    # (0x2000, 0x07), # motion detection I think
    # (0x2003, 0x00), # motion detection I think
    # (0x2004, 0x1C), # motion detection I think
    # (0x2007, 0x00), # motion detection I think
    # (0x2008, 0x58), # motion detection I think
    # (0x200B, 0x00), # motion detection I think
    # (0x200C, 0x7A), # motion detection I think
    # (0x200F, 0x00), # motion detection I think
    # (0x2010, 0xB8), # motion detection I think
    # (0x2013, 0x00), # motion detection I think
    # (0x2014, 0x58), # motion detection I think
    # (0x2017, 0x00), # motion detection I think
    # (0x2018, 0x9B), # motion detection I think
    # (0x2100, 0x01), # auto exposure stuff
    # (0x2101, 0x5F), # auto exposure stuff
    # (0x2102, 0x0A), # auto exposure stuff
    # (0x2103, 0x03), # auto exposure stuff
    # (0x2104, 0x05), # auto exposure stuff
    # (0x2105, 0x02), # auto exposure stuff
    # (0x2106, 0x14), # auto exposure stuff
    # (0x2107, 0x02), # auto exposure stuff
    # (0x2108, 0x03), # auto exposure stuff
    # (0x2109, 0x03), # auto exposure stuff
    # (0x210A, 0x00), # auto exposure stuff
    # (0x210B, 0x80), # auto exposure stuff
    # (0x210C, 0x40), # auto exposure stuff
    # (0x210D, 0x20), # auto exposure stuff
    # (0x210E, 0x03), # auto exposure stuff
    # (0x210F, 0x00), # auto exposure stuff
    # (0x2110, 0x85), # auto exposure stuff
    # (0x2111, 0x00), # auto exposure stuff
    # (0x2112, 0xA0), # auto exposure stuff
    (0x2150, 0x02), # 0x03 # motion detection stuff
    (0x3010, 0x00), # sensor timing - qvga enable on bit 0
    (0x3011, 0x70), # six bit mode enable bit 0 is enable
    (0x3022, 0x01), # advance vsync field
    # (0x3044, 0x0A), # idk
    # (0x3045, 0x00), # idk
    # (0x3047, 0x0A), # idk
    # (0x3050, 0xC0), # idk
    # (0x3051, 0x42), # idk
    # (0x3052, 0x50), # idk
    # (0x3053, 0x00), # idk
    # (0x3054, 0x03), # idk
    # (0x3055, 0xF7), # idk
    # (0x3056, 0xF8), # idk
    # (0x3057, 0x29), # idk
    # (0x3058, 0x1F), # idk
    # (0x3059, 0x1E), # ... something?
    # (0x3059, 0x02), # bit control - 5 : serial enable, 6: 4 bit enable
    (0x3059, 0x22), # bit control - 5 : serial enable, 6: 4 bit enable
    # (0x3060, 0x3A), # osc clk div - 4: msb en, 5: gated clk en
    (0x3060, 0x28), # osc clk div - 4: msb en, 5: gated clk en
    #(0x3061, 0x0f), # pclk0 drive strength
    (0x3062, 0x0F), # pclk0 drive strength
    (0x3064, 0x00), # trigger sync mode enable
    (0x3065, 0x04), # output pin status control
    (0x3067, 0x00),
    (0x0100, 0x01) # set to streaming mode (enable)
]

hm0360_regs_init_768_532_serial = [
    (0x0100, 0x00), # set to standby mode
    (0x0100, 0x01) # set to streaming mode (enable)
]