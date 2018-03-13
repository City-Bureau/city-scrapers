#!/bin/bash

REF=`git symbolic-ref HEAD --short 2>/dev/null`

if [ "$REF" == "master" ] ; then
  echo "Running on master; build will continue."
else
  echo "Not on the master branch; aborting."
  exit 1
fi
