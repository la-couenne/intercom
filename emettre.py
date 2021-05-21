#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Le bouton rec déclenche une suite d'événements:
on vérifie en local la présence du fichier "absent-x" (x=destinataire)
(quand on appuie sur le bouton "absent" ça doit envoyer le fichier "absent-x" (x=ce terminal) à tous par scp)
s'il existe on génère un son d'erreur avec pico2wave qu'on lit en local
si "absent-x" n'existe pas: on génère un flux audio en ssh qu'on lit sur le terminal destinataire
Le fait de relâcher le bouton rec, termine ce flux.

Pour la gestion de la sonnerie: le buzzer est activé si le fichier "sonne" est présent
Le bouton 'echo' est devenu inutile dans cette v2
La détection 'offline' du terminal destinataire qui déclenchera le son d'erreur /erreurs/offline.wav n'a pas encore été fait
Pour le faire on pourrait changer: au lieu de vérifier la non présence de "absent-x" on peut checker le fichier "present-x" (si bouton absent enfoncé: on rm present-x) donc si offline -> msg erreur
Il fonctionne pour 2 interphones (Jules & Aline), à modifier pour avoir >2 interphones
'''
import RPi.GPIO as gpio
import time
import os

# Configuration des variables
ce_terminal = 'a' # ce script est sur le terminal rasptalk-j
destinataire = 'j' # ce script envoie sur -a (sera modifiable avec le bouton rotatif)
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
led_rec = 27 # normalement 5
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

### ON DOIT POUVOIR CHECK PAR SSH QUI EST EN LIGNE (gestion des erreurs ssh) ###

while True: # boucle infinie
    # Gestion bouton parler  ### AJOUTER UN ANTI-ABUS DE 30 Sec?? ###
    if(gpio.input(bouton_parler) == False): # si le "bouton parler" est pressé:
        if etat_absent == 0: # etat du bouton absent (ici le terminal n'est pas sur absent)
            gpio.output(led_rec, gpio.HIGH) # on allume la led rec
            if etat_parler == 0: # si le bouton rec n'a pas déjà été pressé -> on envoie un flux audio par ssh
                etat_parler = 1 # on met la variable à 1
                print("Si terminal desinataire pas absent -> envoi flux") # si absent un fichier "absent-x" a été envoyé à tous par scp
                #os.system('if [ -f "/home/pi/rasptalk/absent-' + destinataire + '" ]; then pico2wave -l fr-FR -w 0.wav "Le bouton, absent, est effoncé chez votre correspondant. Il est impossible de lui parler."; aplay 0.wav; rm 0.wav; else arecord -D plughw:1 -f dat | ssh -C pi@rasptalk-' + destinataire + ' aplay -f dat; fi')
                os.system('sudo ./record-' + destinataire + '.py &')
                print ("")
            else: # le bouton rec a déjà été pressé dans une autre boucle -> on ne fait rien
                print ("le bouton rec a déjà été pressé on ne fait rien car le flux audio est déjà en cours")
                print ("")
        else: # si etat du bouton absent = 1
            # On génère un son d'erreur pour prévenir que personne ne peut nous contacter
            os.system('pico2wave -l fr-FR -w 0.wav "Votre bouton, absent, est effoncé, il est impossible de communiquer."')
            os.system('aplay 0.wav')
            os.system('rm 0.wav')
    else: # si le "bouton parler" n'est pas pressé
        if etat_parler == 1: # le bouton rec n'était pas encore relâché -> on arrête l'enregistrement en tuant son processus
            etat_parler = 0 # on remet la variable à 0
            gpio.output(led_rec, gpio.LOW) # on éteint la led rec
            print ("Le bouton rec vient d'être relâché -> on tue les processus ayant comme nom: arecord")
            os.system('killall arecord')
            print ("")


    # Gestion bouton absent
    if(gpio.input(bouton_absent) == False): # si le "bouton absent" est pressé:
        if etat_parler == 0:
            if etat_absent == 0: # si on ne parle pas et on est pas deja absent
                print("Le bouton absent est enfoncé et on est pas en mode absent: etat_absent -> 1")
                etat_absent = 1 # on bascule l'état absent à 1
                # on envoie le fichier "absent-ce_terminal" sur tous les destinataires
                os.system('ssh pi@rasptalk-' + destinataire + ' "touch /home/pi/rasptalk/absent-' + ce_terminal + '"')
                gpio.output(led_absent, gpio.HIGH) # on allume la led absent
                time.sleep(0.8)
                print("")
            else: # si on ne parle pas mais on est deja absent
                print("Le bouton absent est enfoncé mais on est deja en mode absent: etat_absent -> 0")
                etat_absent = 0 # on bascule l'état absent à 0
                os.system('ssh pi@rasptalk-' + destinataire + ' "rm /home/pi/rasptalk/absent-' + ce_terminal + '"')
                gpio.output(led_absent, gpio.LOW) # on éteint la led absent
                time.sleep(0.8)
                print("")
        if etat_parler == 1: # on a enfoncé le bouton "absent" alors qu'on est déjà en train de parler
            print("On ne tient pas compte de l'enfoncement du bouton absent car le bouton parle est aussi pressé")
            print("")


    # Gestion bouton buzzer
    if(gpio.input(bouton_buzzer) == False): # si le "bouton buzzer" est pressé:
        if etat_absent == 1: # si on est absent
            # On génère un son d'erreur pour prévenir que personne ne peut nous contacter
            os.system('pico2wave -l fr-FR -w 0.wav "Votre bouton, absent, est effoncé, il est impossible de communiquer."')
            os.system('aplay 0.wav')
            os.system('rm 0.wav')
        else: # si "bouton buzzer" est pressé et si on est pas "absent"
            # On génère un son avec le buzzer du correspondant en créant le fichier "sonne" avec scp
            os.system('ssh pi@rasptalk-' + destinataire + ' "touch /home/pi/rasptalk/sonne"')
            print("Le fichier sonne a été créé sur pi@rasptalk-" + destinataire + " pour faire sonner son buzzer")
            time.sleep(0.8)
            print("")


    # Gestion bouton shutdown
    if(gpio.input(bouton_shutdown) == False): # si le "bouton shutdown" est pressé:
            print("Bouton shutdown -> au revoir!")
            gpio.output(led_absent, gpio.HIGH) # on allume la led absent pour voir + ou - quand le rapsberry a finit de s'éteindre
            # ### FAUT-IL ENVOYER DES FICHIERS "absent-x" SUR TOUS LES TERMINAUX?! ###
            #os.system('sudo shutdown -h now')


    # Gestion fichier "sonne"
    if os.path.isfile("/home/pi/rasptalk/sonne"): # On check si on a reçu un fichier "sonne"
        print("Oh il y a un fichier 'sonne' -> on déclenche le buzzer")
        gpio.output(le_buzzer, gpio.HIGH) # on allume le buzzer
        time.sleep(0.7)
        gpio.output(le_buzzer, gpio.LOW) # on l'éteint
        os.system('rm /home/pi/rasptalk/sonne') # on efface le fichier 'sonne'
        print("")


    time.sleep(0.3)  # pour diminuer la charge CPU
