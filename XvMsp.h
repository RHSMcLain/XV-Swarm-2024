#include <cstdint>

struct msp_attitude{
    int16_t roll;       //degrees / 10
    int16_t pitch;      //degrees / 10
    int16_t yaw;        //degrees
};