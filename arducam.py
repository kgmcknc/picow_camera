# import my_i2c

# class arducam_class:
#     i2c_instance = my_i2c.i2c_class()
#     i2c_address = None
#     i2c_address_width = 8
#     i2c_freq = None
#     scl_pin = None
#     sda_pin = None
#     vsync_pin = None
#     hsync_pin = None
#     pix_clk_pin = None
#     data_pin = None

#     def __init__(self, i2c_address=None, i2c_address_width=8, i2c_freq=None, scl_pin=None, sda_pin=None):
#         self.i2c_address = i2c_address
#         self.i2c_address_width = i2c_address_width
#         self.i2c_freq = i2c_freq
#         self.scl_pin = scl_pin
#         self.sda_pin = sda_pin

#     def initiate_i2c(self):
#         self.i2c_instance.i2c_address = self.i2c_address
#         self.i2c_instance.i2c_address_width = self.i2c_address_width
#         self.i2c_instance.scl_pin = self.scl_pin
#         self.i2c_instance.sda_pin = self.sda_pin
#         self.i2c_instance.i2c_freq = self.i2c_freq
#         self.i2c_instance.initiate_i2c()


# void arducam_init(struct arducam_config *config){
# gpio_set_function(config->pin_xclk, GPIO_FUNC_PWM);
# uint slice_num = pwm_gpio_to_slice_num(config->pin_xclk);
# // 6 cycles (0 to 5), 125 MHz / 6 = ~20.83 MHz wrap rate
# pwm_set_wrap(slice_num, 9);
# pwm_set_gpio_level(config->pin_xclk, 3);
# pwm_set_enabled(slice_num, true);
# #ifndef SOFTWARE_I2C
# // SCCB I2C @ 100 kHz
# gpio_set_function(config->pin_sioc, GPIO_FUNC_I2C);
# gpio_set_function(config->pin_siod, GPIO_FUNC_I2C);
# i2c_init(config->sccb, 100 * 1000);
# #else
# gpio_init(config->pin_sioc);
# gpio_init(config->pin_siod);
# gpio_set_dir(config->pin_sioc, GPIO_OUT);
# gpio_set_dir(config->pin_siod, GPIO_OUT);
# #endif

# // Initialise reset pin
# gpio_init(config->pin_resetb);
# gpio_set_dir(config->pin_resetb, GPIO_OUT);

# // Reset camera, and give it some time to wake back up
# gpio_put(config->pin_resetb, 0);
# sleep_ms(100);
# gpio_put(config->pin_resetb, 1);
# sleep_ms(100);
# // Initialise the camera itself over SCCB
# arducam_regs_write(config, hm01b0_324x244);
# // Enable image RX PIO
# uint offset = pio_add_program(config->pio, &image_program);
# image_program_init(config->pio, config->pio_sm, offset, config->pin_y2_pio_base);
# }

# void arducam_capture_frame(struct arducam_config *config) {
# dma_channel_config c = dma_channel_get_default_config(config->dma_channel);
# channel_config_set_read_increment(&c, false);
# channel_config_set_write_increment(&c, true);
# channel_config_set_dreq(&c, pio_get_dreq(config->pio, config->pio_sm, false));
# channel_config_set_transfer_data_size(&c, DMA_SIZE_8);

# dma_channel_configure(
# config->dma_channel, &c,
# config->image_buf,
# &config->pio->rxf[config->pio_sm],
# config->image_buf_size,
# false
# );
# // Wait for vsync rising edge to start frame
# while (gpio_get(config->pin_vsync) == true);
# while (gpio_get(config->pin_vsync) == false);

# dma_channel_start(config->dma_channel);
# pio_sm_set_enabled(config->pio, config->pio_sm, true);
# dma_channel_wait_for_finish_blocking(config->dma_channel);
# pio_sm_set_enabled(config->pio, config->pio_sm, false);
# }
