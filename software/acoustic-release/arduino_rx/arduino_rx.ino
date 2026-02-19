#include "src/flag_tones_to_symbol.h"
#include "src/update_flag_wake_up.h"

void setup() {
  Serial.begin(9600);

    // put your setup code here, to run once:
	float tab[] = {1.0, -1.0};

	int symbol = flag_tones_to_symbol(tab);
    Serial.print("test flag_tones_to_symbol : ");
    Serial.println(symbol);

	bool flag[] = {true, false, false};
	int index[] = {4, -1, -1};
	int threshold = 4;
	int index_flag_update = 1;

	int event = update_flag_wake_up(flag, index, index_flag_update, threshold);
	for (int i_tone = 0; i_tone < 3; i_tone++) {
	  Serial.println("==========================");
      Serial.print("test flag[i_tone] : ");
      Serial.println(flag[i_tone]);
      Serial.print("test index[i_tone] ");
      Serial.println(index[i_tone]);
	}

  Serial.print("test flag_tones_to_symbol EVENT: ");
  Serial.println(event);
}

void loop() {

}
