#include <Arduino.h>
#include <math.h>

// LED infravermelho no D8, coletor do fototransistor no A0.
// Versão corrigida do sketch usado no ensaio (ensaio_2026-10-06/main.cpp).
// O cálculo é o mesmo; mudou só a impressão:
//   - formato "sinal,mm", o que o plot_serial.py do roteiro reconhece como duas colunas
//     (o formato "sinal: X,  distancia: Y" era descartado pelo script);
//   - com sinal zero a distância é "nan", e não 0 (ver abaixo).
const int PIN_LED = 8;
const int PIN_ADC = A0;

unsigned long t_on_ms = 1000;
unsigned long t_off_ms = 1000;

// Ganhos da planilha (ajuste em 20-100 mm), arredondados como no ensaio.
const float g0 = 13.46;  // intercepto (mm)
const float g1 = 308;    // inclinação (mm * contagem^0,5)

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

  Serial.print(sinal);
  Serial.print(',');
  if (sinal > 0) {
    Serial.println(g0 + g1 / sqrt((float)sinal), 2);
  } else {
    // Sinal zero: nenhuma reflexão acima da luz ambiente, logo nenhuma distância medida.
    // "0" diria que o alvo encosta no sensor -- o oposto do que aconteceu. "nan" diz
    // "não medido": o plot_serial.py o lê como float('nan') e o gráfico fica com uma
    // lacuna nesse ponto, em vez de um valor falso.
    Serial.println("nan");
  }
}
