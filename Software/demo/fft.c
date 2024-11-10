#include "fft.h"

Complex complex_mul(Complex a, Complex b) {
    Complex result;
    result.real = a.real * b.real - a.imag * b.imag;
    result.imag = a.real * b.imag + a.imag * b.real;
    return result;
}

Complex complex_add(Complex a, Complex b) {
    Complex result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}

Complex complex_sub(Complex a, Complex b) {
    Complex result;
    result.real = a.real - b.real;
    result.imag = a.imag - b.imag;
    return result;
}

int int_log2(int N) {
    int log2 = 0;
    while (N >>= 1) ++log2;
    return log2;
}

void fft(Complex *x, int N) {
    int n = N;
    for (int i = 1, j = 0; i < N; i++) {
        int bit = n >> 1;
        while (j >= bit) {
            j -= bit;
            bit >>= 1;
        }
        j += bit;

        if (i < j) {
            Complex temp = x[i];
            x[i] = x[j];
            x[j] = temp;
        }
    }

    for (int s = 1; s <= int_log2(N); s++) {
        float PI = 3.14159265358979f;
        int m = 1 << s;
        float theta = -2 * PI / m;
        Complex wm = {cosf(theta), sinf(theta)};
        for (int k = 0; k < N; k += m) {
            Complex w = {1.0f, 0.0f};
            for (int j = 0; j < m / 2; j++) {
                Complex t = complex_mul(w, x[k + j + m / 2]);
                Complex u = x[k + j];
                x[k + j] = complex_add(u, t);
                x[k + j + m / 2] = complex_sub(u, t);
                w = complex_mul(w, wm);
            }
        }
    }
}
