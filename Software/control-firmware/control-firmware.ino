#include "AccelStepper.h"
#include "MultiStepper.h"
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

const int steps_per_rev = 200 * 16;
long motor_step_positions[] = {0, 0, 0, 0, 0, 0};
int gear_ratios[] = {16, 24, 19, 15, 15, 15};

// Set up stepper objects
AccelStepper stepper1(AccelStepper::DRIVER, MOT1_STP, MOT1_DIR);
AccelStepper stepper2(AccelStepper::DRIVER, MOT2_STP, MOT2_DIR);
AccelStepper stepper3(AccelStepper::DRIVER, MOT3_STP, MOT3_DIR);
AccelStepper stepper4(AccelStepper::DRIVER, MOT4_STP, MOT4_DIR);
AccelStepper stepper5(AccelStepper::DRIVER, MOT5_STP, MOT5_DIR);
AccelStepper stepper6(AccelStepper::DRIVER, MOT6_STP, MOT6_DIR);

MultiStepper steppers;

void setup() {
    // Begin Serial port
    Serial.begin(38400);
    // Set up the enable pin
    pinMode(MOT_EN, OUTPUT);
    digitalWrite(MOT_EN, LOW);

    steppers.addStepper(stepper1);
    steppers.addStepper(stepper2);
    steppers.addStepper(stepper3);
    steppers.addStepper(stepper4);
    steppers.addStepper(stepper5);
    steppers.addStepper(stepper6);
    delay(5000);
    // Run a demo sequence
    float accel_factor = 0.00001;
    simultaneous_move_degrees(5.0, accel_factor, 60, 75, 80, 0, 0, 0);
    delay(100);
    simultaneous_move_degrees(3.0, accel_factor, 75, 140, 50, 0, 0, 0);
    delay(500);
    simultaneous_move_degrees(1.0, accel_factor, 75, 130, 45, 0, 0, 0);
    delay(100);
    simultaneous_move_degrees(1.0, accel_factor, 45, 130, 45, 0, 0, 0);
    delay(100);
    simultaneous_move_degrees(1.0, accel_factor, 45, 140, 50, 0, 0, 0);
    delay(500);
    simultaneous_move_degrees(7.5, accel_factor, 0, 0, 0, 0, 0, 0);
    
    
}

void loop() {}

void simultaneous_move_steps(float move_time, float accel_factor, int m1, int m2, int m3, int m4, int m5, int m6) {
    long m1_dist = m1 - motor_step_positions[0];
    long m2_dist = m2 - motor_step_positions[1];
    long m3_dist = m3 - motor_step_positions[2];
    long m4_dist = m4 - motor_step_positions[3];
    long m5_dist = m5 - motor_step_positions[4];
    long m6_dist = m6 - motor_step_positions[5];
    stepper1.setMaxSpeed(m1_dist / move_time);
    stepper2.setMaxSpeed(m2_dist / move_time);
    stepper3.setMaxSpeed(m3_dist / move_time);
    stepper4.setMaxSpeed(m4_dist / move_time);
    stepper5.setMaxSpeed(m5_dist / move_time);
    stepper6.setMaxSpeed(m6_dist / move_time);
    stepper1.setAcceleration(accel_factor * m1_dist / move_time);
    stepper2.setAcceleration(accel_factor * m2_dist / move_time);
    stepper3.setAcceleration(accel_factor * m3_dist / move_time);
    stepper4.setAcceleration(accel_factor * m4_dist / move_time);
    stepper5.setAcceleration(accel_factor * m5_dist / move_time);
    stepper6.setAcceleration(accel_factor * m6_dist / move_time);
    motor_step_positions[0] = m1;
    motor_step_positions[1] = m2;
    motor_step_positions[2] = m3;
    motor_step_positions[3] = m4;
    motor_step_positions[4] = m5;
    motor_step_positions[5] = m6;
    steppers.moveTo(motor_step_positions);
    steppers.runSpeedToPosition();
}
void simultaneous_move_degrees(float move_time, float accel_factor, float m1, float m2, float m3, float m4, float m5, float m6) {
    long m1_steps = m1 * steps_per_rev * gear_ratios[0] / 360;
    long m2_steps = m2 * steps_per_rev * gear_ratios[1] / 360;
    long m3_steps = m3 * steps_per_rev * gear_ratios[2] / 360;
    long m4_steps = m4 * steps_per_rev * gear_ratios[3] / 360;
    long m5_steps = m5 * steps_per_rev * gear_ratios[4] / 360;
    long m6_steps = m6 * steps_per_rev * gear_ratios[5] / 360;
    simultaneous_move_steps(move_time, accel_factor, m1_steps, m2_steps, m3_steps, m4_steps, m5_steps, m6_steps);
}