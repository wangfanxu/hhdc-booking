#!/usr/bin/env python
import signal
import sys
import time

from telegram.ext import Updater, CommandHandler

# from pyvirtualdisplay import Display


import main as bbdc


isChecking = False
chat_id = 134376933

def signal_handler(sig, frame):
	print('Stopping Updater...')
	isChecking = False
	updater.stop()
	# display.stop()
	
	bbdc.stopDisplay()
	print('Bye!')
	sys.exit(0)

def check(bot, update):
	global chat_id
	chat_id = update.message.chat_id
	print('chat_id = ' + str(chat_id))

	global isChecking
	while isChecking == True:
		time.sleep(1)
	isChecking = True
    # update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))
	update.message.reply_text('Checking...')

	(num_slots, msg) = bbdc.check_bbdc()

	update.message.reply_text(msg)

	isChecking = False


signal.signal(signal.SIGINT, signal_handler)

bbdc = bbdc.BBDCClass()
bbdc.startDisplay()

# display = Display(visible=1, size=(800, 600))
# display.start()

updater = Updater('888342541:AAFQ67Zmro2y2VjeZh13bLDWwBq4VMRk6CI')

updater.dispatcher.add_handler(CommandHandler('check', check))

updater.start_polling()
print('Started Polling...')

count = 1
while True:
	print( "======\n Check Count %d\n======="%(count) )
	if isChecking == False:
		isChecking = True
		(num_slots, msg) = bbdc.check_bbdc()

		if num_slots > 0:
			updater.bot.sendMessage(chat_id, msg)
		isChecking = False

	time.sleep(100)

	count = count+1



