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
![schema_600px](https://user-images.githubusercontent.com/38251711/119102653-8b111280-ba1a-11eb-88a5-2f3cf12088b1.png)

# System configuration
We change the names of the raspberries to “rasptalk-a”, “rasptalk-b”, “rasptalk-c” …
```shell
$> sudo nano /etc/hostname -> modifier le nom
$> sudo nano /etc/hosts -> modifier le nom (tout en bas)
```

# Setting up an SSH certificate
To be able to use an ssh connection without having to enter a password, we will create a certificate in the form of a private key, a public key.
If it does not exist, create the .ssh directory
```shell
$> mkdir $HOME/.ssh
$> sudo chmod 700 $HOME/.ssh
```
Go to the .ssh directory
```shell
$> cd $HOME/.ssh
```
We will generate our keys, -b 4096 increases the security of your key instead of 2096 by default, the -C “comment” will be used to locate the public key among others in the ~ / .ssh / authorized_keys file which we will create later on the server.
```shell
$> ssh-keygen -b 4096 -C "pi@rasptalk-a"
```
The command asks us to indicate the name of the file in which to save the keys:
We just do [ENTER] so that the silk key generated and placed in the .ssh / id_rsa folder
Then we leave the passphrase empty so that he does not ask for it
Here we are with a private key (id_rsa) and a public key (id_rsa.pub)

The private key must be kept in the .ssh directory and the public key is the one to put on the server that wants to connect.

We must now add the public key to the authorized_keys file located in the /home/user/.ssh folder of the server:
```shell
$> cat id_rsa.pub | ssh <nom_utilisateur>@<adresse_ip> 'cat >> ~/.ssh/authorized_keys'
```
The line is appended to the ~ / .ssh / authorized_keys file on the server in the form: ssh-rsa encrypted-key> comment

We will finish with the modification of the configuration of the SSH service: (therefore locally not on the server ..)
```shell
$> sudo nano /etc/ssh/sshd_config
```
We uncomment the following lines:
```shell
PubkeyAuthentication yes
RSAAuthentication yes
AuthorizedKeysFile %h/.ssh/authorized_keys
```
Now one last thing, if we want a script executed by root to also be able to use the ssh login without a password:
We define a password for the raspberry administrator:
```shell
$> sudo passwd root
```
Then we connect as root with the command:
```shell
$> su
```
Check that the /root/.ssh folder exists (if it does not exist: mkdir /root/.ssh)
Give it these rights:
```shell
$> chmod 700 /root/.ssh
```
Then return to $ HOME / .ssh
```shell
$> cd $HOME/.ssh
```
Upload the authorized_keys and id_rsa files to /root/.ssh
```shell
$> cp authorized_keys /root/.ssh
$> cp id_rsa /root/.ssh
```
Finally we restart ssh:
```shell
$> sudo service ssh restart
```

# A synthesizer to vocalize errors
Installation of a speech synthesizer that reads errors, for example if the correspondent is turned off:
```shell
$> sudo apt-get install libttspico-utils
```
test creating the .wav file and playing the file:
```shell
$> pico2wave -l fr-FR -w fichier.wav "Bienvenue en cette belle journée!"
$> aplay fichier.wav
```

# Configure the microphone
![2-rasp](https://user-images.githubusercontent.com/38251711/119105932-1b048b80-ba1e-11eb-9e6d-55615022851d.png)
check that the microphone is seen on the USB port:
```shell
$> lsusb
```
which gives for example: Bus 001 Device 008: ID 0d8c:0139 C-Media Electronics, Inc.

We can verify that the user pi is in the audio group:
```shell
$> groups pi
```
If not, add it with:
```shell
$> sudo usermod -a -G audio pi
```

 On va configurer le port du microphone et la carte audio:
```shell
$> alsamixer
```

Gives a setting diagram, use F6 to select the sound card:
bcm2835 is the raspberry (for the jack & hdmi output)
and for the mic input: USB PnP sound device with the card number: 1
Now on the diagram we can raise the sound of the HP and the mic at least to 50%
On the far right we have the automatic gain control by pressing the M key (I leave it auto)

Finally save these settings:
```shell
$> sudo alsactl store 1
```
1 is your card number.
To test the recording: a 4-second 8-bit sound (coming from device 1: -D plughw: 1) and you play it with aplay:
```shell
$> arecord -D plughw:1 -d 4 test.wav
$> aplay test.wav
```

Here is one last little thing to pay attention:
if you use a jack for sound like me, we put the audio output of the raspberry in analog and not on HDMI (right button on the HP next to the clock)

# Boot directly from a hard drive
![3-ddur](https://user-images.githubusercontent.com/38251711/119107104-3d4ad900-ba1f-11eb-8121-92210eeb7dfc.png)
I personally have used a pidrive, but it is possible to use an old hard drive or even a USB key, here is a good tutorial:
https://www.framboise314.fr/boot-simplifie-sur-usb-avec-les-raspberry-pi-1-2-et-3

# Sources
alsa: https://wiki.debian.org/fr/ALSA
voice synthesizer: https://www.framboise314.fr/donnez-la-parole-a-votre-raspberry-pi/
ssh connection: https://doc.ubuntu-fr.org/ssh
scp without password: https://geekeries.org/2016/10/transferts-scp-sans-mot-de-passe
amplification module: https://www.adafruit.com/product/1752

# enjoy :-)

