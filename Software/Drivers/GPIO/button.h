#ifndef __BUTTON_H
#define __BUTTON_H

#include <system.h>
#include <generated/csr.h>

#define MODE_EDGE 0x00
#define MODE_CHANGE 0x01
#define EDGE_RISING 0x00
#define EDGE_FALLING 0x01

void ButtonInitInterrupt(uint8_t mode, uint8_t edge);
void ButtonEnableInterrupt(void);
void ButtonDisableInterrupt(void);
void ButtonClearPendingInterrupt(void);

#endif /* __BUTTON_H */