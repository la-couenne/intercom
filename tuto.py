#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Ce script fonctionne avec 2 interphones, par souci de clarté du code je n'ai pas mis la partie de gestion de plusieurs interphones avec
le bouton encodeur rotatif ni le bouton qui rend ce poste "absent". Pour + d'info sur l'encodeur rotatif voir le tuto dans les sources.

Fonctionnement:
Lorsqu'on appuie sur le bouton "Parler" on génère un flux audio en ssh qu'on lit sur le terminal destinataire.
Le fait de relâcher ce bouton, termine le flux.

Quand on appuie sur le bouton "Buzzer" pour faire sonner l'interphone qu'on appelle: en fait on crée un fichier appelé "sonne" sur le poste
distant. Celui-ci check la présence de ce fichier en boucle, quand il existe il fait sonner son buzzer avant de supprimer le fichier "sonne"

Pour terminer, j'utilise le synthétiseur vocal pico2wave pour générer un son lors d'erreurs (Surtout utilisé si on tente de communiquer
avec un interphone qui a enclenché son bouton "Absent" cela génère une phrase comme quoi il est impossible de le contacter..)

### La détection 'offline' du terminal destinataire n'a pas encore été fait ###
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
os.system('pico2wave -l fr-FR -w 0.wav "Bienvenue sur le terminal daline. il est prêt a fonctionner." && aplay 0.wav && rm 0.wav')


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
