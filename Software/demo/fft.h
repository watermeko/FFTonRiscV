#ifndef FFT_H
#define FFT_H

#include <math.h>

typedef struct {
    float real;
    float imag;
} Complex;

Complex complex_mul(Complex a, Complex b);
Complex complex_add(Complex a, Complex b);
Complex complex_sub(Complex a, Complex b);

void fft(Complex *x, int N);

#endif
