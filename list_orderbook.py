# -*- coding: utf-8 -*-
'''
Created on 10 de julho de 2020

@author: Rodrigo Nunes

	Descrição
	Retorna informações do livro de negociações
	(orderbook) do Mercado Bitcoin para o par de moedas (coin_pair)
	informado. Diferente do método orderbook público descrito em
	/api-doc/#method_trade_api_orderbook, aqui são fornecidas
	informações importantes para facilitar a tomada de ação de
	clientes TAPI e sincronia das chamadas. Dentre elas, o
	número da última ordem contemplada (latest_order_id) e número
	das ordens do livro (order_id), descritos abaixo. Importante
	salientar que nesse método ordens de mesmo preço não são
	agrupadas como feito no método público.
'''


import hashlib
import hmac
import json
import time
import userinfo

from http import client
from urllib.parse import urlencode

class ListOrderBook:
	# Constantes
	MB_TAPI_ID = userinfo.id
	MB_TAPI_SECRET = userinfo.secret
	REQUEST_HOST = 'www.mercadobitcoin.net'
	REQUEST_PATH = '/tapi/v3/'


	# Nonce
	# Para obter variação de forma simples
	# timestamp pode ser utilizado:
	#tapi_nonce = str(int(time.time()))

	def __init__(self,coin_pair,tapi_nonce=str(int(time.time()))):
		# Parâmetros
		params = {
			'tapi_method': 'list_orderbook',
			'tapi_nonce': tapi_nonce,
			'coin_pair': coin_pair
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

			self.result = json.loads(resp)

			#print(json.dumps(self.result, indent=4))

		finally:
			if conn:
				conn.close()


	# Funções que retornam informações com as ordens de compra.
	def getOrderbookBidsID(self,index=0):
		'''
		bids: Lista de ordens de compra (bid) abertas, ordenadas pelo maior preço.
		'''
		return self.result['response_data']['orderbook']['bids'][index]['order_id']

	def getOrderbookBidsQuantity(self,index=0):
		'''
		quantity: Quantidade disponível para compra ao preço de limit_price.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orderbook']['bids'][index]['quantity']

	def getOrderbookBidsLimitPrice(self,index=0):
		'''
		limit_price: Preço unitário de compra.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orderbook']['bids'][index]['limit_price']

	def getOrderbookBidsIsOwner(self,index=0):
		'''
		is_owner: Informa se ordem pertence ao proprietário da chave TAPI.
		Tipo: Booleano
		Domínio de dados:
		true : Pertence ao proprietário da chave TAPI
		false : Não pertence ao proprietário da chave TAPI
		'''
		return self.result['response_data']['orderbook']['bids'][index]['is_owner']


	# Funções que retornam informações com as ordens de venda
	def getOrderbookAsksID(self,index=0):
		'''
		bids: Lista de ordens de venda (asks) abertas, ordenadas pelo menor preço.
		'''
		return self.result['response_data']['orderbook']['asks'][index]['order_id']

	def getOrderbookAsksQuantity(self,index=0):
		'''
		quantity: Quantidade disponível para venda ao preço de limit_price.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orderbook']['asks'][index]['quantity']

	def getOrderbookAsksLimitPrice(self,index=0):
		'''
		limit_price: Preço unitário de venda.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orderbook']['asks'][index]['limit_price']

	def getOrderbookAsksIsOwner(self,index=0):
		'''
		is_owner: Informa se a ordem pertence ao proprietário da chave TAPI.
		Tipo: Booleano
		Domínio de dados:
		true : Pertence ao proprietário da chave TAPI
		false : Não pertence ao proprietário da chave TAPI
		'''
		return self.result['response_data']['orderbook']['asks'][index]['is_owner']

	def getOrderbookLatestOrderId(self):
		'''
		latest_order_id: Última ordem contemplada no resultado de orderbook.
		Entende-se como ordem contemplada a última ordem criada e confrotada ao
		livro de acordo com o resultado retornado deste método. Assim, essa
		ordem pode ter sido executada ou não. A última ordem contemplada pode
		não estar presente no livro, ou por ter sido executada em sua totalidade
		ou por já ter sido cancelada em ação posterior a sua criação. Assim, é
		importante salientar que uma ordem cancelada, apesar de alterar o
		livro, não altera o valor deste campo.
		'''
		return self.result['response_data']['orderbook']['latest_order_id']
