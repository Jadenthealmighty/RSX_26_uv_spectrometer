/*
 * Info based on C12880MA Spectrometer from Hamamatsu
 * Macro Definitions
 */

#include <Arduino.h>

#define SPEC_TRG         A0
#define SPEC_ST          A1
#define SPEC_CLK         A2
#define SPEC_VIDEO       A3

#define SPEC_CHANNELS    288
uint16_t data[SPEC_CHANNELS];

int integrateTime;
double delayTime;
int maxVal = 0;

// This is the exposure level, it ranges between 0-3 (inclusive) to vary between the different preset exposure levels
int expsrLev = 0;

// exposure too low
const int EXPSR_LOW = 200;
// exposure too high
const int EXPSR_HI = 400;

const int integrateClkVals[] = {1, 2000, 10000, 29000};
// The best values for the clock speed, note that each of these is divided by 5 for the final value for cycle time.
const int delayVals[] = {1, 5, 10, 20};



void setup(){
  pinMode(SPEC_CLK, OUTPUT);
  pinMode(SPEC_ST, OUTPUT);


  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, LOW);

  Serial.begin(115200);
  updateExpsrTime(0); //Lowest exposure time possible
  
}


void readSpectrometer(){

  // Start clock cycle and set start pulse to on
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK, LOW);

  digitalWrite(SPEC_ST, HIGH);
  delayMicroseconds(delayTime);

  //integration time start
  for(int i = 0; i < integrateTime; i++){

      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime); 
 
  }
  //integration time end


  /*
  * RSX specific: our spectrometer has an error where it the reading is off by
  * exactly two clock cycles. The following two cycles is a necessary correction
  * otherwise every reading is off by ~5 nm. Usually needs 86 but we need 88.
  */

  digitalWrite(SPEC_ST, LOW);
  for(int i = 0; i < 88; i++){
      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime); 
  }

  //Read from SPEC_VIDEO
  maxVal = 0;
  for(int i = 0; i < SPEC_CHANNELS; i++){
      data[i] = analogRead(SPEC_VIDEO);
      if (data[i] > maxVal){
        maxVal = data[i];
      }
      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime); 
  }


  // Signal to reset frame
  digitalWrite(SPEC_ST, HIGH);
  for(int i = 0; i < 7; i++){
      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);
  }

  // Exposure/integration time updating
  // uncomment for auto_exposure 
  
  // <START>

  // if (maxVal < EXPSR_LOW){
  //   expsrLev = (int) fmin(expsrLev + 1, 3);
  //   updateExpsrTime(expsrLev);
  // }
  // if (maxVal > EXPSR_HI){
  //   expsrLev = (int) fmax(expsrLev - 1, 0);
  //   updateExpsrTime(expsrLev);
  // }

  //<END>

  digitalWrite(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
}


/*
*  ----  Update exposure time (value of 0-3 inclusive), for externally setting exposure time--- 
*/
void updateExpsrTime(int expsrLevel){
  integrateTime = integrateClkVals[expsrLevel];
  delayTime = delayVals[expsrLevel] / 5;
}


void printData(){
  for (int i = 0; i < SPEC_CHANNELS; i++){
    Serial.print(data[i]);
    Serial.print(',');
  }
  Serial.print("\n");
}

void loop(){
  readSpectrometer();
  printData();
  delay(20);
}

