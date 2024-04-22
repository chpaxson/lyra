#include "AA_MCP2515.h"
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

/*==== CAN Config ====*/
#define CAN_CS  53
#define CAN_INT 21

const CANBitrate::Config CAN_BITRATE = CANBitrate::Config_8MHz_500kbps;

CANConfig config(CAN_BITRATE, CAN_CS, CAN_INT);
CANController CAN(config);

void setup() {
    // Begin Serial port
    Serial.begin(38400);
    pinMode(MOT_EN, OUTPUT);
    // Motor 1
    pinMode(MOT1_STP, OUTPUT);
    pinMode(MOT1_DIR, OUTPUT);

    digitalWrite(MOT1_DIR, HIGH);
    digitalWrite(MOT_EN, HIGH);
    // Set up Motor 1
    setWorkMode(1, 1);
    setWorkCurrent(1, 1000);
    setHoldCurrent(1, 3);
    setMicrosteps(1, 16);
    enableBehavior(1, 1);
}

void loop() {
    digitalWrite(MOT1_STP, HIGH);
    delay(10);
    digitalWrite(MOT1_STP, LOW);
    delay(10);
}

/*
    0 - Pulse interface, open loop
    1 - Pulse interface, closed loop
    2 - Pulse interface, FOC
    3 - Serial interface, open loop
    4 - Serial interface, closed loop
    5 - Serial interface, FOC
*/
void setWorkMode(int motor, int mode) {
    sendCommand(motor, {0x82, mode});
    Serial.print("Motor ");
    Serial.print(motor);
    Serial.print(" work mode set to ");
    switch mode {
        case 0:
            Serial.println("CR_OPEN");
            break;
        case 1:
            Serial.println("CR_CLOSE");
            break;
        case 2:
            Serial.println("CR_FOC");
            break;
        case 3:
            Serial.println("SR_OPEN");
            break;
        case 4:
            Serial.println("SR_CLOSE");
            break;
        case 5:
            Serial.println("SR_FOC");
            break;
    }
}

void setWorkCurrent(int motor, int current) {
    sendCommand(motor, {0x83, current >> 8, current & 0xFF});
    Serial.print("Motor ");
    Serial.print(motor);
    Serial.print(" work current set to ");
    Serial.print(current);
    Serial.println(" mA");
}

/*
    Input as a percentage
    0 -> 10%, 1 -> 20%, 2 -> 30%, 3 -> 40%, 4 -> 50%, 5 -> 60%, 6 -> 70%, 7 -> 80%, 8 -> 90%
*/
void setHoldCurrent(int motor, int currentPercent) {
    sendCommand(motor, {0x9B, currentPercent / 10 - 1});
    Serial.print("Motor ");
    Serial.print(motor);
    Serial.print(" hold current set to ");
    Serial.print(currentPercent * 10);
    Serial.println(" mA");
}

void setMicrosteps(int motor, int microsteps) {
    sendCommand(motor, {084A, microsteps});
    Serial.print("Motor ");
    Serial.print(motor);
    Serial.print(" microsteps set to ");
    Serial.println(microsteps);
}

/*
    0 - Active when pin is low
    1 - Active when pin is high
    2 - Always active
*/
void enableBehavior(int motor, int behavior) {
    sendCommand(motor, {0x85, behavior});
    Serial.print("Motor ");
    Serial.print(motor);
    Serial.print(" enable behavior set to be ");
    switch behavior {
        case 0:
            Serial.println("active when pin is low");
            break;
        case 1:
            Serial.println("active when pin is high");
            break;
        case 2:
            Serial.println("always active");
            break;
    }
}

/*
    Direction is the first bit of the second byte
    Speed is 12 bits long, starting at the 5th bit of the second byte and completing the third byte
    Acceleration is the fourth byte
    Pulses is 24 bits long, composing bytes 5, 6, and 7
*/
void move_relative(int motor, bool dir, uint16_t speed, uint8_t accel, uint32_t pulses) {
    byte byte2 = (dir << 8) | (speed >> 8);
    byte byte3 = speed & 0b000011111111;
    byte byte4 = accel;
    byte byte5 = pulses >> 16;
    byte byte6 = pulses >> 8;
    byte byte7 = pulses;
    sendCommand(motor, {0xFD, byte2, byte3, byte4, byte5, byte6, byte7});
    Serial.print("Motor ");
    Serial.print(motor);
    Serial.print(" moving ");
    if (dir) {
        Serial.print("clockwise ");
    } else {
        Serial.print("counter-clockwise ");
    }
    Serial.print(pulses);
    Serial.println(" pulses");
}


// Send a frame to the motor controller
void sendCommand(int motorAddress, int[] commandData) {
    crc = motorAddress;
    for (int i = 0; i < sizeof(commandData); i++) {
        crc = crc + commandData[i];
    }
    crc = crc % 256;
    byte data[] = {motorAddress, commandData, crc};
    CAN.write(motorAddress, data, sizeof(data));
}
