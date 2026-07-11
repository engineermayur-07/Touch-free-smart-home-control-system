#include <LiquidCrystal.h>

LiquidCrystal lcd(6, 7, 8, 9, 10, 11);

const int fanPin = 2;
const int ledPin = 3;
const int buzzerPin = 4;
const int pumpPin = 5;
const int gasSensorPin = A0;

void setup() {
  lcd.begin(16, 2);
  lcd.print("System Ready");
  delay(2000);
  lcd.clear();

  pinMode(fanPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(pumpPin, OUTPUT);
  pinMode(gasSensorPin, INPUT);

  digitalWrite(fanPin, LOW);
  digitalWrite(ledPin, LOW);
  digitalWrite(buzzerPin, LOW);
  digitalWrite(pumpPin, LOW);

  Serial.begin(9600);
}

void loop() {
  int gasValue = analogRead(gasSensorPin);
  if (gasValue > 400) {
    digitalWrite(buzzerPin, HIGH);
    lcd.clear();
    lcd.print("Gas Detected!");
    delay(5000);
    digitalWrite(buzzerPin, LOW);
    lcd.clear();
  }

  if (Serial.available()) {
    char command = Serial.read();
    switch (command) {
      case '1': digitalWrite(fanPin, HIGH); lcd.print("Fan: ON"); break;
      case '2': digitalWrite(fanPin, LOW); lcd.print("Fan: OFF"); break;
      case '3': digitalWrite(ledPin, HIGH); lcd.print("Light: ON"); break;
      case '4': digitalWrite(ledPin, LOW); lcd.print("Light: OFF"); break;
      case '5': digitalWrite(pumpPin, HIGH); lcd.print("Pump: ON"); break;
      case '6': digitalWrite(pumpPin, LOW); lcd.print("Pump: OFF"); break;
      case '7': digitalWrite(buzzerPin, HIGH); lcd.print("Buzzer: ON"); break;
      case '8': digitalWrite(buzzerPin, LOW); lcd.print("Buzzer: OFF"); break;
    }
    delay(1000);
    lcd.clear();
  }
}
