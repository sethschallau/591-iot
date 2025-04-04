### Architecture
ESP86 tracks motor time running and the pushes to MQTT Broker the time.
Server pulls this, calculates the usage with the analytics down and appends (total rolls, total tree, total c02 usage) to the existing one in a local file
The server pushes out to the broker again, and the interface pulls from that and displays it

### Training
We need to run the motor with the paper towel attached and log how long it takes to unroll the entire roll. Then we find how many trees and C02 a paper towel roll uses. This will let us calculate. 

### Analytics
( total time unrolling / full roll time ) = rolls unrolled
( time unrolling / full roll time ) * rolls per tree  = total tree
( time unrolling / full roll time ) * C02 per roll = C02 usage 

### Breakdown

We propose a smart home device that tracks automatically rotates paper towels so the user doesn't have to touch the roll when cooking and then provides analytics on a homes paper towel usage and provides feedback on their fiscal and environmental impact due to their paper towel consumption. The project will consist of a stepper motor and a custom paper towel enclosure that rotates when an ultrasonic sensor  detects a user waving for a paper towel. We will also publish to a broker and subscribe with a web service that will display the usage patterns and analyze how many rolls have been used.

Step 1: Design the dispenser; 20%, Alex

Step 2: Configure the sensors to activate the dispenser; 20%, Sayali

Step 3: Setup the web service/server; 10%, Seth

Step 4: Publish the dispenser data to a web service; 20%, Amy

Step 5: Analyze/Visualize the cost and tree usage of the dispensed towels; 10%, Seth


### Demo steps
