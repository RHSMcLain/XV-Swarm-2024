#include <ESP8266WiFi.h> //https://github.com/esp8266/Arduino/tree/master
#include <WiFiUDP.h>

IPAddress local_IP(192,168,4,22);
IPAddress gateway(192,168,4,9);
IPAddress subnet(255,255,255,0);
unsigned int localPort = 80;
int droneArray[3] = {1,7,9};


WiFiUDP Udp;
char packetBuffer[256]; //buffer to hold incoming packet
char ReplyBuffer[256] = "reply";       // a string to send back

void setup()
{
  Serial.begin(115200);
  Serial.println();

  Serial.print("Setting soft-AP configuration ... ");
  Serial.println(WiFi.softAPConfig(local_IP, gateway, subnet) ? "Ready" : "Failed!");

  Serial.print("Setting soft-AP ... ");
  Serial.println(WiFi.softAP("XV_Basestation") ? "Ready" : "Failed!");

  Serial.print("Soft-AP IP address = ");
  Serial.println(WiFi.softAPIP());
  Udp.begin(localPort);
}


  //add name of drone from handshake to array


void loop() {
  //listens for message
  int packetSize = Udp.parsePacket ();
  if (packetSize) {

    Serial.print("Received packet of size ");

    Serial.println(packetSize);

    Serial.print("From ");

    IPAddress remoteIp = Udp.remoteIP();

    Serial.print(remoteIp);

    Serial.print(", port ");

    Serial.println(Udp.remotePort());

    // read the packet into packetBufffer

    int len = Udp.read(packetBuffer, 255);

    if (len > 0) {

      packetBuffer[len] = 0;

    }

    Serial.println("Contents:");

    Serial.println(packetBuffer);

    // send a reply, to the IP address and port that sent us the packet we received
    // if (packetBuffer == 2006) {
      if (strcmp(packetBuffer, "Drone 1")){      
       Serial.println("It is Drone 1");
       Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
       Udp.write(ReplyBuffer);
      
      Udp.endPacket();
     }
     

  }
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print your board's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.print(rssi);

  Serial.println(" dBm");


}


//pulled out of loop. We think this is trying to connect to a separate client and is not needed. 
  // char intToPrint[5];

  // WiFiClient client;
  // const char * host = "192.168.4.1";
  // const int httpPort = 80;

  // if (!client.connect(host, httpPort)) {
  //   Serial.println("connection failed");
  //   return;
  // }
  // if (client.connect(host, httpPort)) {
  //   Serial.println("connection not failed");
  //   return;
  // }

  // String url = "/data/";
  // url += "?sensor_reading=";
  // url += intToPrint;

  // client.print(String("GET ") + url + " HTTP/1.1\r\n" +
  //              "Host: " + host + "\r\n" +
  //              "Connection: close\r\n\r\n");
  // unsigned long timeout = millis();
  // while (client.available() == 0) {
  //   if (millis() - timeout > 5000) {
  //     Serial.println(">>> Client Timeout !");
  //     client.stop();
  //     return;
  //   }
  // }
