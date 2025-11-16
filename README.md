# phone code

## Things you forget because smooth brained

* Editor is Sublime Text

# GitHub workflow

```bash
cd C:\Users\user\phone-code     # go to the project folder
git add .                       # add all changes
git commit -m "comment"         # create a commit
git push                        # upload to GitHub
```

# Do not forget to

* Install and update PipeWire and PulseAudio
* Make every Pi update the repo on boot and start the script automatically
* lsusb -v | grep -i (add tt to get the tt)

# Known bugs

* Playback only works correctly on the first three sound cards, the others show buffer issues
* Sound cards only activate after plugging something into the jack
* USB power dependency problems, probably solved by using a powered USB hub

# Testing the code

Run this to check syntax without running the script:

```bash
python -m py_compile multi_play.py
```
