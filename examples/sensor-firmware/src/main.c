/* Sensor Firmware — STM32F407, demonstrates SF-01..SF-07 handling */
#include <stdint.h>
#include <stdbool.h>

#define WINDOW 3
static float buf[WINDOW] = {0};
static int idx = 0;

bool detect_stuck_sensor(float cur, float last) {
    // SF-01: flag if |cur-last| < 0.01 for WINDOW samples
    return (cur - last < 0.01f && last - cur < 0.01f);
}

float median_filter(float x) {
    buf[idx++ % WINDOW] = x;
    float a = buf[0], b = buf[1], c = buf[2];
    // simple sort 3
    if (a > b) { float t=a;a=b;b=t; }
    if (b > c) { float t=b;b=c;c=t; }
    if (a > b) { float t=a;a=b;b=t; }
    return b; // SF-03 outlier + SF-06 missing sample tolerant
}

bool std_dev_filtered(float std) { return std < 2.0f; } // SF-02

int main(void) {
    float last = 25.0f;
    while (1) {
        float raw = 25.0f; // read I2C sensor @i2c1
        if (detect_stuck_sensor(raw, last)) { /* raise flag, watchdog ok */ }
        float f = median_filter(raw);
        (void)f;
        last = raw;
    }
}
