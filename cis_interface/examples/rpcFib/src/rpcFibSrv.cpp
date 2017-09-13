
#include "PsiInterface.hpp"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>


int main(int argc, char *argv[]) {

  float timeSleep = atof(argv[1]);
  printf("Hello from C++ rpcFibSrv: sleeptime = %f\n", timeSleep);
  
  // Create server-side rpc conneciton
  PsiRpcServer rpc("srv_fib", "%d", "%d %d");

  // Continue receiving requests until error occurs (the connection is closed
  // by all clients that have connected).
  int input;
  while (1) {
    int ret = rpc.recv(0, &input);
    if (ret < 0) {
      printf("rpcFibSrv(CPP): end of input\n");
      break;
    }

    // Compute fibonacci number
    printf("rpcFibSrv(CPP): <- input %d", input);
    int result = 1;
    int prevResult = 1;
    int prevPrev = 0;
    int idx = 1;
    while(idx++ < input){
      result = prevResult + prevPrev;
      prevPrev = prevResult;
      prevResult = result;
    }
    printf(" ::: ->(%2d %2d)\n", input, result);

    // Sleep and then send response back
    if (timeSleep) 
      sleep(timeSleep);
    rpc.send(0, input, result);
  }

  printf("Goodbye from C++ rpcFibSrv\n");
  
}

