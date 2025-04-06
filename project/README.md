### Architecture
[image on the way]

### Training
We need to run the motor with the paper towel attached and log how long it takes to unroll the entire roll. Then we find how many trees and C02 a paper towel roll uses. This will let us calculate.

### Analytics
( total time unrolling / full roll time ) = rolls unrolled
( time unrolling / full roll time ) * rolls per tree  = total tree
( time unrolling / full roll time ) * C02 per roll = C02 usage

#### Paper Towel Roll to Tree and C02 Emission Ratio
- 1 Tree = X Rolls of Paper Towels
- 1 Roll of Paper Towels = Y grams of C02

### Demo steps

- (5 pts) Moving a hand in front of the ultrasonic sensor sends a signal to the ESP8266
- (15 pts) Upon receiving the signal, the ESP8266 triggers the stepper motor with a paper towel roll attached
- (10 pts) When the hand is removed from the sensor's range, the motor stops actuating
- (15 pts) The ESP8266 tracks how long the motor is activated and sends this time to the cloud MQTT broker
- (15 pts) A server pulls this information from the broker and stores it locally
- (10 pts) The time usage is used to calculate the approximate paper towel usage
- (15 pts) The approximate paper towel usage is used to calculate tree usage and carbon footprint
- (15 pts) The paper towel, tree, and carbon information is presented to the user on a web interface
