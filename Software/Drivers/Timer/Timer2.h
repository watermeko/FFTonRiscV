#ifndef __TIMER2_H
#define __TIMER2_H

#include <system.h>
#include <generated/csr.h>

void Timer2_busy_wait(unsigned int ms);
void Timer2_busy_wait_us(unsigned int us);

#endif /* __TIMER2_H */