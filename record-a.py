#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Le destinataire est dans le nom du fichier: "record-a.py" se connecte en ssh sur le destinataire "a"
C'est juste l'exécution de arecord, car je ne parvient pas à l'exécuter en arrière plan avec &
### RETESTER AVEC & car j'avais testé avec $.. ###
En le lançant depuis un autre script python, je peux tuer le processus contenant "arecord"
'''
import os
os.system('if [ -f "/home/pi/rasptalk/absent-a" ]; then pico2wave -l fr-FR -w 0.wav "Le bouton, absent, est effoncé chez votre correspondant. Il est impossible de lui parler."; aplay 0.wav; rm 0.wav; else arecord -D plughw:1 -f dat | ssh -C pi@rasptalk-a aplay -f dat; fi')
