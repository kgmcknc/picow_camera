import rp2
from machine import Pin
import time

hm01b0_address = 0x24
hm01b0_freq = 400000
hm01b0_pix_clk_freq = 20_830_000

@rp2.asm_pio(autopush=True, fifo_join=rp2.PIO.JOIN_RX, in_shiftdir=rp2.PIO.SHIFT_LEFT, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def hm01b0_get_frame():
    # vsync,hsync,pix_clk,d0

    irq(clear, 0)    # clear irq if it's somehow set...
    set(y, 1)        # set initial line number to 1
    mov(y, isr)      # write line number isr
    push(noblock)           # push line number to rx_fifo
    
    wait(0, pin, 0) # wait for vsync 0 (not processing frame)
    wait(1, pin, 0) # wait for vsync being high to start frame

    label("process_frame")   # create lable for processing the frame

    label("process_line")
    wait(1, pin, 1) # wait hsync high
    wait(1, pin, 2) # wait pix clk high
    in_(pins, 4)    # get data from pins
    wait(0, pin, 2) # wait pix clk low
    jmp(pin, "process_line")
    
    #line is done
    nop()
    nop()
    nop()
    nop()

    push(noblock)      # push any leftover bits in isr
    set(y, y+1) # increment line counter
    mov(y, isr) # write line number isr
    push(noblock)      # push line number to rx_fifo

    set(x,0)
    mov(osr, pins)
    out(x, 1)

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
    base_pin = None
    sm_freq = None
    sm_id = None
    sm_inst = None
    processing_frame = 0
    frame_done = 0

    def __init__(self, sm_id=None, freq=None, base_pin=None, jmp_pin=None):
        self.base_pin = base_pin
        self.jmp_pin = jmp_pin
        self.sm_freq = freq
        self.sm_id = sm_id
        self.sm_inst = rp2.StateMachine(self.sm_id, hm01b0_get_frame, freq=self.sm_freq, in_base=self.base_pin, jmp_pin=self.jmp_pin)
        rp2.PIO(0).irq(self.stop)

    def start(self):
        # drain fifo if not empty
        while(self.sm_inst.rx_fifo() > 0):
            self.sm_inst.get()
        self.processing_frame = 1
        print("pio active")
        self.sm_inst.active(1)

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
        
        # while(self.processing_frame):
        #     pix_data = bytearray()
        #     if(self.sm_inst.rx_fifo() > 0):
        #         print("got data")
        #         pix_data.append(self.sm_inst.get() & 0xff)
        #     else:
        #         print("no data")
        # while(self.sm_inst.rx_fifo() > 0):
        #     print("finish data")
        #     pix_data.append(self.sm_inst.get() & 0xff)
        # self.frame_done = 0
        # return pix_data

    def wait_frame_done(self):
        while(not self.frame_done):
            print("waiting end")
            pass
        self.frame_done = 0

    def get_frame_data(self):
        pix_data = bytearray()
        while(self.sm_inst.rx_fifo() > 0):
            pix_data.append(self.sm_inst.get() & 0xff)
        return pix_data

hm01b0_regs_init_324x244 = [
    (0x0103, 0x00),
    (0x0100, 0x00),
    (0x1003, 0x08),
    (0x1007, 0x08),
    (0x3044, 0x0A),
    (0x3045, 0x00),
    (0x3047, 0x0A),
    (0x3050, 0xC0),
    (0x3051, 0x42),
    (0x3052, 0x50),
    (0x3053, 0x00),
    (0x3054, 0x03),
    (0x3055, 0xF7),
    (0x3056, 0xF8),
    (0x3057, 0x29),
    (0x3058, 0x1F),
    (0x3059, 0x1E),
    (0x3064, 0x00),
    (0x3065, 0x04),
    (0x1000, 0x43),
    (0x1001, 0x40),
    (0x1002, 0x32),
    (0x0350, 0x7F),
    (0x1006, 0x01),
    (0x1008, 0x00),
    (0x1009, 0xA0),
    (0x100A, 0x60),
    (0x100B, 0x90),
    (0x100C, 0x40),
    (0x3022, 0x01),
    (0x1012, 0x01),
    (0x2000, 0x07),
    (0x2003, 0x00),
    (0x2004, 0x1C),
    (0x2007, 0x00),
    (0x2008, 0x58),
    (0x200B, 0x00),
    (0x200C, 0x7A),
    (0x200F, 0x00),
    (0x2010, 0xB8),
    (0x2013, 0x00),
    (0x2014, 0x58),
    (0x2017, 0x00),
    (0x2018, 0x9B),
    (0x2100, 0x01),
    (0x2101, 0x5F),
    (0x2102, 0x0A),
    (0x2103, 0x03),
    (0x2104, 0x05),
    (0x2105, 0x02),
    (0x2106, 0x14),
    (0x2107, 0x02),
    (0x2108, 0x03),
    (0x2109, 0x03),
    (0x210A, 0x00),
    (0x210B, 0x80),
    (0x210C, 0x40),
    (0x210D, 0x20),
    (0x210E, 0x03),
    (0x210F, 0x00),
    (0x2110, 0x85),
    (0x2111, 0x00),
    (0x2112, 0xA0),
    (0x2150, 0x03),
    (0x0340, 0x01),
    (0x0341, 0x7A),
    (0x0342, 0x01),
    (0x0343, 0x77),
    (0x3010, 0x00),#bit[0] 1 enable QVGA
    (0x0383, 0x01),
    (0x0387, 0x01),
    (0x0390, 0x00),
    (0x3011, 0x70),
    (0x3059, 0x22),
    (0x3060, 0x30),
    (0x0101, 0x01),
    (0x0104, 0x01),
    #{0x0390, 0x03),  #1/4 binning
    #{0x0383, 0x03),
    #{0x0387, 0x03),
    #{0x1012, 0x03),
    (0x0100, 0x01)
]
