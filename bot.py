# -*- coding: utf-8 -*-
'''
Created on 10 de julho de 2020

@author: Rodrigo Nunes

Version: v0.001

    Esse bot será baseado no valor do spreed:
        Passo 1:Obter o valor de compra com base no valor de venda do orderbook
        Passo 2:Realizar a compra com base no valor de venda - spreed definido pelo usuário
        Passo 3:Ápos realizar a compra definir o percentual de ganho e fixar o valor de venda        
        Passo 4:Após realizar a venda
        Passo 5:voltar ao passo 1
'''
import time
import os
import sys
import threading
import configparser
from get_account_info import GetAccountInfo
from list_orderbook import ListOrderBook
from place_sell_order import PlaceSellOrder
from place_buy_order import PlaceBuyOrder
from cancel_order import CancelOrder
from list_orders import ListOrders
from datetime import datetime

# Obtém a hora de inicio do bot e cria um arquivo out com base na data.
inicioBot = str(datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S'))
file = "out-"+str(datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S'))

# Moeda a ser usada no script futuramente pode ser passado por
# parâmetro na linha de comando.
moeda='BRLXRP'

# Obtém as informações de configuração do bot
cfg = configparser.ConfigParser()

# Contador para ordens do inicio do bot
ordensDia=0

# Obtém o spreed em formato percentual do orderbook
def spreedOrderbook(coin_pair):
    time.sleep(1)
    orderBook = ListOrderBook(coin_pair,str(int(time.time())))
    priceSell = float(orderBook.getOrderbookAsksLimitPrice())
    priceBuy = float(orderBook.getOrderbookBidsLimitPrice())
    s = float(((priceSell-priceBuy)/priceSell)*100)
    #s = float("{0:9.2f}".format(s))
    return float("{0:9.2f}".format(s))
    
# Obtém o menor preço de venda do orderbook
def menorVenda(coin_pair):
    time.sleep(1)
    orderBook = ListOrderBook(coin_pair,str(int(time.time())))
    priceSell = float(orderBook.getOrderbookAsksLimitPrice())
    return priceSell

# Realiza uma ordem de compra com base no saldo
# e retorn o order_id da operação.
def buy(coin_pair,saldo):    
    time.sleep(1)
    # Obtém informações do orderbook com base no coin_pair
    orderBook = ListOrderBook(coin_pair,str(int(time.time())))

    # Abre o arquivo e insere as informações nele
    f = open(file,'a')
    f.write("\n############ ORDEN DE COMPRA ############\n")
    f.write("Saldo de Reais: R$"+str(saldo)+"\n")
    f.close()

    # Menor preço de vendo do orderbook
    priceSell = menorVenda(moeda)

    # Preço de compra sugerido
    betterBuy=float("{0:9.5f}".format(priceSell*(1.0-spreedBuy)))

    # Obtém informações do orderbook para estabelecer o melhor preço de compra.   
    cont=0
    while cont<20:
        priceBuy = float(orderBook.getOrderbookBidsLimitPrice(cont))
        f = open(file,'a')
        f.write("Maior compra com indice: {0} R${1:9.5f}".format(cont,priceBuy)+"\n")
        f.close()
        if betterBuy>=priceBuy:
            betterBuy=priceBuy+0.00001
            break
        cont=cont+1        
    
    # Formatando o preço de compra para 5 casas decimais
    betterBuy=float("{0:9.5f}".format(betterBuy))

    f = open(file,'a')
    f.write("\nMelhor preço de compra: "+str(betterBuy)+"\n")
    f.close()

    # Calcula a quantidade a ser comprada
    quantidade=float("{0:9.8f}".format(saldo/betterBuy))
    f = open(file,'a')
    f.write("Quantidade da moeda a ser comprada: "+str(quantidade)+"\n")
    f.close()

    # Executa a ordem de compra
    time.sleep(1)  
    buyOrder = PlaceBuyOrder(coin_pair,quantidade,betterBuy,str(int(time.time())))
    buyOrder_id = int(buyOrder.getOrderId())

    return buyOrder_id

# Cancela uma ordem
def cancelOrder(coin_pair, order_id):
    cancelBuyOrder = CancelOrder(coin_pair,order_id,str(int(time.time())))


# Realiza uma orderm de venda com base na moeda o saldo e o último preço
# de compra da moeda
def sell(coin_pair,saldo,lastBuy):
        
    # Insere informações no arquivo out
    f = open(file,'a')
    f.write("\n############ ORDEN DE VENDA ############\n")
    f.close()    
    
    # Calcula o preço de venda
    betterSell = float(float(lastBuy)*(1.0+spreedSell))

    # Obtém informações do orderbook para estabelecer o melhor preço de venda.
    time.sleep(1)
    orderBook = ListOrderBook(coin_pair,str(int(time.time())))
    cont=0
    while cont<20:
        priceSell = float(orderBook.getOrderbookAsksLimitPrice(cont))
        f = open(file,'a')
        f.write("Menor venda com indice: {0} R${1:9.5f}".format(cont,priceSell)+"\n")
        f.close()
        if betterSell<=priceSell:
            betterSell=priceSell-0.00001
            break
        cont=cont+1

    # Exibe no arquivo out o preço de venda e o preço da ultima compra.
    f = open(file,'a')
    f.write("Melhor preço de venda: "+"{0:9.8f}".format(betterSell)+"\n")
    f.write("Preço da última compra: R$"+str(lastBuy)+"\n")
    f.close()

    # Calcula o valor em Reais com base no preço de venda e o saldo da moeda.
    reais = float("{0:9.4f}".format((betterSell*saldo)*0.997))

    # Exibe as informações no arquivo out
    # Mostrando o valor em Reais já com a taxa descontada
    f = open(file,'a')
    f.write("Valor em Reais calculado descontando a taxa: R$"+str(reais)+"\n")
    f.close()

    # Formata o preço de venda para 5 casas decimais
    betterSell = float("{0:9.5f}".format(betterSell))
    
    # Realiza a ordem de venda com base nas informações inseridas e calculadas
    time.sleep(1)
    sellOrder = PlaceSellOrder(coin_pair,saldo,betterSell,str(int(time.time())))
    sellOrder_id = sellOrder.getOrderId()
    
    # Retorna o ID da ordem de venda
    return sellOrder_id 

while True:
    # Obtém a percentagem do spreed passado por parâmetro no arquivo.
    # Em caso de erro exibe a mensagem e encerra o script.
    try:        
        cfg.read('config')
        spreedBuy=cfg.getfloat('spreed','buy')
        spreedSell=cfg.getfloat('spreed','sell')
    except:
        print("É necessário passar dois argumento spreed como parâmetro")
        print("Um para compra e outro pra venda:")
        print("Edite o arquivo config na seção spreed.")
        exit()

    try:
        # Cabeçalho
        f = open(file,'a')
        f.write("#########################################\n")
        f.write("Bot Iniciado: "+inicioBot+"\n")
        f.write("Ordens criadas no dia: "+str(ordensDia)+"\n")
        f.write("Operação Iniciada: "+str(datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S'))+"\n\n")
        f.close()
    
        # Contador para ordens criadas no dia
        ordensDia=ordensDia+1
    
        # Exibe o cabeçalho no arquivo out
        f = open(file, 'a')
        f.write("Obtendo o valor da última Compra ...\n")
        time.sleep(1)
        l = ListOrders(moeda,str(int(time.time())),4,1)
        ultimaCompra = l.getOrdersLimitPrice()
        f.write("Valor da última Compra: R$"+str(ultimaCompra)+"\n\n")
        f.close()
        time.sleep(1)

        AccountInfo = GetAccountInfo(str(int(time.time())))
        saldoBRL = float(AccountInfo.getBalanceAvailable('brl'))
        qtdCoin = float(AccountInfo.getBalanceAvailable('xrp'))  

        # Exibe o saldo das moedas
        f = open(file,'a')
        f.write("Saldo em Reais: R$"+str(saldoBRL)+"\n")
        f.write("Saldo em Coin: R$"+str(qtdCoin)+"\n\n")
        f.write("Spreed definido pelo usuário para compra: "+str(float("{0:9.2f}".format(spreedBuy*100)))+"%\n")
        f.write("Spreed definido pelo usuário para venda: "+str(float("{0:9.2f}".format(spreedSell*100)))+"%\n")
        f.write("Spreed definido pelo orderbook: "+str(spreedOrderbook(moeda))+"%\n")
        f.write("#########################################\n")
        f.close()

        if qtdCoin>=0.1:
            # Executa uma ordem de venda, obtém o ID e aguarda 20 segundos
            f = open(file,'a')
            f.write("\n\nIniciando ordem de venda...\n")        
            sell_id = sell(moeda,qtdCoin,ultimaCompra)
            f.write("Ordem de venda criada com id: "+str(sell_id)+"\n")
            f.close()
            f = open(file,'a')
            f.write("Aguardando 1 minuto...\n")
            f.close()
            time.sleep(60)
        
            # Cancela a ordem
            cancelOrder(moeda,sell_id)
            f = open(file,'a')
            f.write("Ordem de venda cancelada:\n\n")
            f.close()            
    
        if saldoBRL>=10.0:    
            # Executa uma ordem de compra, obtém o ID e aguarda 20 segundos
            f = open(file,'a')
            f.write("\n\nIniciando ordem de compra...\n")
            buy_id = buy(moeda,saldoBRL)
            f.write("Ordem de compra criada com id: "+str(buy_id)+"\n")
            f.close()
            f = open(file,'a')
            f.write("Aguardando 20 segundos...\n")
            f.close()
            time.sleep(20)
    
            # Cancela a ordem
            cancelOrder(moeda,buy_id)
            f = open(file,'a')
            f.write("Ordem de compra cancelada:\n\n")
            f.close()

        if saldoBRL<10.0 and qtdCoin<0.1:
            # Verifica se há ordens abertas
            f = open(file,'a')
            f.write("\nVerificando se há ordens abertas...\n")
            f.close()
            try:
                time.sleep(1)
                l = ListOrders(moeda,str(int(time.time())),2)
                if int(l.getOrdersStatus()) == 2:
                    f = open(file,'a')
                    f.write("Há ordens abertas com ID: "+str(l.getOrdersId())+"\n")
                    f.close()
                    time.sleep(1)
                    cancelOrder(moeda,l.getOrdersId())
                    f = open(file,'a')
                    f.write("Ordem Cancelada.\n")
                    f.close()
            except:
                f = open(file,'a')
                f.write("Não há ordens abertas.\n")
                f.close()
            f=open(file,'a')
            f.write("Tentando Novamente.\n\n")
            f.close()

    except :        
        f = open(file,'a')
        f.write("\nOcorreu algum erro!!!\n")
        f.write("Tentando novamente em 3 segundos!...\n")
        f.close()
        time.sleep(3)
