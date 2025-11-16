#!/bin/bash

echo "start pulling script"
echo

cd /home/nachtdienst/phone-code || {
    echo "Directory not found, stopping"
    exit 1
}

git pull
echo "finished pulling script UwU"
echo
echo
echo

echo "starting multi_play"
python3 button_test.py

echo
read -p "Press Enter to close..."

