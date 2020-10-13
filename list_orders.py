# -*- coding: utf-8 -*-

'''
Created on 10 de julho de 2020

@author: Rodrigo Nunes

	Descrição
	Retorna uma lista de até 200 ordens, de acordo com os filtros informados,
	ordenadas pela data de última atualização. As operações executadas de cada
	ordem também são retornadas. Apenas ordens que pertencem ao proprietário da
	chave da TAPI são retornadas. Caso nenhuma ordem seja encontrada, é retornada
	uma lista vazia.
'''
import hashlib
import hmac
import json
import time
import userinfo

from http import client
from urllib.parse import urlencode

class ListOrders:

	# Constantes
	MB_TAPI_ID = userinfo.id
	MB_TAPI_SECRET = userinfo.secret
	REQUEST_HOST = 'www.mercadobitcoin.net'
	REQUEST_PATH = '/tapi/v3/'
	coin_pair = ''
	result = ''

	# Nonce
	# Para obter variação de forma simples
	# timestamp pode ser utilizado:
	#tapi_nonce = str(int(time.time()))
	


	def __init__(self,coin_pair,tapi_nonce=str(int(time.time())),status_list='',order_type=''):
		self.coin_pair = coin_pair
		self.tapi_nonce = tapi_nonce
		self.status_list = status_list
		self.order_type = order_type

		# Parâmetros
		params = {
			'tapi_method': 'list_orders',
			'tapi_nonce': self.tapi_nonce,
			'coin_pair': self.coin_pair,
			'status_list':'['+str(self.status_list)+']',
			'order_type':self.order_type
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


	def getOrdersId(self,index=0):
		'''
		order_id: Número de identificação da ordem, único por coin_pair.
		Tipo: Inteiro
		'''
		return self.result['response_data']['orders'][index]['order_id']

	def getOrdersCoinPair(self,index=0):
		'''
		coin_pair: Par de moedas.
		Tipo: String
		Domínio de dados:
		BRLBTC : Real e Bitcoin
		BRLBCH : Real e BCash
		BRLETH : Real e Ethereum
		BRLLTC : Real e Litecoin
		BRLXRP : Real e XRP (Ripple)
		BRLMBPRK01 : Real e Precatório MB SP01
		BRLMBPRK02 : Real e Precatório MB SP02
		BRLMBPRK03 : Real e Precatório MB BR03
		BRLMBPRK04 : Real e Precatório MB RJ04
		BRLMBCONS01 : Real e Cota de Consórcio
		BRLUSDC : Real e USDC (USD Coin)
		'''
		return self.result['response_data']['orders'][index]['coin_pair']

	def getOrdersOrderType(self,index=0):
		'''
		order_type: Tipo da ordem a ser filtrado.
		Tipo: Inteiro
		Domínio de dados:
		1 : Ordem de compra
		2 : Ordem de venda
		'''
		return self.result['response_data']['orders'][index]['order_type']

	def getOrdersStatus(self,index=0):
		'''
		status: Estado da ordem.
		Tipo: Inteiro
		Domínio de dados:
		2 : open : Ordem aberta, disponível no livro de negociações. Estado intermediário.
		3 : canceled : Ordem cancelada, executada parcialmente ou sem execuções. Estado final.
		4 : filled : Ordem concluída, executada em sua totalidade. Estado final.
		'''
		return self.result['response_data']['orders'][index]['status']

	def getOrdersHasFills(self,index=0):
		'''
		has_fills: Indica se a ordem tem uma ou mais execuções. Auxilia na identificação de ordens parcilamente executadas.
		Tipo: Booleano
		false : Sem execuções.
		true : Com uma ou mais execuções.
		'''
		return self.result['response_data']['orders'][index]['has_fills']

	def getOrdersQuantity(self,index=0):
		'''
		quantity: Quantidade da moeda digital a comprar/vender ao preço de limit_price.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orders'][index]['quantity']

	def getOrdersLimitPrice(self,index=0):
		'''
		limit_price: Preço unitário máximo de compra ou mínimo de venda.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orders'][index]['limit_price']

	def getOrdersExecutedQuantity(self,index=0):
		'''
		limit_price: Preço unitário máximo de compra ou mínimo de venda.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orders'][index]['executed_quantity']

	def getOrdersExecutedPriceAvg(self,index=0):
		'''
		executed_price_avg: Preço unitário médio de execução.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orders'][index]['execuder_price_avg']

	def getOrdersFee(self,index=0):
		'''
		fee: Comissão da ordem, para ordens de compra os valores são em moeda digital, para ordens de venda os valores são em Reais.
		Tipo: String
		Formato: Ponto como separador decimal, sem separador de milhar
		'''
		return self.result['response_data']['orders'][index]['fee']

	def getOrdersCreatedTimestamp(self,index=0):
		'''
		created_timestamp: Data e hora de criação da ordem.
		Tipo: String
		Formato: Era Unix
		'''
		return self.result['response_data']['orders'][index]['']

	def getOrdersUpdatedTimestamp(self,index=0):
		'''
		updated_timestamp: Data e hora da última atualização da ordem. Não é alterado caso a ordem esteja em um estado final (ver status).
		Tipo: String
		Format: Era Unix
		'''
		return self.result['response_data']['orders'][index]['updated_timestamp']

	def getOrdersOperationsId(self,index=0,indexOperation=0):
		'''
		operation_id: Número de identificação da operação, único por coin_pair
		Tipo: Inteiro
		'''
		return self.result['response_data']['orders'][index]['operations'][indexOperation]['operation_id']

	def getOrdersOperationsQuantity(self,index=0,indexOperation=0):
		'''
		quantity: Quantidade de moeda digital da operação.
		Tipo: String
		'''
		return self.result['response_data']['orders'][index]['operations'][indexOperation]['quantity']

	def getOrdersOperationsPrice(self,index=0,indexOperation=0):
		'''
		price: Preço unitário da operação.
		Tipo: String
		'''
		return self.result['response_data']['orders'][index]['operations'][indexOperation]['price']

	def getOrdersOperationsFeeRate(self,index=0,indexOperation=0):
		'''
		fee_rate: Comissão cobrada pelo serviço de intermediação. A comissão varia para ordens executadas e executoras.
		Tipo: String
		'''
		return self.result['response_data']['orders'][index]['operations'][indexOperation]['fee_rate']

	def getOrdersOperationsExecutedTimestamp(self,index=0,indexOperation=0):
		'''
		executed_timestamp: Data e hora de execução da operação.
		Tipo: String
		Format: Era Unix
		'''
		return self.result['response_data']['orders'][index]['operations'][indexOperation]['executed_timestamp']

	
