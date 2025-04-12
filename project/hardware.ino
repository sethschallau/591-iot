// Pin definitions for ULN2003 and 28BYJ-48 motor control
#define IN1 D3  // GPIO0 -> IN1 on ULN2003
#define IN2 D4  // GPIO2 -> IN2 on ULN2003
#define IN3 D5  // GPIO14 -> IN3 on ULN2003
#define IN4 D6  // GPIO12 -> IN4 on ULN2003

unsigned long previousMillis = 0; // Variable to store the last time motor state was changed
const long interval = 5000;        // Interval for running the motor (5 seconds)

bool motorRunning = false;  // Motor status: true means running, false means stopped

void setup() {
  // Set motor control pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {
  unsigned long currentMillis = millis();

  // Check if it's time to toggle motor state (5 seconds running, 5 seconds stopped)
  if (currentMillis - previousMillis >= interval) {
    // Save the last time the motor state was changed
    previousMillis = currentMillis;

    if (motorRunning) {
      // Stop the motor after 5 seconds
      motorRunning = false;
      stopMotor();
    } else {
      // Start the motor after 5 seconds of stopping
      motorRunning = true;
      rotateMotor();  // Rotate motor for 5 seconds
    }
  }

  // If the motor is running, keep rotating it
  if (motorRunning) {
    rotateMotor();
  }
}

// Function to rotate the motor (full-step sequence)
void rotateMotor() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(5);  // Adjust delay to control motor speed
  
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(5);
  
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  delay(5);
  
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  delay(5);
}

// Function to stop the motor by setting all control pins LOW
void stopMotor() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
