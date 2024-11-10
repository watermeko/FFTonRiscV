#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/console.h>
#include <generated/csr.h>
#include "myu8g2.h"
#include "Drivers/Timer/Timer1.h"
#include "Drivers/Timer/Timer2.h"
#include "Drivers/GPIO/button.h"

#include "fft.h"

#define WITH_CXX
#define N 256
#define OLED_H 64
#define OLED_W 128

static void timer_adc_start(void);
static void oledtest_cmd(void);
void isr_handler(void);
void OLEDInit(void);
void calc_fft(void);
void PrintFloat(float value);
uint16_t reverse_bits_12(uint16_t data);

int adcvals[N];
int i=0;
bool flag = false;
u8g2_t u8g2;

void isr_handler(void)
{	
	unsigned int irqs = irq_pending() & irq_getmask();
	if(irqs & (1 << TIMER1_INTERRUPT))
	{
		Timer1ClearPendingInterrupt();

		adc_clk_out_write(~adc_clk_out_read());
		if(i<N){
			adcvals[i] = adc_data_in_read();
			i++;
		}else{
			Timer1DisableInterrupt();
			printf("flag");
			flag = true;
		}
	}
	else if(irqs & (1 << BUTTON_INTERRUPT))
	{
		ButtonClearPendingInterrupt();
		timer_adc_start();
	}
	else
	{
		printf("Unexpected IRQ: %x\n", irqs);
	}
}

void calc_fft(void){
	Complex x[N];
	int j,max=1;
	for(j=0;j<N;j++){
		x[j].real= reverse_bits_12((adcvals[j]) & 0xFFF)*5.0f/4096;
		x[j].imag = 0;
	}
	fft(x,N);
	float magnitudes[N/2];
	for (j = 0; j < N/2; j++) {
		magnitudes[j] = sqrtf(x[j].imag*x[j].imag+x[j].real*x[j].real)/N;
		if(j!=0&&(magnitudes[j]>magnitudes[max])){
			max = j;
		}
		printf("output[%d] = ", j);
		PrintFloat(magnitudes[j]);
		printf("\n");
	}
	printf("max=%d",max);


    float lengths[5] = {0};
    for(int j = 1; j < N / 2; j++){
        if (j <= 10) {
            lengths[0] += magnitudes[j];
        } else if (j <= 20) {
            lengths[1] += magnitudes[j];
        } else if (j <= 30) {
            lengths[2] += magnitudes[j];
        } else if (j <= 40) {
            lengths[3] += magnitudes[j];
        } else if (j <= 50) {
            lengths[4] += magnitudes[j];
        }
    }

    float max_length = 0;
    for (int k = 0; k < 5; k++) {
        if (lengths[k] > max_length) {
            max_length = lengths[k];
        }
    }
    float scale_factor = (OLED_H - 10) / max_length;

                     
    u8g2_ClearBuffer(&u8g2);               
    u8g2_SetFont(&u8g2, u8g2_font_squeezed_b7_tr);  

    for(int k = 0; k < 5; k++){
        char str[8];
        sprintf(str, "%d", 2 * k);        
        u8g2_DrawUTF8(&u8g2, (OLED_W / 6) * k, OLED_H, str); 
        int display_length = (int)(lengths[k] * scale_factor);
        u8g2_DrawBox(&u8g2, (OLED_W / 6) * k + 10, OLED_H - display_length, 7, display_length);
    }
    u8g2_DrawUTF8(&u8g2, (OLED_W / 6) * 5, OLED_H, "KHz");  
    u8g2_SendBuffer(&u8g2);                 
}

uint16_t reverse_bits_12(uint16_t data) {
    uint16_t reversed = 0;
    for (int i = 0; i < 12; i++) {
        reversed <<= 1;               
        reversed |= (data & 1); 
        data >>= 1;                  
    }
    return reversed;
}

void OLEDInit(void){
    u8g2Init(&u8g2);
	u8g2_ClearBuffer(&u8g2);               
    u8g2_SetFont(&u8g2, u8g2_font_inb24_mf); 
	u8g2_DrawUTF8(&u8g2,5,30,"READY");  
	u8g2_SendBuffer(&u8g2);     
}

void PrintFloat(float value){

int tmp,tmp1,tmp2,tmp3,tmp4,tmp5,tmp6;

tmp = (int)value;

tmp1=(int)((value-tmp)*10)%10;

tmp2=(int)((value-tmp)*100)%10;

tmp3=(int)((value-tmp)*1000)%10;

tmp4=(int)((value-tmp)*10000)%10;

tmp5=(int)((value-tmp)*100000)%10;

tmp6=(int)((value-tmp)*1000000)%10;

printf("%d.%d%d%d%d%d%d",tmp,tmp1,tmp2,tmp3,tmp4,tmp5,tmp6);

}

static char *readstr(void)
{
	char c[2];
	static char s[64];
	static int ptr = 0;

	if(readchar_nonblock()) {
		c[0] = getchar();
		c[1] = 0;
		switch(c[0]) {
			case 0x7f:
			case 0x08:
				if(ptr > 0) {
					ptr--;
					fputs("\x08 \x08", stdout);
				}
				break;
			case 0x07:
				break;
			case '\r':
			case '\n':
				s[ptr] = 0x00;
				fputs("\n", stdout);
				ptr = 0;
				return s;
			default:
				if(ptr >= (sizeof(s) - 1))
					break;
				fputs(c, stdout);
				s[ptr] = c[0];
				ptr++;
				break;
		}
	}

	return NULL;
}

static char *get_token(char **str)
{
	char *c, *d;

	c = (char *)strchr(*str, ' ');
	if(c == NULL) {
		d = *str;
		*str = *str+strlen(*str);
		return d;
	}
	*c = 0;
	d = *str;
	*str = c+1;
	return d;
}

static void prompt(void)
{
	printf("\e[92;1mFFTonRiscV\e[0m> ");
}

static void help(void)
{
	puts("Available commands:");
	puts("help               - Show this command");
	puts("reboot           - Reboot CPU");
	puts("adcstart        - Start ADC");
#ifdef WITH_CXX
	puts("hellocpp           - Hello C++");
#endif
}

static void reboot_cmd(void)
{
	ctrl_reset_write(1);
}

#ifdef WITH_CXX
extern void hellocpp();

static void hellocpp_cmd()
{
	printf("Hello C++ demo...\n");
	hellocpp();
}
#endif

static void timer_adc_start(void){
	printf("adc start\n");
	i=0;
	Timer1PeriodicInterrupt(1);
}

static void console_service(void)
{
	char *str;
	char *token;

	str = readstr();
	if(str == NULL) return;
	token = get_token(&str);
	if(strcmp(token, "help") == 0)
		help();
	else if(strcmp(token, "reboot") == 0)
		reboot_cmd();
	else if(strcmp(token,"adcstart")==0)
		timer_adc_start();
#ifdef WITH_CXX
	else if(strcmp(token, "hellocpp") == 0)
		hellocpp_cmd();
#endif
	prompt();
}

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
	irq_setmask(
		irq_getmask() |
		(1 << TIMER1_INTERRUPT)|
		(1 << BUTTON_INTERRUPT));
	irq_attach(TIMER1_INTERRUPT,isr_handler);
	irq_attach(BUTTON_INTERRUPT,isr_handler);
	irq_setie(1);
#endif
	uart_init();
	ButtonInitInterrupt(MODE_EDGE,EDGE_FALLING);
	ButtonEnableInterrupt();

	help();
	prompt();
	OLEDInit();

	while(1) {
		console_service();
		if(flag){
			calc_fft();
			flag = false;
		}
	}
	return 0;
}
