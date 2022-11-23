from array   import array
from machine import mem32
from rp2     import asm_pio, StateMachine
from time    import sleep

# code from https://forums.raspberrypi.com/viewtopic.php?t=320873

class my_dma_class:
    def __init__(self):
        self.start_mem_addr = None
        self.start_mem_data = None
        self.array_mem_addr = None
        self.dma_wr_addr = None
        self.dma_rd_addr = None
        self.dma_wr_cnt_addr = None

    def configure_dma(self, dst, smNumber, dmaChannel=0):
        DMA_BASE             = 0x50000000 + (dmaChannel * 0x40)
        self.dma_rd_addr     = DMA_BASE + 0x00
        self.dma_wr_addr     = DMA_BASE + 0x04
        self.dma_wr_cnt_addr = DMA_BASE + 0x08
        self.start_mem_addr  = DMA_BASE + 0x0C
        self.array_mem_addr  = AddressOfArray(dst)      # Where to write to
        
        PIOx_BASE            = 0x50200000 + ((smNumber >> 2) << 20)
        PIOx_RXFx            = PIOx_BASE + 0x20 + ((smNumber & 3) * 4)
        
        mem32[self.dma_rd_addr]     = PIOx_RXFx                # Where to copy from
        mem32[self.dma_wr_addr]     = self.array_mem_addr
        mem32[self.dma_wr_cnt_addr] = ItemsInArray(dst)        # Number of items to transfer

        IRQ_QUIET         = 1                        # No interrupt
        TREQ_SEL          = 0x04   # <-- Get         # Wait for PIO_RXF
        CHAIN_TO          = 0                        # Do not chain
        RING_SEL          = 0                        # No ring selected
        RING_SIZE         = 0                        # No wrapping
        INCR_READ         = 0      # <-- Get         # Do not increment read address
        INCR_WRITE        = 1                        # Increment write address
        DATA_SIZE         = self.BytesPerItem(dst) >> 1   # Data size - 0=8-bit, 1=16-bit, 2=32-bit
        HIGH_PRIORITY     = 1                        # High priority
        ENABLE            = 1                        # Enabled
        
        self.start_mem_data = (
                               (IRQ_QUIET     << 21) | # Initiate the transfer
                               (TREQ_SEL      << 15) |
                               (CHAIN_TO      << 11) |
                               (RING_SEL      << 10) |
                               (RING_SIZE     <<  9) |
                               (INCR_WRITE    <<  5) |
                               (INCR_READ     <<  4) |
                               (DATA_SIZE     <<  2) |
                               (HIGH_PRIORITY <<  1) |
                               (ENABLE        <<  0)
                            )
    
    def BytesPerItem(self, a):
        try    : return a.typesize() # See www.raspberrypi.org/forums/viewtopic.php?t=320819
        except : return 4            # No way to tell in standard MicroPython !

    def start_dma_transfer(self):
        mem32[self.start_mem_addr] = self.start_mem_data

@micropython.asm_thumb
def AddressOfArray(r0):
    nop()
    
def ItemsInArray(a):
    return len(a)
        

