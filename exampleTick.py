from backtesting import evaluateTick
from strategy import Strategy
from order import Order
from event import Event

import numpy as np
import random


class BuynHoldTick(Strategy):

    def __init__(self):
        self.bought = False

    def push(self, event):
        # If didnt buy yet, do it
        if event.type == Event.TRADE:
            if not self.bought:
                self.bought = True
                # Send one buy order once
                return [Order(event.instrument, 100, 0)]
            return []
        return []


class MAVGTick(Strategy):

    def __init__(self):
        self.signal = 0
        self.prices = []
        self.size = 1000
        self.std = 0

    def push(self, event):
        if event.type == Event.TRADE:
            price = event.price
            self.prices.append(price)
            orders = []
            if len(self.prices) == self.size:
                std = np.array(self.prices).std()
                mavg = sum(self.prices)/self.size

                if price >= mavg + std:
                    if self.signal == 1:
                        orders.append(Order(event.instrument, -100, 0))
                        orders.append(Order(event.instrument, -100, 0))
                    if self.signal == 0:
                        orders.append(Order(event.instrument, -100, 0))
                    self.signal = -1
                elif price <= mavg - std:
                    if self.signal == -1:
                        orders.append(Order(event.instrument, 200, 0))
                    if self.signal == 0:
                        orders.append(Order(event.instrument, 100, 0))
                    self.signal = 1

                del self.prices[0]

            return orders
        return []


# print(evaluateTick(BuynHoldTick(), {'PETR4': '2018-03-07.csv'}))
# print(evaluateTick(MAVGTick(), {'PETR4': '2018-03-07.csv'}))


class Sar(Strategy):
    def __init__(self):
        self.high = 0
        self.min = 0
        self.status = 1
        self.psar = 0  
        self.af = 0.02
        self.size = 1000
        self.prices = []
        self.signal = 0
        self.cruzamento = 0
        self.initial = True

    def push(self,event):

        if event.type == Event.TRADE:
            price = event.price
            self.prices.append(price)
            orders = []
            if len(self.prices) == self.size:
                self.high = max(self.prices)    # novo maior valor
                self.min = min(self.prices)     # novo menor valor
                if self.initial:
                    print("so tinha que printar uma vez")
                    self.psar = price * 0.8
                    self.initial = False
                else:
                    if self.status == 1:
                        self.psar = self.psar + self.af *(self.high - self.psar)
                    else:
                        self.psar = self.psar - self.af *(self.psar - self.min )

                if self.status == 1:
                    if price < self.psar:
                        self.status = 0
                        self.psar = price * 1.2
                        self.cruzamento += 1

                else:
                    if price > self.psar:
                        self.status = 1
                        self.psar = price * 0.8
                        self.cruzamento += 1
                
                if self.status == 0:
                    if self.signal == 1:
                        orders.append(Order(event.instrument, -100, 0))
                        orders.append(Order(event.instrument, -100, 0))
                    if self.signal == 0:
                        orders.append(Order(event.instrument, -100, 0))
                    self.signal = -1
                else:
                    if self.signal == -1:
                        orders.append(Order(event.instrument, 100, 0))
                        orders.append(Order(event.instrument, 100, 0))
                    if self.signal == 0:
                        orders.append(Order(event.instrument, 100, 0))
                    self.signal = 1

                del self.prices[0]
            
            return orders

        return []

    def fill(self, id, instrument, price, quantity, status):
            super().fill(id, instrument, price, quantity, status)
            
            # Imprimindo o preenchimento das ordens
            if quantity != 0:
                print('Fill: {0} {1}@{2}'.format(instrument, quantity, price))
            
print(evaluateTick(Sar(), {'PETR4': '2018-03-07.csv'}))





        
    

