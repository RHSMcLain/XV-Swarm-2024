#include <Arduino.h>

#define MSP_ATTITUDE 108
#define MSP_SET_RAW_RC 200
#define MSP_RAW_GPS 106
#define MSP_WP 118
#define MSP_SET_WP 209 

struct msp_attitude_h{
    int16_t roll;       //degrees / 10
    int16_t pitch;      //degrees / 10
    int16_t yaw;        //degrees
};

struct msp_raw_gps_h{
    uint8_t gpsFix;     //0 or 1
    uint8_t numSat;
    uint32_t lat;       //degrees / 10,000,000
    uint32_t lon;       //degrees / 10,000,000
    uint16_t gpsAlt;    //meters
    uint16_t gpsSpeed;  //cm / seconds
    uint16_t gpsCourse; //degrees
};

class XvMsp{
    public:
        void begin();

        void commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes);

        void sendMSP(uint8_t req, uint8_t *data, uint8_t n_bytes);

        void readAttitudeData();

        void readGPSData();

        msp_attitude_h msp_attitude;
        msp_raw_gps_h msp_raw_gps;
    private:
};