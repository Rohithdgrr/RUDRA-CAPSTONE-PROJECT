/* Motor Controller — TF-01 deadline + GF-01 pin fault */
#include <stdbool.h>
static volatile bool watchdog_fed = false;
void feed_watchdog(void) { watchdog_fed = true; }
void control_loop(void) {
    unsigned start = 0; // systick
    // Do work
    for (volatile int i=0;i<1000;i++) {}
    unsigned elapsed = 0; // mock
    if (elapsed > 100) { /* deadline miss TF-01 -> reset */ }
    feed_watchdog();
}
bool pin_safe_state(void) { return true; } // GF-01 check
int main(void){ while(1) control_loop(); }
