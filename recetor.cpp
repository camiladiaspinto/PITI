#include <Arduino.h>

#define RXp2 16
#define TXp2 17

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600, SERIAL_8N1, RXp2, TXp2);
}

void loop() {

  if (Serial1.available() > 0) { // Verifica se há dados recebidos da ESP

    byte buffer[256];
    int bytesRead = Serial1.readBytes(buffer, sizeof(buffer));

    char receivedString[bytesRead + 1];
    for (int i = 0; i < bytesRead; i++) {
      receivedString[i] = (char)buffer[i];
    }
    receivedString[bytesRead] = '\0';

    Serial.write((const uint8_t*)receivedString, bytesRead);
  }

  delay(1000);
}
