# -*- coding: utf-8 -*-
'''
Created on 10 de julho de 2020

@author: Rodrigo Nunes

	cancel_order Descrição:
	Cancela uma ordem, de venda ou compra, de acordo com o ID e par de moedas informado.
	O retorno contempla o sucessoo ou não do cancelamento, bem como os dados e status
	atuais da ordem. Somente ordens pertencentes ao próprio usuário podem ser canceladas.
'''

import hashlib
import hmac
import json
import time
import userinfo

from place_sell_order import PlaceSellOrder


from http import client
from urllib.parse import urlencode

class CancelOrder:

	# Constante
	MB_TAPI_ID = userinfo.id
	MB_TAPI_SECRET = userinfo.secret
	REQUEST_HOST = 'www.mercadobitcoin.net'
	REQUEST_PATH = '/tapi/v3/'
    

	# Para obter variação de forma simples
	# timestamp pode ser utilizado:
	#tapi_nonce = str(int(time.time()))

	def __init__(self,coin_pair,order_id,tapi_nonce=str(int(time.time()))):
		self.coin_pair=coin_pair
		self.order_id=order_id
		self.tapi_nonce=tapi_nonce

		# Parâmetros
		params = {
			'tapi_method': 'cancel_order',
			'tapi_nonce': self.tapi_nonce,
			'coin_pair': self.coin_pair,
			'order_id': self.order_id
		}

		params = urlencode(params)

		# Gerar MAC
		params_string = self.REQUEST_PATH + '?' + params
		H = hmac.new(bytes(self.MB_TAPI_SECRET, encoding='utf8'), digestmod=hashlib.sha512)
		H.update(params_string.encode('utf-8'))
		tapi_mac = H.hexdigest()

		# Gerar cabeçalho da requisição
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'TAPI-ID': self.MB_TAPI_ID,
			'TAPI-MAC': tapi_mac
		}

		# Realizar requisição POST
		try:
			conn = client.HTTPSConnection(self.REQUEST_HOST)
			conn.request("POST", self.REQUEST_PATH, params, headers)

			# Mostra o resultado
			resp = conn.getresponse()
			resp = resp.read()

			result = json.loads(resp)

			#print(json.dumps(result, indent=4))
			conn.close()

		finally:
			if conn:
				conn.close()
