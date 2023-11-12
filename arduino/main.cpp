#include <iostream>
#include "./deps/flag_tones_to_symbol.h"
#include "./deps/update_flag_wake_up.h"
using namespace std;

int main(int argc, char** argv){
	float tab[] = {1.0, -1.0};

	int symbol = flag_tones_to_symbol(tab);
	cout << "test flag_tones_to_symbol : " << symbol << endl;

	bool flag[] = {true, false, false};
	int index[] = {4, -1, -1};
	int threshold = 4;
	int index_flag_update = 1;

	int event = update_flag_wake_up(flag, index, index_flag_update, threshold);
	for (int i_tone = 0; i_tone < 3; i_tone++) {
	    cout << " ========== " << endl;
	    cout << "test flag[i_tone] : " << flag[i_tone] << endl;
	    cout << "test index[i_tone] : " << index[i_tone] << endl;
	}
	cout << "test flag_tones_to_symbol EVENT: " << event << endl;

    return 0;
}