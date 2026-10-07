#include <Arduino.h>
#include <math.h>

// LED infravermelho no D8, coletor do fototransistor no A0.
const int PIN_LED = 8;
const int PIN_ADC = A0;

unsigned long t_on_ms = 1000;
unsigned long t_off_ms = 1000;

const float g0 = 13.46;  // intercepto
const float g1 = 308;  // inclinaçã0

void setup() {
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);
  Serial.begin(115200);
}

void loop() {
  // LED ligado
  digitalWrite(PIN_LED, HIGH);
  delay(t_on_ms);
  int adc_on = analogRead(PIN_ADC);

  // LED desligado
  digitalWrite(PIN_LED, LOW);
  delay(t_off_ms);
  int adc_off = analogRead(PIN_ADC);

  // Sinal devido ao infravermelho refletido
  int sinal = adc_off - adc_on;
  if (sinal < 0) sinal = 0;

  // Estimativa da distância
  if (sinal > 0) {
    float distancia = g0 + g1 / sqrt((float)sinal);

    // Saída: sinal,distancia
    Serial.print("sinal: ");
    Serial.print(sinal);
    Serial.print(",  distancia: ");
    Serial.println(distancia, 2);
  } else {
    // Sem sinal: não é possível calcular 1/sqrt(S)
    Serial.print("sinal: ");
    Serial.print(sinal);
    Serial.println(",  distancia: 0");
  }
}

