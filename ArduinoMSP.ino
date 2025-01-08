#define MSP_ATTITUDE 108
#define MSP_SET_RAW_RC 200
#define MSP_RAW_GPS 106
#define MSP_WP 118
#define MSP_SET_WP 209

uint16_t rc_values[8];
long start;
bool light;


void setup() {
  pinMode(13, OUTPUT);
  start = millis();
  delay(250);
  Serial1.begin(9600);
  Serial.begin(9600);
  rc_values[0] = 1500;
  rc_values[1] = 1500;
  rc_values[2] = 885;
  rc_values[3] = 1500;
  rc_values[4] = 1500;
  rc_values[5] = 1500;
  rc_values[6] = 1500;
  rc_values[7] = 1500;
}

void loop() {
  if((millis()-start) > 1000)
  {
    if(light)
    {
      digitalWrite(13, HIGH); 
      light = false;
    }
    else
    {
      digitalWrite(13, LOW); 
      light = true;
    }
    start = millis();
  }
  uint8_t datad = 0;
  uint8_t *data = &datad;
  // commandMSP(MSP_SET_RAW_RC, rc_values, 16);
  sendMSP(MSP_RAW_GPS, 0, 0);
  readGPSData();
  // sendMSP(MSP_ATTITUDE, data, 0);
  // readAttitudeData();
}

void commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes)
{

  uint8_t checksum = 0;

  Serial1.write((byte *) "$M<", 3);
  Serial1.write(n_cbytes);
  checksum ^= (n_cbytes);
  Serial1.write(cmd);
  checksum ^= cmd;
  uint16_t cur_byte = 0;
  while(cur_byte < (n_cbytes/2))
  {
    int8_t byte1 = ((uint16_t)data[cur_byte] >> 0) & 0xFF;
    int8_t byte2 = ((uint16_t)data[cur_byte] >> 8) & 0xFF;
    Serial1.write(byte1);
    Serial1.write(byte2);
    checksum ^= byte1;
    checksum ^= byte2;
    cur_byte++;
  }
  Serial1.write(checksum);
  while(Serial1.available())
  {
    Serial1.read();
    Serial.println("clear");
  }
}

void sendMSP(uint8_t req, uint8_t *data, uint8_t n_bytes) {

    uint8_t checksum = 0;

    Serial1.write((byte *) "$M<", 3);
    Serial1.write(n_bytes);
    checksum ^= n_bytes;

    Serial1.write(req);
    checksum ^= req;

    Serial1.write(checksum);
}

void readAttitudeData() {
  delay(100);
  byte count = 0;

  int16_t rollRec;
  int16_t pitchRec;
  int16_t yawRec;

  while (Serial1.available()) {
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
  Serial.print("Roll: " + String(rollRec/10.0));
  Serial.print(" Pitch: " + String(pitchRec/10.0));
  Serial.println(" Yaw: " + String(yawRec));
}

void readGPSData()
{
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
  Serial.print("Fix: " + String(gpsFix));
  Serial.print(" NumSat: " + String(numSat));
  Serial.print(" Lat: " + String(lat/10000000.0, 5));
  Serial.print(" Lon: " + String(lon/10000000.0, 5));
  Serial.print(" GPSALT: " + String(gpsAlt));
  Serial.print(" SOG: " + String(gpsSpeed));
  Serial.println(" GPSCourse: " + String(gpsCourse/10.0));
}
