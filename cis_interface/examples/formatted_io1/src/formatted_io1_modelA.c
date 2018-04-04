#include <stdio.h>
// Include methods for input/output channels
#include "CisInterface.h"

#define MYBUFSIZ 1000

int main(int argc, char *argv[]) {
  // Initialize input/output channels
  cisInput_t in_channel = cisInputFmt("inputA", "%6s\t%d\t%f\n");
  cisOutput_t out_channel = cisOutputFmt("outputA", "%6s\t%d\t%f\n");

  // Declare resulting variables and create buffer for received message
  int flag = 1;
  char name[MYBUFSIZ];
  int count = 0;
  double size = 0.0;

  // Loop until there is no longer input or the queues are closed
  while (flag >= 0) {
  
    // Receive input from input channel
    // If there is an error, the flag will be negative
    // Otherwise, it is the size of the received message
    flag = cisRecv(in_channel, &name, &count, &size);
    if (flag < 0) {
      printf("Model A: No more input.\n");
      break;
    }

    // Print received message
    printf("Model A: %s, %d, %f\n", name, count, size);

    // Send output to output channel
    // If there is an error, the flag will be negative
    flag = cisSend(out_channel, name, count, size);
    if (flag < 0) {
      printf("Model A: Error sending output.\n");
      break;
    }

  }
  
  return 0;
}

