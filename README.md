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

# The python code
```shell
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Ce script fonctionne avec 2 interphones

Fonctionnement:
Lorsqu'on appuie sur le bouton "Parler" on génère un flux audio en ssh qu'on lit sur le terminal destinataire.
Le fait de relâcher ce bouton, termine le flux.

Quand on appuie sur le bouton "Buzzer" pour faire sonner l'interphone qu'on appelle: en fait on crée un fichier appelé "sonne" sur le poste
distant. Celui-ci check la présence de ce fichier en boucle, quand il existe il fait sonner son buzzer avant de supprimer le fichier "sonne"

Pour terminer, j'utilise le synthétiseur vocal pico2wave pour générer un son lors d'erreurs (Surtout utilisé si on tente de communiquer
avec un interphone qui a enclenché son bouton "Absent" cela génère une phrase comme quoi il est impossible de le contacter..)
'''
import RPi.GPIO as gpio
import time
import os

# Configuration des variables
ce_terminal = 'a' # ce script est sur le terminal rasptalk-a
destinataire = 'j' # ce script envoie sur -j (sera modifiable avec le bouton rotatif)
etat_absent = 0 # etat du bouton absent (1 si bouton enfoncé)
etat_parler = 0 # etat du bouton parler (rec)
etat_buzzer = 0
print("- - - Ce terminal est: " + ce_terminal + " et notre destinataire: " + destinataire + " - - -")

# on definit les numero des gpio
# Les Entrées (les boutons)
bouton_absent = 18
bouton_parler = 23
bouton_buzzer = 24
bouton_shutdown = 25
bouton_select1 = 16
bouton_select2 = 21
# Les Sorties (les leds)
le_buzzer = 22
led_absent = 17
led_parle = 27
led_rec = 5
led_posteA = 6
led_posteB = 13
led_posteC = 19
led_posteD = 26

gpio.setmode(gpio.BCM) # on utilise les Gpio en mode BCM
gpio.setup(bouton_absent, gpio.IN) # on défini ces ports comme entrées pour lire les positions des boutons
gpio.setup(bouton_parler, gpio.IN)
gpio.setup(bouton_buzzer, gpio.IN)
gpio.setup(bouton_shutdown, gpio.IN)
gpio.setup(bouton_select1, gpio.IN)
gpio.setup(bouton_select2, gpio.IN)

gpio.setup(led_absent, gpio.OUT) # et ceux-ci comme sorties pour allumer/éteindre les led
gpio.setup(le_buzzer, gpio.OUT)
gpio.setup(led_parle, gpio.OUT)
gpio.setup(led_rec, gpio.OUT)
gpio.setup(led_posteA, gpio.OUT)
gpio.setup(led_posteB, gpio.OUT)
gpio.setup(led_posteC, gpio.OUT)
gpio.setup(led_posteD, gpio.OUT)

# On génère un son de bienvenue avec le synthétiseur vocal pico2wave
os.system('pico2wave -l fr-FR -w 0.wav "Bienvenue sur ce terminal. il est prêt a fonctionner." && aplay 0.wav && rm 0.wav')


while True: # boucle infinie
    # Gestion bouton parler
    if(gpio.input(bouton_parler) == True): # si le "bouton parler" est pressé: (Parfois mettre False au lieu de True si notre bouton est off (on) ou on (off) c'est à dire qu'il coupe quand on appuie..
        if etat_absent == 0: # etat du bouton absent (ici le terminal n'est pas sur absent)
            gpio.output(led_rec, gpio.HIGH) # on allume la led rec
            if etat_parler == 0: # si le bouton rec n'a pas déjà été pressé -> on envoie un flux audio par ssh
                etat_parler = 1 # on met la variable à 1
                print("Le terminal desinataire n'est pas absent -> envoi du flux audio")
                os.system('sudo ./record-' + destinataire + '.py &') # on execute record-j.py en arrière plan, et on kill son processus quand on relâche le bouton "parler"
            else: # le bouton rec a déjà été pressé dans une autre boucle -> on ne fait rien
                print ("le bouton rec a déjà été pressé on ne fait rien car le flux audio est déjà en cours")
        else: # si etat du bouton absent = 1
            # On génère un son d'erreur pour prévenir que personne ne peut nous contacter
            os.system('pico2wave -l fr-FR -w 0.wav "Votre bouton, absent, est effoncé, il est impossible de communiquer." && aplay 0.wav && rm 0.wav')
    else: # si le "bouton parler" n'est pas pressé
        if etat_parler == 1: # le bouton rec n'était pas encore relâché -> on arrête l'enregistrement en tuant son processus
            etat_parler = 0 # on remet la variable à 0
            gpio.output(led_rec, gpio.LOW) # on éteint la led rec
            print ("Le bouton rec vient d'être relâché -> on tue les processus ayant comme nom: arecord")
            os.system('killall arecord')


    # Gestion bouton absent
    if(gpio.input(bouton_absent) == True): # si le "bouton absent" est pressé:
        if etat_parler == 0: # on check qu'on ne soie pas en train de parler (si c'est le cas on ne fait rien)
            if etat_absent == 0: # si on ne parle pas et on est pas deja absent
                print("Le bouton absent est enfoncé et on est pas en mode absent: etat_absent -> 1")
                etat_absent = 1 # on bascule l'état absent à 1
                # on envoie le fichier "absent-ce_terminal" sur tous les destinataires
                os.system('ssh pi@rasptalk-' + destinataire + ' "touch /home/pi/rasptalk/absent-' + ce_terminal + '"')
                gpio.output(led_absent, gpio.HIGH) # on allume la led absent
                time.sleep(0.8)
            else: # si on ne parle pas mais on est deja absent
                print("Le bouton absent est enfoncé mais on est deja en mode absent: etat_absent -> 0")
                etat_absent = 0 # on bascule l'état absent à 0
                os.system('ssh pi@rasptalk-' + destinataire + ' "rm /home/pi/rasptalk/absent-' + ce_terminal + '"')
                gpio.output(led_absent, gpio.LOW) # on éteint la led absent
                time.sleep(0.8)
        if etat_parler == 1: # on a enfoncé le bouton "absent" alors qu'on est déjà en train de parler
            print("On ne tient pas compte de l'enfoncement du bouton absent car le bouton parle est aussi pressé")


    # Gestion bouton buzzer
    if(gpio.input(bouton_buzzer) == False): # si le "bouton buzzer" est pressé:
        if etat_absent == 1: # si on est absent
            # On génère un son d'erreur pour prévenir que personne ne peut nous contacter
            os.system('pico2wave -l fr-FR -w 0.wav "Votre bouton, absent, est effoncé, il est impossible de communiquer." && aplay 0.wav && rm 0.wav')
        else: # si "bouton buzzer" est pressé et si on est pas "absent"
            # On génère un son avec le buzzer du correspondant en créant le fichier "sonne"
            os.system('ssh pi@rasptalk-' + destinataire + ' "touch /home/pi/rasptalk/sonne"')
            print("Le fichier sonne a été créé sur pi@rasptalk-" + destinataire + " pour faire sonner son buzzer")
            time.sleep(0.8)


    # Gestion bouton shutdown
    if(gpio.input(bouton_shutdown) == False): # si le "bouton shutdown" est pressé:
            print("Bouton shutdown -> au revoir!")
            # On génère un son de fin de programme
            os.system('pico2wave -l fr-FR -w 0.wav "Le système va séteindre. Attendez au moins 2 minute avant de retirer la prise." && aplay 0.wav && rm 0.wav')
            for i in range(0,4): # on fait cligoter 4x toutes les leds
                gpio.output(led_absent, gpio.LOW)
                gpio.output(led_parle, gpio.LOW)
                gpio.output(led_rec, gpio.LOW)
                gpio.output(led_posteA, gpio.LOW)
                gpio.output(led_posteB, gpio.LOW)
                gpio.output(led_posteC, gpio.LOW)
                time.sleep(0.4)
                gpio.output(led_absent, gpio.HIGH)
                gpio.output(led_parle, gpio.HIGH)
                gpio.output(led_rec, gpio.HIGH)
                gpio.output(led_posteA, gpio.HIGH)
                gpio.output(led_posteB, gpio.HIGH)
                gpio.output(led_posteC, gpio.HIGH)
                time.sleep(0.4)
            os.system('sudo shutdown -h now') # on éteint le système


    # Gestion fichier "sonne"
    if os.path.isfile("/home/pi/rasptalk/sonne"): # On check si on a reçu un fichier "sonne"
        print("Oh il y a un fichier 'sonne' -> on déclenche le buzzer")
        os.system('rm /home/pi/rasptalk/sonne') # on efface le fichier "sonne"
        gpio.output(le_buzzer, gpio.HIGH) # on allume le buzzer
        time.sleep(0.7)
        gpio.output(le_buzzer, gpio.LOW) # on l'éteint


    time.sleep(0.3)  # pour diminuer la charge CPU
```
When we press the “Talk” button the above program launches the script below, in this way the infinite loop can continue and wait for the moment when we release the button and thus kill the process of this 2nd script:
```shell
#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Quand on enfonce le bouton "parler" le programme principal lance ce script en arrière plan avec la commande:
os.system('sudo ./record-a.py &')

De cette façon, la boucle infinie du programme principal peut continuer et checker le moment où l'on relâche le bouton "parler" et à ce moment on tuera son processus avec la commande:
os.system('killall arecord')
'''
import os
os.system('if [ -f "/home/pi/rasptalk/absent-a" ]; then pico2wave -l fr-FR -w 0.wav "Le bouton, absent, est effoncé chez votre correspondant. Il est impossible de lui parler."; aplay 0.wav; rm 0.wav; else arecord -D plughw:1 -f dat | ssh -C pi@rasptalk-a aplay -f dat; fi')
```

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

