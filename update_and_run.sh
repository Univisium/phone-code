#!/bin/bash

# rainbow boot message
text=" multi play system starting "
colors=(
  "\033[31m"  # red
  "\033[33m"  # yellow
  "\033[32m"  # green
  "\033[36m"  # cyan
  "\033[34m"  # blue
  "\033[35m"  # magenta
  "\033[95m"  # light magenta
  "\033[94m"  # light blue
)

len=${#text}
for ((i=0; i<len; i++)); do
  char="${text:$i:1}"
  color_index=$(( i % ${#colors[@]} ))
  printf "%b%s" "${colors[$color_index]}" "$char"
done
printf "\033[0m\n\n"

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
python3 multi_play.py
python3 button_test.py

echo
read -p "Press Enter to close..."

