# Multi-station wifi intercom with a Raspberry Pi

![interphone_titre](https://user-images.githubusercontent.com/38251711/119101090-e93cf600-ba18-11eb-8574-0ca27c2b0b2e.png)

I suggest you discover an object that children really enjoy, but that can also be adapted as a door intercom.

I searched a lot for a way to stream audio over wifi, and finally I carried out my project in the way that seemed easiest to me: using an SSH connection and the arecord / aplay commands of the ALSA driver from the sound output of our Raspberry Pi. The principle is simple, we press the button when we speak, and our interlocutor hears us 🙂 Otherwise I use a USB micophone, an amplified speaker, and a Python file.

# List of equipment (for an intercom)
1 Raspberry Pi
1 Micro SD Card
1 AC adapter (I used a 5v 6A to also power the amp)
1 USB microphone
1 8 Ohms 10W speaker (depending on the amp)
1 amplifier for the speaker (I used that of Adafruit 20W MAX9744)
1 cable with 2 Jack sockets
1 10mm red LED (emission indicator)
2 push buttons at least (one to talk and one to turn off the Raspberry)
1 resistance of 100 Ohms
1 resistance of 10 KOhms
1 bakelite plate

# The electronic diagram
