#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9



MFRC522 rfid(SS_PIN, RST_PIN);

String rfid_nuids[] = {"37fc943b", "cb72c5ae", "f73f9339"};

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  rfid.PCD_DumpVersionToSerial();
  if (rfid.PCD_PerformSelfTest()) Serial.println("Passed Self-Test");
}

void loop() {
  Serial.println("start");
  if ( !rfid.PICC_IsNewCardPresent() ) {
    Serial.println("A");
    return;
  }
  Serial.println("detected");
  if ( !rfid.PICC_ReadCardSerial()) {
    Serial.println("B");
    return;
  }
  Serial.println("knon");

  String nuid = readHex(rfid.uid.uidByte, rfid.uid.size);
  Serial.println(nuid);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

String readHex(byte *buffer, byte bufferSize) {
  String result = "";
  for (byte i = 0; i < bufferSize; i++) {
    String* hex[] = {};
    result = result + String(buffer[i] < 0x10 ? " 0" : "");
    result = result + String(buffer[i], HEX);
  }
  return result;
}