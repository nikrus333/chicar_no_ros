#include "ChiMotorCustom.h"
#include <Servo.h>

ChiMotor chiMotor;
Servo drive;

String strIn;
String sAng;
String sVel;
byte devider;
double vel;
double angle;

long timer;

void fuTest() {
  chiMotor.interruptListener();
}

void steering (int turn_angle){ // переписать под инста-рулежку
  if (turn_angle<-30){
    turn_angle = -30;}
  else if (turn_angle>30){
    turn_angle = 30;}
  drive.write(map(turn_angle, -30, 30, 60, 120));
}


void setup() {
  
  chiMotor.init(1, 2, 52, 3);
  chiMotor.wheelMode();
  attachInterrupt(digitalPinToInterrupt(2), fuTest, CHANGE);

  Serial.begin(115200);
  Serial.setTimeout(3);

  timer = millis();
  pinMode(53, OUTPUT);
  digitalWrite(53, HIGH);

  drive.attach(10);
}

void loop() {
  chiMotor.tick();
  if (millis() - timer > 50) {
    //Serial.print(chiMotor.getRealRadianVelocity());
    Serial.println(vel);
    Serial.println(angle);
    timer = millis();
  }
  
  

  if (Serial.available() > 0) {
    strIn = Serial.readString();
    if(strIn.equals("w"))
      vel += 2;
      else if(strIn.equals("x"))
      vel -= 2;
      else if(strIn.equals("a"))
      angle -= 10;
      else if(strIn.equals("d"))
      angle += 10;
      else if(strIn.equals("s")) {
      vel = 0;
      angle = 0;
      }
      else {
        devider = strIn.indexOf(',');
    sVel = strIn.substring(0, devider);
    sAng = strIn.substring(devider + 1);
    vel = sVel.toFloat();
    angle = sAng.toFloat();
      }
    
    chiMotor.setGoalVelocity(vel);
    steering(angle);
  }
}
