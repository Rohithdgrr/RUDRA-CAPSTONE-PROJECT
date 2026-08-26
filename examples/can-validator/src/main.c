/* CAN Validator — CF-01 loss, CF-03 flood */
#include <stdint.h>
#include <stdbool.h>
bool retransmit_ok(uint32_t lost) { return lost < 3; }
bool flood_detected(uint32_t rate_hz) { return rate_hz < 5000; } // threshold 50Hz ideal per diagnosis
int main(void){
    while(1){
        // CAN RX
        uint32_t rate = 0; // read can1
        if (!flood_detected(rate)) { /* enter bus-off safe */ }
    }
}
