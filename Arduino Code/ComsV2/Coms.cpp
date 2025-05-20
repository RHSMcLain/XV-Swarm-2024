#include "Coms.h"

void FcComs::commandMSP(uint8_t cmd, uint16_t data[], uint8_t n_cbytes){

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

void FcComs::reqMSP(uint8_t req, uint8_t *data, uint8_t n_bytes){

  uint8_t checksum = 0;

  Serial1.write((byte *) "$M<", 3);
  
  Serial1.write(n_bytes);
  checksum ^= n_bytes;

  Serial1.write(req);
  checksum ^= req;

  Serial1.write(checksum);
}

void FcComs::sendWaypoints(Waypoint wp[],uint8_t size){
  // uint8_t size = sizeof(wp);
  for(uint8_t i = 1; i <= size; i++){
    uint8_t checksum = 0;
    uint8_t n_bytes = 21;

    Serial1.write((byte *) "$M<", 3);
    Serial1.write(n_bytes);
    checksum ^= n_bytes;

    Serial1.write(MSP_SET_WP);
    checksum ^= MSP_SET_WP;
    //id
    Serial1.write(i);
    checksum ^= i;
    //action
    Serial1.write(wp[i].action);
    checksum ^= wp[i].action;
    //lat creates array of each byte
    uint8_t lat[4] = {
      ((uint32_t)wp[i].lat >> 0) & 0xFF, 
      ((uint32_t)wp[i].lat >> 8) & 0xFF, 
      ((uint32_t)wp[i].lat >> 16) & 0xFF, 
      ((uint32_t)wp[i].lat >> 24) & 0xFF
    };
    //for writes and checksums each byte
    for(uint8_t x = 0; x < 4; x++){
      Serial1.write(lat[x]);
      // Serial.println(lat[x]);
      checksum ^= lat[x];
    }
    //lon
    uint8_t lon[4] = {
      ((uint32_t)wp[i].lon >> 0) & 0xFF,
      ((uint32_t)wp[i].lon >> 8) & 0xFF,
      ((uint32_t)wp[i].lon >> 16) & 0xFF,
      ((uint32_t)wp[i].lon >> 24) & 0xFF
    };
    for(uint8_t x = 0; x < 4; x++){
      Serial1.write(lon[x]);
      // Serial.println(lon[x]);
      checksum ^= lon[x];
    }
    //alt
    uint8_t alt[4] = {
      ((uint32_t)wp[i].alt >> 0) & 0xFF,
      ((uint32_t)wp[i].alt >> 8) & 0xFF,
      ((uint32_t)wp[i].alt >> 16) & 0xFF,
      ((uint32_t)wp[i].alt >> 24) & 0xFF
    };
    for(uint8_t x = 0; x < 4; x++){
      Serial1.write(alt[x]);
      // Serial.println(alt[x]);
      checksum ^= alt[x];
    }
    //p1
    uint8_t p1[2] = {
      ((uint16_t)wp[i].p1 >> 0) & 0xFF,
      ((uint16_t)wp[i].p1 >> 8) & 0xFF
    };
    for(uint8_t x = 0; x < 2; x++){
      Serial1.write(p1[x]);
      // Serial.println(p1[x]);
      checksum ^= p1[x];
    }
    //p2
    uint8_t p2[2] = {
      ((uint16_t)wp[i].p2 >> 0) & 0xFF,
      ((uint16_t)wp[i].p2 >> 8) & 0xFF
    };
    for(uint8_t x = 0; x < 2; x++){
      Serial1.write(p2[x]);
      // Serial.println(p2[x]);
      checksum ^= p2[x];
    }
    //p3
    uint8_t p3[2] = {
      ((uint16_t)wp[i].p3 >> 0) & 0xFF,
      ((uint16_t)wp[i].p3 >> 8) & 0xFF
    };
    for(uint8_t x = 0; x < 2; x++){
      Serial1.write(p3[x]);
      // Serial.println(p3[x]);
      checksum ^= p3[x];
    }
    //flag
    Serial1.write(wp[i].flag);
    // Serial.println(wp[i].flag);
    Serial.println(i);
    checksum ^= wp[i].flag;
    Serial1.write(checksum);
    while(Serial1.available()){
      Serial1.read();
    }
    // if(wp[i].flag == NAV_WP_FLAG_LAST){
    //   return;
    // }
    delay(50);
  }
}

void FcComs::readAttitudeData(){
  byte count = 0;
  reqMSP(MSP_ATTITUDE, 0, 0);
  delay(10);
  int16_t rollRec;
  int16_t pitchRec;
  int16_t yawRec;
  uint8_t checksum = 0;

  while (Serial1.available()){
    count += 1;
    byte first;
    byte second;
    uint8_t n_bytes = 0;
    switch (count) {
      //first five bytes are header-type informatin, so start at 6
    case 1:
    case 2:
    case 3:
      Serial1.read();
      break;
    case 4:
      n_bytes = Serial1.read();
      checksum ^= n_bytes;
      Serial.println("Recived attitude bytes: " + String(n_bytes));
      break;
    case 5:
      checksum ^= Serial1.read();
      break;
    case 6:
      first = Serial1.read();
      second = Serial1.read();
      checksum ^= first;
      checksum ^= second;
      rollRec = second;
      rollRec <<= 8;
      rollRec += first;
      break;
    case 7:
      first = Serial1.read();
      second = Serial1.read();
      checksum ^= first;
      checksum ^= second;
      pitchRec = second;
      pitchRec <<= 8;
      pitchRec += first;
      break;  
    case 8:
      first = Serial1.read();
      second = Serial1.read();
      checksum ^= first;
      checksum ^= second;
      yawRec = second;
      yawRec <<= 8;
      yawRec += first;
      break;
    case 9:
      if(checksum = Serial1.read()){
        Serial.println("Checksum is correct for attitude");
      }
      else{
        Serial.println("Checksum is incorrect for attitude");
      }
      break;
    }
  }
  msp_attitude.roll = rollRec;
  msp_attitude.pitch = pitchRec;
  msp_attitude.yaw = yawRec;
  Serial.print("Roll: " + String(rollRec/10.0));
  Serial.print(" Pitch: " + String(pitchRec/10.0));
  Serial.println(" Yaw: " + String(yawRec));
}

void FcComs::readGPSData(){
  byte count = 0;
  reqMSP(MSP_RAW_GPS, 0, 0);
  delay(10);
  uint8_t gpsFix;
  uint8_t numSat;
  uint32_t lat;
  uint32_t lon;
  uint16_t gpsAlt;
  uint16_t gpsSpeed;
  uint16_t gpsCourse;
  uint8_t checksum = 0;

  while (Serial1.available()) {
    count ++;
    byte first;
    byte second;
    byte third;
    byte fourth;
    uint8_t n_bytes = 0;
    switch (count) {
      //first five bytes are header-type informatin, so start at 6
    case 1:
    case 2:
    case 3:
      Serial1.read();
      break;
    case 4:
      n_bytes = Serial1.read();
      checksum ^= n_bytes;
      Serial.println("Recived gps bytes: " + String(n_bytes));
      break;
    case 5:
      checksum ^= Serial1.read();
      break;
    case 6: //Fix, 1 is yes, 0 is no
      gpsFix = Serial1.read();
      checksum ^= gpsFix;
      break;
    case 7: //Number of satellites
      numSat = Serial1.read();
      checksum ^= numSat;
      break;  
    case 8: //Combine latitude bytes
      first = Serial1.read();
      second = Serial1.read();
      third = Serial1.read();
      fourth = Serial1.read();
      checksum ^= first;
      checksum ^= second;
      checksum ^= third;
      checksum ^= fourth;
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
      checksum ^= first;
      checksum ^= second;
      checksum ^= third;
      checksum ^= fourth;
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
      checksum ^= first;
      checksum ^= second;
      gpsAlt = second;
      gpsAlt <<= 8;
      gpsAlt += first;
      break;
    case 11: //Speed in cm/s
      first = Serial1.read();
      second = Serial1.read();
      checksum ^= first;
      checksum ^= second;
      gpsSpeed = second;
      gpsSpeed <<= 8;
      gpsSpeed += first;
      break;
    case 12: //Degrees times 10
      first = Serial1.read();
      second = Serial1.read();
      checksum ^= first;
      checksum ^= second;
      gpsCourse = second;
      gpsCourse <<= 8;
      gpsCourse += first;
      break;
    case 13:
      if(checksum == Serial1.read()){
        Serial.println("Checksum is correct for GPS");
      }
      else{
        Serial.println("Checksum is incorrect for GPS");
      }
      while(Serial1.available()){
        Serial1.read();
      }
      break;
    }
  }
  if(gpsFix > 2 || numSat > 30){
    return;
  }
  msp_raw_gps.gpsFix = gpsFix;
  msp_raw_gps.numSat = numSat;
  msp_raw_gps.lat = lat;
  msp_raw_gps.lon = lon;
  msp_raw_gps.gpsAlt = gpsAlt;
  msp_raw_gps.gpsSpeed = gpsSpeed;
  msp_raw_gps.gpsCourse = gpsCourse / 10;
  Serial.print("Fix: " + String(gpsFix));
  Serial.print(" NumSat: " + String(numSat));
  Serial.print(" Lat: " + String(lat/10000000.0, 5));
  Serial.print(" Lon: " + String(180 - lon/10000000.0, 5));
  Serial.print(" GPSALT: " + String(gpsAlt));
  Serial.print(" SOG: " + String(gpsSpeed));
  Serial.println(" GPSCourse: " + String(gpsCourse/10.0));
}

Arduino_h::IPAddress bsip;
int connectTime = 0;
WiFiUDP Udp;
bool firstconnectframe = false;

PrevMessage_h WifiComs::parseMessage(char buffer[]){
    PrevMessage_h msg;
    char *token;
    //Serial.println(buffer);
    token = strtok(buffer, "|");
    int i = 0;
    int wpNum = 0;
    int length;
    char lastWp;
    while(token != 0){
      //Serial.println(token);
      switch(i){
        case 0:
          msg.cmd = token;
          break;
        case 1:
          msg.sourceIP = token;
          break;
        case 2:
          if(msg.cmd == "SWM"){
            i = 8;
            state = token;
          }
          else{
            msg.yaw = atoi(token);  
          }     
          break;
        case 3:
          msg.pitch = atoi(token);  //pitch
          break;
        case 4: 
          msg.roll = atoi(token);
          break;
        case 5:
          msg.throttle = atoi(token);
          break;
        case 6:
          msg.killswitch = atoi(token);
          break;
        case 7:
          msg.armVar = atoi(token);
          break;
        case 8:
          msg.navHold = atoi(token);
          break;
        case 9:
          length = atoi(token);
          break;
        case 10:
          do{
            wpNum = atoi(token);
            token = strtok(NULL, "|"); 
            waypointArr[wpNum].lon = atoi(token);
            token = strtok(NULL, "|"); 
            waypointArr[wpNum].lat = atoi(token);
            token = strtok(NULL, "|"); 
            waypointArr[wpNum].alt = atoi(token);
            token = strtok(NULL, "|"); 
            waypointArr[wpNum].action = atoi(token);
            token = strtok(NULL, "|"); 
            waypointArr[wpNum].p1 = atoi(token);
            token = strtok(NULL, "|"); 
            waypointArr[wpNum].flag = atoi(token);
            token = strtok(NULL, "|"); 
            lastWp = *token;
            token = strtok(NULL, "|");
          }while(lastWp == *"loop");
          newWaypoints = true;
          break;
      }
      i++;
      token = strtok(NULL, "|"); 
    }
    return msg;
    //HAS REQUIRED PACKETS FROM LISTEN, CODE FOR MANUAL MODE HERE --------------
    //Currently does not include a break, repeats loop forever
}

BSIPMessage_h WifiComs::parseBSIP(char buffer[]){
    BSIPMessage_h msg;
    char *token;
    token = strtok(buffer, "|");
    int i = 0;
    // Serial.println("In parseBSIP");
    while(token != 0){
      // Serial.println(token);
      switch(i){
        case 0:
          msg.cmd = token;
          break;
        case 1:
          msg.BSIP = token;
          break;        
        }
      i++;
      token = strtok(NULL, "|"); 
    }
    return msg;  
}

int WifiComs::GenerateSearchPath(SearchArea searchArea){
  int shapePoints = sizeof(searchArea.searchBounds);
  char search = *"N";
  char spread = *"E";
  int laps;
  double northSouth = searchArea.searchBounds[0].y - searchArea.searchBounds[1].y;
  double eastWest = searchArea.searchBounds[0].x - searchArea.searchBounds[1].x;
  double viewDeg = searchArea.viewDistance / 111111;
  if(abs(northSouth) > abs(eastWest)){
    if(northSouth > 0){
      search = *"S";
    }
    else{
      search = *"N";
    }
    if(eastWest > 0){
      spread = *"W";
    }
    else{
      spread = *"E";
    }
    laps = floor(abs(northSouth)/(viewDeg*searchArea.dronesSearching*4));
    Serial.println("northSouth");
  }
  else{
    if(eastWest > 0){
      search = *"W";
    }
    else{
      search = *"E";
    }
    if(northSouth > 0){
      spread = *"S";
    }
    else{
      spread = *"N";
    }
    laps = floor(abs(eastWest)/(viewDeg*searchArea.dronesSearching*4));
    Serial.println("eastWest");
  }
  Waypoint path[128];
  Serial.print(search);
  Serial.println(spread);
  Serial.println(laps);
  switch(search){
    case *"N": // Northward search pattern
      for(int i = 1; i/4 < laps; i+=4){
        // Set latitude for each leg of the lap
        path[i].lat = 10000000*(searchArea.searchBounds[0].y + viewDeg);
        path[i+1].lat = 10000000*(searchArea.searchBounds[1].y - viewDeg);
        path[i+2].lat = 10000000*(searchArea.searchBounds[1].y - viewDeg);
        path[i+3].lat = 10000000*(searchArea.searchBounds[0].y + viewDeg);
      }
      break;
    case *"E": // Eastward search pattern
      for(int i = 1; i/4 < laps; i+=4){
        // Set longitude for each leg of the lap
        path[i].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x + viewDeg);
        path[i+1].lon = 0x100000000 + 10000000*(searchArea.searchBounds[1].x - viewDeg);
        path[i+2].lon = 0x100000000 + 10000000*(searchArea.searchBounds[1].x - viewDeg);
        path[i+3].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x + viewDeg);
      }
      break;
    case *"S": // Southward search pattern
      for(int i = 1; i/4 < laps; i+=4){
        // Set latitude for each leg of the lap
        path[i].lat = 10000000*(searchArea.searchBounds[0].y - viewDeg);
        path[i+1].lat = 10000000*(searchArea.searchBounds[1].y + viewDeg);
        path[i+2].lat = 10000000*(searchArea.searchBounds[1].y + viewDeg);
        path[i+3].lat = 10000000*(searchArea.searchBounds[0].y - viewDeg);
      }
      break;
    case *"W": // Westward search pattern
      for(int i = 1; i/4 < laps; i+=4){
        // Set longitude for each leg of the lap
        path[i].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x - viewDeg);
        path[i+1].lon = 0x100000000 + 10000000*(searchArea.searchBounds[1].x + viewDeg);
        path[i+2].lon = 0x100000000 + 10000000*(searchArea.searchBounds[1].x + viewDeg);
        path[i+3].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x - viewDeg);
      }
      break;
  }
  // Adjust path for spread direction
  switch(spread){
    case *"N": // Spread north
      for(int i = 1; i/4 < laps; i+=4){
        // Offset latitude for each lap to spread north
        path[i].lat = 10000000*(searchArea.searchBounds[0].y + ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+1].lat = 10000000*(searchArea.searchBounds[0].y + ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+2].lat = 10000000*(searchArea.searchBounds[0].y + 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+3].lat = 10000000*(searchArea.searchBounds[0].y + 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
      }
      break;
    case *"E": // Spread east
      for(int i = 1; i/4 < laps; i+=4){
        // Offset longitude for each lap to spread east
        path[i].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x + ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+1].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x + ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+2].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x + 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+3].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x + 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
      }
      break;
    case *"S": // Spread south
      for(int i = 1; i/4 < laps; i+=4){
        // Offset latitude for each lap to spread south
        path[i].lat = 10000000*(searchArea.searchBounds[0].y - ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+1].lat = 10000000*(searchArea.searchBounds[0].y - ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+2].lat = 10000000*(searchArea.searchBounds[0].y - 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+3].lat = 10000000*(searchArea.searchBounds[0].y - 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
      }
      break;
    case *"W": // Spread west
      for(int i = 1; i/4 < laps; i+=4){
        // Offset longitude for each lap to spread west
        path[i].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x - ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+1].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x - ((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+2].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x - 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
        path[i+3].lon = 0x100000000 + 10000000*(searchArea.searchBounds[0].x - 2*((i+3)/4)*(viewDeg*2*(searchArea.droneId+.5)));
      }
      break;
  }
  Serial.println("generate path");
  for(int i = 1; i <= (laps*4); i++){
    Serial.println(path[i].lat/10000000.0, 6);
    Serial.println((path[i].lon - 0x100000000)/10000000.0, 6);
    waypointArr[i].lat = path[i].lat;
    waypointArr[i].lon = path[i].lon;
    waypointArr[i].alt = 500;
    waypointArr[i].action = NAV_WP_ACTION_WAYPOINT;
    waypointArr[i].p1 = 0;
    waypointArr[i].p2 = 0;
    waypointArr[i].p3 = 0;
    if(i == laps*4){
      waypointArr[i].flag = NAV_WP_FLAG_LAST;
    }
    else{
      waypointArr[i].flag = 0;
    }
    Serial.println(i);
  }
  return laps*4;
}

void WifiComs::SendMessage(char msg[]){
    Udp.begin(localPort);
    // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.beginPacket("192.168.4.22", 80);
    Udp.write(msg);
    Udp.endPacket();
}

int WifiComs::WifiConnection(char ReplyBuffer[]){
    // attempt to connect to Wi-Fi network:
    if(WiFi.status() != WL_CONNECTED && ((millis() - connectTime) > 2000)) {
      // Connect to WPA/WPA2 network:
      WiFi.begin(ssid);
      //Retry every 5 seconds
      connectTime = millis();
      firstconnectframe = true;
      wifiState = 0;
      return 0;
    }
    else if(WiFi.status() == WL_CONNECTED && firstconnectframe){
      Udp.begin(localPort);
      // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.beginPacket("192.168.4.22", 80);
      Udp.write("State: 0 -> 1 |Connected|");
      Serial.println("State: 0 -> 1 |Connected|");
      Udp.endPacket();
      Udp.beginPacket("192.168.4.22", 80);
      Udp.write(ReplyBuffer);
      Udp.endPacket();
      wifiState = 1;
      firstconnectframe = false;
      return 1;
    }
    if(wifiState == 1 && WiFi.status() == WL_CONNECTED){
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("State: 1 -> 2");
      Serial.println("State: 1 -> 2");
      Udp.endPacket();
      wifiState = 2;
      return 2;
    }
    else if(wifiState == 2){ 
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("AmDrone");
      Serial.println("State: 2 -> 3");
      Udp.endPacket();
      wifiState = 3;
      return 3;
    }
    else if(wifiState == 4) {
      Udp.beginPacket(bsip, 5005);
      Serial.println(bsip);
      Serial.println(handShake);
      Udp.write(handShake);
      Udp.endPacket();
      Serial.println("State: 4 -> 5");
      wifiState = 5;
      return 5;
    }
    else
    {
      return wifiState;
    }
}

int WifiComs::Listen(char packetBuffer[255]){
    int packetSize = Udp.parsePacket();
    if(packetSize){
      //Serial.print("Received packet of size ");
      //Serial.println(packetSize);
      //Serial.print("From ");
      Arduino_h::IPAddress remoteIp = Udp.remoteIP();
      //Serial.print(remoteIp);
      //Serial.print(", port ");
      //Serial.println(Udp.remotePort());
      // read the packet into packetBufffer
      int len = Udp.read(packetBuffer, 255);
      //Serial.println(packetBuffer);
      if (len > 0) {
        packetBuffer[len] = 0;
        if (wifiState == 3){
          // Serial.println("Parsing BSIP Message");
          //read BSID response from AP      
          BSIPMessage = parseBSIP(packetBuffer);
          BSIPMessage_h msg;
          msg = BSIPMessage;
          if (msg.cmd == "BSIP"){
            bsip = msg.BSIP;
            // Serial.print("Base Station IP: ");
            // Serial.println(bsip);
            wifiState = 4;
            Serial.println("State: 3 -> 4");
            return 4;
          }
        }
        else if (wifiState == 5){
          // Serial.println(packetBuffer);
          PrevMessage = parseMessage(packetBuffer);
          wifiState = 5;
          return 5;
        }
      }    
    }
    return wifiState;
}