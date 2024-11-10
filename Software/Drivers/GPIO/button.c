#include "button.h"

void ButtonInitInterrupt(uint8_t mode, uint8_t edge)
{
	button_mode_write(mode);
    button_edge_write(edge);
	ButtonClearPendingInterrupt();
}

void ButtonEnableInterrupt(void)
{
    ButtonClearPendingInterrupt();
    button_ev_enable_write(0x1);
}

void ButtonDisableInterrupt(void)
{
    button_ev_enable_write(0x0);
    ButtonClearPendingInterrupt();
}

void ButtonClearPendingInterrupt(void)
{
    button_ev_pending_write(0x01);
}
