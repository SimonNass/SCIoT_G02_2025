#include <MFRC522.h>
#include <MFRC522Extended.h>
#include <deprecated.h>
#include <require_cpp11.h>

//lib MFRC522 by GithubCommunity installed
#include "MFRC522.h"
#include <SPI.h>
//lib DHT sensor library by Adafruit installed + dependencies
#include "DHT.h"
#include <Servo.h>

#define SS_PIN 10
#define RST_PIN 9
#define servo_pin 3
#define DHTPIN 2
#define DHTTYPE DHT11
#define sound_pin 0

MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo servo;  // create servo object to control a servo
DHT dht(DHTPIN, DHTTYPE);
String input_str = "";
boolean string_complete = false;

void setup() {
  // comunication chanel
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  input_str.reserve(200);

  // RFID
  //SPI.begin();
  //mfrc522.PCD_Init();
  //delay(15);
  //mfrc522.PCD_DumpVersionToSerial();
  //if (mfrc522.PCD_PerformSelfTest()) Serial.println("Passed Self-Test");

  // servo motor
  servo.attach(servo_pin); // attaches the servo on pin 9 to the servo object
  if (!servo.attached()) {
    // TODO not attached
  }

  // temperature sensor
  dht.begin(); // initialize the sensor
  
  // sound sensor
  pinMode(sound_pin, INPUT);
}

void loop() {
  //delay(2000);
  //Serial.println("---");
  //senseSound();
  //senseHumidity();
  //senseTemperature();
  //activateRFID();
  //activateServo(0);
  if (string_complete) {
    handleRequest(input_str);
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      string_complete = true;
    } else {
      input_str += inChar;
    }
  }
}

void handleRequest(String input) {
  //Serial.print("echo request: ");
  String end_of_serial = "EndOfSerial";
  //Serial.print(input);
  int index = input.indexOf(":");
  String type_name = input.substring(0,index);
  String body = input.substring(index+1,input.length());
  //Serial.print(type_name);
  //Serial.print(body);
  if (type_name.equals("motor")) {
    activateServo(body.toInt());
    Serial.println(end_of_serial);
  } else if (type_name.equals("soundlevel")) {
    senseSound();
    Serial.println(end_of_serial);
  } else if (type_name.equals("humidity")) {
    senseHumidity();
    Serial.println(end_of_serial);
  } else if (type_name.equals("temperature")) {
    senseTemperature();
    Serial.println(end_of_serial);
  } else if (type_name.equals("rfid")) {
    //activateRFID();
    Serial.println(end_of_serial);
  } else if (type_name.equals("exit")) {
    Serial.println(end_of_serial);
    exit(0);
  }
  //delay(15);
  input_str = "";
  string_complete = false;
}

void activateRFID() {
  //Serial.println("start search");
  if (!mfrc522.PICC_IsNewCardPresent())
  {
    delay(1000);
    //Serial.println("stop");
    // Wenn keine Karte in Reichweite ist ..
    // .. wird die Abfrage wiederholt.
    return;
  }
  //Serial.println("new");
  if (!mfrc522.PICC_ReadCardSerial())
  {
    delay(1000);
    // Wenn kein RFID-Sender ausgewählt wurde ..
    // .. wird die Abfrage wiederholt.
    return;
  }
  //Serial.println("Karte entdeckt!");
  String WertDEZ;
  // Dezimal-Wert in Strings schreiben
  for (byte i = 0; i < mfrc522.uid.size; i++)
  {
    // String zusammenbauen
    WertDEZ = WertDEZ + String(mfrc522.uid.uidByte[i], DEC) + " ";
  }
  // Kennung dezimal anzeigen
  Serial.print("RFIDuid: ");
  Serial.println(WertDEZ);
  // kurze Pause, damit nur ein Wert gelesen wird
  delay(1000);
}

void activateServo(int pos) {
  int val = max(min(180,pos),0);
  if (val >= 0 && val <= 180) {
    servo.write(val);
    Serial.print("Servomotor: ");
    Serial.println(val);
  }
}


void senseHumidity() {
  //delay(2000);
  float humi  = dht.readHumidity();
  if (isnan(humi)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Humidity: ");
    Serial.println(humi);
  }
}

void senseTemperature() {
  //delay(2000);
  float tempC = dht.readTemperature();
  if (isnan(tempC)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Temperature: ");
    Serial.println(tempC);
  }
}

void senseSound() {
  int currentState = analogRead(sound_pin);
  Serial.print("Soundlevel: ");
  Serial.println(currentState);
}
