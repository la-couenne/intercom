#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
script de test
'''
import RPi.GPIO as gpio
import time
import os

print('Début')

gpio.setmode(gpio.BCM) # on utilise les Gpio en mode BCM

# On défini ces ports comme entrées pour lire la position du bouton
gpio.setup(24, gpio.IN) # Bouton Buzzer
gpio.setup(18, gpio.IN) # Bouton Absent
gpio.setup(23, gpio.IN) # Bouton Parler
gpio.setup(25, gpio.IN) # Shutdown
gpio.setup(21, gpio.IN) # Bouton Selection

# et ceux-ci comme sorties pour allumer les led de controle
gpio.setup(17, gpio.OUT) # Led Absent
gpio.setup(27, gpio.OUT) # Led Parle
gpio.setup(22, gpio.OUT) # Buzzer
gpio.setup(5, gpio.OUT) # Led REC
gpio.setup(6, gpio.OUT) # Led Poste A
gpio.setup(13, gpio.OUT) # Led Poste B
gpio.setup(19, gpio.OUT) # Led Poste C

while True: # boucle infinie
	if(gpio.input(24) == False): # si le bouton buzzer est pressé:
		print("Le Bouton BUZZER est pressé")
		gpio.output(22, gpio.HIGH) # on fait sonner le buzzer
		time.sleep(0.5)
		gpio.output(22, gpio.LOW) # on eteint le buzzer



        if(gpio.input(18) == True): # si le bouton absent est pressé:
                print("Le Bouton ABSENT est pressé")
                gpio.output(17, gpio.HIGH) # on allume la led
                time.sleep(1)
                gpio.output(17, gpio.LOW) # on eteint la led



        if(gpio.input(23) == True): # si le bouton parler est pressé:
                print("Le Bouton PARLER est pressé")
                gpio.output(27, gpio.HIGH) # on allume la led
                time.sleep(1)
                gpio.output(27, gpio.LOW) # on eteint la led



        if(gpio.input(25) == False): # si le bouton shutdown est pressé:
                print("Le Bouton SHUTDOWN est pressé")
                gpio.output(6, gpio.HIGH) # on allume les led
		gpio.output(13, gpio.HIGH)
		gpio.output(19, gpio.HIGH)
                time.sleep(1)
                gpio.output(6, gpio.LOW) # on eteint les led
		gpio.output(13, gpio.LOW)
		gpio.output(19, gpio.LOW)



        if(gpio.input(21) == False): # si le bouton selection est pressé:
                print("Le Bouton SELECTION est pressé")
                gpio.output(5, gpio.HIGH) # on allume la led REC pour tester
                time.sleep(0.5)
                gpio.output(5, gpio.LOW) # on eteint la led



	print("")
	time.sleep(0.3)  # pour diminuer la charge CPU
