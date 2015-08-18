#! /bin/sh

scriptspath=`dirname $0`
for script in `ls "$scriptspath" | awk '/^[0-9]+-/'`; do
    "$scriptspath/$script"
done
