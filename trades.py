# -*- coding: utf-8 -*-
'''
Created on 15 de agosto de 2020

@author: Rodrigo Nunes

	Descrição
    Histórico de negociações realizadas.
'''
import hashlib
import json

from http import client

class Trades:
	REQUEST_HOST = 'www.mercadobitcoin.net'

	def __init__(self,coin='xrp'):
		REQUEST_PATH='/api/'+coin.upper()+'/trades/'

		try:
			conn = client.HTTPSConnection(self.REQUEST_HOST)
			conn.request("GET", REQUEST_PATH)
			resp = conn.getresponse()
			resp = resp.read()
			self.result = json.loads(resp)
			#print(json.dumps(self.result, indent=4))
		finally:
			if conn:
				conn.close()

	# index 999 refere-se a última negociação.

	# Obtém o Id da negociação com base no indíce
	def getId(self,index=999):
		return self.result[index]['tid']
	
	# Obtém a data da negociação com base no indíce
	def getDate(self,index=999):
		return self.result[index]['date']

	# Obtém o tipo de negociação com base no indíce buy=compra sell=venda
	def getType(self,index=999):
		return self.result[index]['type']

	# Obtém o preço de negociação com base no indíce
	def getPrice(self,index=999):
		return self.result[index]['price']

	# Obtém a quantidade da moeda negociada com base no indíce
	def getAmount(self,index=999):
		return self.result[index]['amount']