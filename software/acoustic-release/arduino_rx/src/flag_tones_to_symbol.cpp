#include "flag_tones_to_symbol.h"

int flag_tones_to_symbol(float* flag){
  /*
  The flag_tones_to_symbol function takes a flag as input and
  returns the symbol that it represents.

  :param flag: Store the flag tones
  :return: The number of tones in the flag

  */

  return static_cast<int>(flag[1] - flag[0]);
}
