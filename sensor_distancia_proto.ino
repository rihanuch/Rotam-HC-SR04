#include <HCSR04.h>

UltraSonicDistanceSensor distanceSensor_1(13, 12);  // Initialize sensor that uses digital pins 13 and 12.
UltraSonicDistanceSensor distanceSensor_2(11, 10);  // Initialize sensor that uses digital pins 11 and 10.

void setup () {
    Serial.begin(9600);  // We initialize serial connection so that we could print values from sensor.
}

void loop () {
    // Every 250 miliseconds, do a measurement using the sensor and print the distance in centimeters.
    Serial.print(distanceSensor_1.measureDistanceCm());
    Serial.print(";");
    Serial.println(distanceSensor_2.measureDistanceCm());
    delay(250);
}
