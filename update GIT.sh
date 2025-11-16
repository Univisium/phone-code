#!/bin/bash

echo "start pulling script"
echo

cd /home/nachtdienst/phone-code || {
    echo "Directory not found, stopping"
    exit 1
}

git pull
echo "finished pulling script UwU"


