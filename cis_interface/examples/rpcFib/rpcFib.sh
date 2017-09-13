#!/bin/bash

export PSI_DEBUG="INFO"
export PSI_NAMESPACE="rpcFib"
export FIB_ITERATIONS="3"
export FIB_SERVER_SLEEP_SECONDS="0.01"

yaml1= 
yaml2= 
yaml3= 

# ----------------Your Commands------------------- #
case $1 in
    "" | -a | --all )
	echo "Running Python, Matlab, C integration"
	yaml1='rpcFibSrv_c.yml'
	yaml2='rpcFibCli_python.yml'
	yaml3='rpcFibCliPar_matlab.yml'
	;;
    -p | --python )
	echo "Running Python"
	yaml1='rpcFibSrv_python.yml'
	yaml2='rpcFibCli_python.yml'
	yaml3='rpcFibCliPar_python.yml'
	;;
    -m | --matlab )
	echo "Running Matlab"
	yaml1='rpcFibSrv_matlab.yml'
	yaml2='rpcFibCli_matlab.yml'
	yaml3='rpcFibCliPar_matlab.yml'
	;;
    -c | --gcc )
	echo "Running C"
	yaml1='rpcFibSrv_c.yml'
	yaml2='rpcFibCli_c.yml'
	yaml3='rpcFibCliPar_c.yml'
	;;
    --cpp | --g++ )
	echo "Running C"
	yaml1='rpcFibSrv_cpp.yml'
	yaml2='rpcFibCli_cpp.yml'
	yaml3='rpcFibCliPar_cpp.yml'
	;;
    * )
	echo "Running ", $1
	yaml=$1
	;;
esac

cisrun $yaml1 $yaml2 $yaml3

cat /tmp/fibCli.txt
