#!/bin/bash -x

for f in $* ; do
    sed -i $f 's/\n/ /'
done
