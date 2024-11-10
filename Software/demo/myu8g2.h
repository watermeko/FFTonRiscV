#ifndef __MYU8G2_H
#define __MYU8G2_H

#include "csrc/u8g2.h"
#include <generated/csr.h>
#include "libbase/i2c.h"


#define u8         unsigned char 
#define MAX_LEN    128
#define OLED_ADDRESS  0x3c
#define OLED_CMD   0x00  
#define OLED_DATA  0x40  

uint8_t u8x8_byte_hw_i2c(u8x8_t *u8x8, uint8_t msg, uint8_t arg_int, void *arg_ptr);
uint8_t u8x8_gpio_and_delay(u8x8_t *u8x8, uint8_t msg, uint8_t arg_int, void *arg_ptr);
void u8g2Init(u8g2_t *u8g2);
void draw(u8g2_t *u8g2);
void testDrawPixelToFillScreen(u8g2_t *u8g2);
void drawDonut(u8g2_t *u8g2);

#endif

