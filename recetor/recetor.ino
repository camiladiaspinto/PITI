#include "HardwareSerial.h"

// Declaração das portas seriais
HardwareSerial mySerial1(1); // Comunicação no pino 17
HardwareSerial mySerial2(2); // Recebimento no pino 16

void setup() {
  Serial.begin(9600);
  mySerial1.begin(9600, SERIAL_8N1, -1, 17);
  mySerial2.begin(9600, SERIAL_8N1, 16, -1);
}

void loop() {
  // Verifica se há dados disponíveis no Serial padrão
  while (Serial.available() > 0) {
    byte data = Serial.read();
    mySerial1.write(data);
  }

  if (mySerial2.available() > 0) {
    byte msb = mySerial2.read();  // Lê o byte mais significativo
    Serial.write(msb);
  }
}
