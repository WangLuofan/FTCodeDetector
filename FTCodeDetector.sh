#!/bin/sh


py3=`which python3`

if [ -z "$py3" ]
then
	echo "Python3 Not Found.\n"
	exit -1
fi

if [ $# -lt 1 ]
then
	echo "Parameter Error.\n"
	exit -1
fi

$py3 $1 $2 $3