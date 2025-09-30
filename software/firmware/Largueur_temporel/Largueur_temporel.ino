#include <Wire.h>
#include <DS3231.h>
#include "BluetoothSerial.h"
#include <Preferences.h>
#include <ESP32Servo.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

DS3231 myRTC;
BluetoothSerial SerialBT;
Preferences preferences;
Servo myservo;


byte year;
byte month;
byte date;
byte hour;
byte minute;
byte second;

byte alarm_date;
byte alarm_month;
byte alarm_hour;
byte alarm_minute;
byte alarm_second;

int pin_magnet = 16;
int pin_shtdwn = 27;

byte alarmMinute;
byte alarmBits;


String get_token(String &from, uint8_t index, char separator) {
  String to;
  uint16_t start = 0, idx = 0;
  uint8_t cur = 0;
  while (idx < from.length()) {
    if (from.charAt(idx) == separator) {
      if (cur == index) {
        to = from.substring(start, idx);
        return to;
      }
      cur++;
      while ((idx < from.length() - 1) && (from.charAt(idx + 1) == separator)) idx++;
      start = idx + 1;
    }
    idx++;
  }
  if ((cur == index) && (start < from.length())) {
    to = from.substring(start, from.length());
    return to;
  }
  return "";
}

void setTime(byte year, byte month, byte date, byte hour, byte minute, byte second) {
  myRTC.setClockMode(false);
  myRTC.setYear(year);
  myRTC.setMonth(month);
  myRTC.setDate(date);
  myRTC.setHour(hour);
  myRTC.setMinute(minute);
  myRTC.setSecond(second);
}

void setAlarm(byte alarm_date, byte alarm_hour, byte alarm_minute, byte alarm_second) {
  myRTC.turnOffAlarm(1);
  myRTC.setA1Time(
    alarm_date, alarm_hour, alarm_minute, alarm_second,
    0b00000000, false, false, true);
  // enable Alarm 1 interrupts
  myRTC.turnOnAlarm(1);
  // clear Alarm 1 flag
  myRTC.checkIfAlarm(1);
  // deactivate the second alarm
  alarmMinute = 0xFF;      // a value that will never match the time
  alarmBits = 0b01100000;  // Alarm 2 when minutes match, i.e., never
  // Upload the parameters to prevent Alarm 2 entirely
  myRTC.setA2Time(
    0, 0, alarmMinute,
    alarmBits, false, false, false);
  // disable Alarm 2 interrupt
  myRTC.turnOffAlarm(2);
  // clear Alarm 2 flag
  myRTC.checkIfAlarm(2);
}

void parse_time(String msg) {
  if (msg.startsWith("A")) {
    Serial.println("AlarmSet");
    alarm_date = byte(get_token(msg, 0, '/').toInt());
    alarm_month = byte(get_token(msg, 1, '/').toInt());
    alarm_hour = byte(get_token(msg, 2, '/').toInt());
    alarm_minute = byte(get_token(msg, 3, '/').toInt());
    Serial.print(alarm_minute);
    setAlarm(alarm_date, alarm_hour, alarm_minute, 0);

    preferences.putUInt("state", 1);            //armed
    preferences.putUInt("month", alarm_month);  //store month
    preferences.end();

    // Going to sleep
    digitalWrite(pin_shtdwn, HIGH);
    delay(5000);
  }

  else {
    Serial.println("timeSet");
    year = byte(get_token(msg, 0, '/').toInt());
    date = byte(get_token(msg, 2, '/').toInt());
    month = byte(get_token(msg, 1, '/').toInt());
    hour = byte(get_token(msg, 3, '/').toInt());
    minute = byte(get_token(msg, 4, '/').toInt());
    second = byte(get_token(msg, 5, '/').toInt());
    Serial.println(second);
    setTime(year, month, date, hour, minute, second);
  }
}

void wake_up() {
  int month_stored = preferences.getUInt("month", 0);
  bool century = false;
  month = myRTC.getMonth(century);

  if (month == month_stored) {
    preferences.putUInt("state", 0);
    preferences.end();

    // release payload
    myservo.write(180);
    delay(2000);
    myservo.write(0);
  } else {
    // Go back to sleep
    myRTC.checkIfAlarm(1);
    digitalWrite(pin_shtdwn, HIGH);
    delay(5000);
  }
}

void setup() {
  Serial.begin(115200);
  SerialBT.begin("LAMOS");

  Wire.begin(22, 21);

  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
  myservo.setPeriodHertz(50); // standard 50 hz servo
	myservo.attach(pin_magnet, 1000, 2000);

  
  pinMode(pin_shtdwn, OUTPUT);
  digitalWrite(pin_shtdwn, LOW);

  preferences.begin("my-app", false);
  unsigned int state = preferences.getUInt("state", 0);

  if (state == 1) {
    wake_up();
  }
}

void loop() {
  String msg;
  if (SerialBT.available() > 0) {
    msg = SerialBT.readStringUntil('\n');
    msg.remove(msg.length() - 1, 1);
    parse_time(msg);
  }
  delay(20);
}
