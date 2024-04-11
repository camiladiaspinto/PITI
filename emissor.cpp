#define RXp2 16
#define TXp2 17
void setup() {
  Serial.begin(9600);
  Serial1.begin(9600, SERIAL_8N1, RXp2, TXp2); // Defina aqui os pinos RX e TX do seu Arduino
}

void loop() {
  if (Serial.available() > 0) {
    byte buffer[128];
    int bytesRead = Serial.readBytes(buffer, sizeof(buffer));
    
    // Enviar dados recebidos para o módulo serial 1
    Serial1.write(buffer, bytesRead);

    Serial1.flush();
  }
}
