import json
import uuid
from yookassa import Configuration,Payment
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

Configuration.account_id = os.getenv('account_id')
Configuration.secret_key = os.getenv('secret_key')

def payment(value,description):
	payment = Payment.create({
		"amount": {
			"value": f"{value}",
			"currency": "RUB"
		},
		"payment_method_data": {
			"type": "bank_card"
		},
		"confirmation": {
			"type": "redirect",
			"return_url": "https://t.me/elbrus_reminder_tim_bot"
		},
		"capture": True,
		"description": f"{description}"
	})
	return json.loads(payment.json())


async def check_payment(payment_id):
	payment = json.loads((Payment.find_one(payment_id)).json())
	while payment['status'] == 'pending':
		payment = json.loads((Payment.find_one(payment_id)).json())
		await asyncio.sleep(3)

	if payment['status']=='succeeded':
		return True
	else:
		return False