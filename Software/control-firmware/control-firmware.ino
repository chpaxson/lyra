#include "AA_MCP2515.h"
#include <Stepper.h>
/*==== CAN Bus Pins ====*/
#define CAN_CS 53
#define CAN_INT 21
/*==== Motor Pins ====*/
#define MOT_EN 13

#define MOT1_STP 2
#define MOT2_STP 3
#define MOT3_STP 4
#define MOT4_STP 5
#define MOT5_STP 6
#define MOT6_STP 7

#define MOT1_DIR 22
#define MOT2_DIR 23
#define MOT3_DIR 24
#define MOT4_DIR 25
#define MOT5_DIR 26
#define MOT6_DIR 27



void setup() {
  // put your setup code here, to run once:
  Serial.begin(38400);
}

void loop() {
  // put your main code here, to run repeatedly:

}
