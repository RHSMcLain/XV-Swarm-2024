#include <Arduino.h>
#include <WiFiNINA.h>                    //https://github.com/arduino-libraries/WiFiNINA/tree/master
#include <WiFiUDP.h>
#include "XvWifi.h"

ManualControlMessage_h XvWifi::parseMessage(char buffer[]){
    ManualControlMessage_h msg;
    char *token;
    token = strtok(buffer, "|");
    int i = 0;
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
          msg.yaw = atoi(token);       
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
        }
      i++;
      token = strtok(NULL, "|"); 
    }
    return msg;  
    //HAS REQUIRED PACKETS FROM LISTEN, CODE FOR MANUAL MODE HERE --------------
    //Currently does not include a break, repeats loop forever
}

BSIPMessage_h XvWifi::parseBSIP(char buffer[]){
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

void XvWifi::SendMessage(char msg[]){
    Udp.begin(localPort);
    // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.beginPacket("192.168.4.22", 80);
    Udp.write(msg);
    Udp.endPacket();
}

int XvWifi::WifiConnection(char ReplyBuffer[], int wifiState, int droneState){
    // attempt to connect to Wi-Fi network:
    if(WiFi.status() != WL_CONNECTED && ((millis() - connectTime) > 5000)) {
      // Connect to WPA/WPA2 network:
      WiFi.begin(ssid);
      //Retry every 5 seconds
      connectTime = millis();
      while((millis() - connectTime) > 2000){
        // you're connected now, so print out the data:
        if(WiFi.status() == WL_CONNECTED){
          Udp.begin(localPort);
          // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
          Udp.beginPacket("192.168.4.22", 80);
          Udp.write("State: 0 -> 1 |Connected|");
          Udp.endPacket();
          wifiState = 1;
          Udp.beginPacket("192.168.4.22", 80);
          Udp.write(ReplyBuffer);
          Udp.endPacket();
          return 1;
        }
      }
      return 0;
    }
    if(wifiState == 1 && droneState == 1 && WiFi.status() == WL_CONNECTED){
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("State: 1 -> 2");
      Udp.endPacket();
      return 2;
    }
    else if(wifiState == 2){ 
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.write("AmDrone");
      Udp.endPacket();
      return 3;
    }
    else if(wifiState == 4) {
      Udp.beginPacket(bsip, 5005);
      Udp.write(handShake);
      Udp.endPacket();
      return 5;
    }
    else
    {
      return wifiState;
    }
}

int XvWifi::Listen(int wifiState, char packetBuffer[255]){
    int packetSize = Udp.parsePacket();
    if(packetSize){
      //Serial.print("Received packet of size ");
      //Serial.println(packetSize);
      //Serial.print("From ");
      IPAddress remoteIp = Udp.remoteIP();
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
            return 4;
          }
        }
        else if (wifiState == 5){
          ManualControlMessage = parseMessage(packetBuffer);
          return 5;
        }
      }    
    }
    return wifiState;
}
