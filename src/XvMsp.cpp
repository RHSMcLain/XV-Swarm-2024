#include <Arduino.h>
#include "XvMsp.h"

void XvMsp::begin(int speed){
    Serial1.begin(speed);
}

void XvMsp::commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes){

  uint8_t checksum = 0;

  Serial1.write((byte *) "$M<", 3);
  Serial1.write(n_cbytes);
  checksum ^= (n_cbytes);

  Serial1.write(cmd);
  checksum ^= cmd;

  uint16_t cur_byte = 0;
  while(cur_byte < (n_cbytes/2)){
    int8_t byte1 = ((uint16_t)data[cur_byte] >> 0) & 0xFF;
    int8_t byte2 = ((uint16_t)data[cur_byte] >> 8) & 0xFF;
    Serial1.write(byte1);
    Serial1.write(byte2);
    checksum ^= byte1;
    checksum ^= byte2;
    cur_byte++;
  }
  Serial1.write(checksum);
  while(Serial1.available()){
    Serial1.read();
  }
}

void XvMsp::sendMSP(uint8_t req, uint8_t *data, uint8_t n_bytes){

  uint8_t checksum = 0;

  Serial1.write((byte *) "$M<", 3);
  Serial1.write(n_bytes);
  checksum ^= n_bytes;

  Serial1.write(req);
  checksum ^= req;

  Serial1.write(checksum);
}

void XvMsp::readAttitudeData(){
  delay(100);
  byte count = 0;

  int16_t rollRec;
  int16_t pitchRec;
  int16_t yawRec;

  while (Serial1.available()){
    count += 1;
    byte first;
    byte second;
    switch (count) {
      //first five bytes are header-type informatin, so start at 6
    case 1 ... 5:
      Serial1.read();
      break;
    case 6:
      first = Serial1.read();
      second = Serial1.read();
      rollRec = second;
      rollRec <<= 8;
      rollRec += first;
      break;
    case 7:
      first = Serial1.read();
      second = Serial1.read();
      pitchRec = second;
      pitchRec <<= 8;
      pitchRec += first;
      break;  
    case 8:
      first = Serial1.read();
      second = Serial1.read();
      yawRec = second;
      yawRec <<= 8;
      yawRec += first;
      break;
    case 9:
      Serial1.read();
      break;
    }
  }
  msp_attitude.roll = rollRec;
  msp_attitude.pitch = pitchRec;
  msp_attitude.yaw = yawRec;
}

void XvMsp::readGPSData(){
  delay(100);
  byte count = 0;

  uint8_t gpsFix;
  uint8_t numSat;
  uint32_t lat;
  uint32_t lon;
  uint16_t gpsAlt;
  uint16_t gpsSpeed;
  uint16_t gpsCourse;

  while (Serial1.available()) {
    count += 1;
    byte first;
    byte second;
    byte third;
    byte fourth;
    switch (count) {
      //first five bytes are header-type informatin, so start at 6
    case 1 ... 5:
      Serial1.read();
      break;
    case 6: //Fix, 1 is yes, 0 is no
      gpsFix = Serial1.read();
      break;
    case 7: //Number of satellites
      numSat = Serial1.read();
      break;  
    case 8: //Combine latitude bytes
      first = Serial1.read();
      second = Serial1.read();
      third = Serial1.read();
      fourth = Serial1.read();
      lat = fourth;
      lat <<= 8;
      lat += third;
      lat <<= 8;
      lat += second;
      lat <<= 8;
      lat += first;
      break;
    case 9: //Combine longitude bytes
      first = Serial1.read();
      second = Serial1.read();
      third = Serial1.read();
      fourth = Serial1.read();
      lon = fourth;
      lon <<= 8;
      lon += third;
      lon <<= 8;
      lon += second;
      lon <<= 8;
      lon += first;
      break;
    case 10: //Altitude in meters
      first = Serial1.read();
      second = Serial1.read();
      gpsAlt = second;
      gpsAlt <<= 8;
      gpsAlt += first;
      break;
    case 11: //Speed in cm/s
      first = Serial1.read();
      second = Serial1.read();
      gpsSpeed = second;
      gpsSpeed <<= 8;
      gpsSpeed += first;
      break;
    case 12: //Degrees times 10
      first = Serial1.read();
      second = Serial1.read();
      gpsCourse = second;
      gpsCourse <<= 8;
      gpsCourse += first;
      break;
    case 13:
      Serial1.read();
      break;
    }
  }
  msp_raw_gps.gpsFix = gpsFix;
  msp_raw_gps.numSat = numSat;
  msp_raw_gps.lat = lat;
  msp_raw_gps.lon = lon;
  msp_raw_gps.gpsAlt = gpsAlt;
  msp_raw_gps.gpsSpeed = gpsSpeed;
  msp_raw_gps.gpsCourse = gpsCourse;
}