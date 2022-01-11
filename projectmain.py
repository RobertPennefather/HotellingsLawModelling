import turtle
import random
import numpy as np
import time
import itertools
import argparse

from Tkinter import *


class Consumer:
    
    def __init__(self, position):
        self.store = None 
        self.position = position
        
    def __repr__(self):
        return "%s: %s" % (self.position, self.store)
    
    def __str__(self):
        return "%s: %s" % (self.position, self.store)
        
    def setStore(self, stores):
        self.store = self.findStore(stores)
    
    def findStore(self, stores):
        best = None
        bestIndex = None
        index = 0
        match = not CONSUMER_REJECTS
        
        for shop in stores:
            vector = (self.position[0] - shop.position[0], self.position[1] - shop.position[1])
            distance = (vector[0]**2+vector[1]**2)**0.5
            
            cost = shop.price
            
            total = distance + cost
            
            #Consumer must have resonable combination of distance and cost to buy
            
            if CONSUMER_REJECTS and (LIMIT) < total:
                index += 1
                continue
            
            elif best is None or total < best:
                best = total
                bestIndex = index
                match = True
                
            #will stay with old store if equal, partially represents brand loyalty
            elif total == best and self.store == index:
                best = total
                bestIndex = index
                match = True
                
            index += 1
            
        if not match:
            self.store = None
            return None
        
        self.store = bestIndex
        return bestIndex



class Store:
    
    def __init__(self):
        self.company = None
        
        #Select random position
        #add edge case so multiple stores don't start in same location 
        x = random.randint(0,MAP_SIZE-1)
        y = random.randint(0,MAP_SIZE-1)
        self.position = (x,y)
        
        self.price = random.uniform(0.5,MAX_START_PRICE)
        
    def __repr__(self):
        return "%s: %s - $%s" % (self.company.colour, self.position, self.price)
    
    def __str__(self):
        return "%s: %s - $%s" % (self.company.colour, self.position, self.price)
    
    def setCompany(self, company):
        self.company = company
        
    def getRevenue(self, people, shops):
        return self.getMarketFraction(people, shops) * self.price
    
    def getMarketFraction(self, people, shops):
        
        #Get index of shop in shops
        index = 0
        for shop in shops:
            if shop == self:
                break
            index += 1
        
        #Find how many people want to go to current shop
        totalPeople = 0
        totalCustomers = 0
        for person in people:
            if person.findStore(shops) == index:
                totalCustomers += 1
            totalPeople += 1
            
        return 1.0*totalCustomers/totalPeople
    
    def changePrice(self, people, shops):
        if self.company == None:
            print "Store has no company"
            return
        
        #Market share after moving price original, up, down
        revenue = [0.0]*3
        revenue[0] = self.company.getProfit(people, shops)
        
        #Test price up
        self.price = self.price+1
        revenue[1] = self.company.getProfit(people, shops)
        self.price = self.price-1
        
        #Test price down
        if (self.price > 0):
            self.price = self.price-1
            revenue[2] = self.company.getProfit(people, shops)
            self.price = self.price+1
        
        change = np.argmax(revenue)
        
        if change == 1:
            self.price = self.price+1
        elif change == 2:
            self.price = self.price-1
    
    def changePosition(self, people, shops):
        if self.company == None:
            print "Store has no company"
            return
        
        #Market share after moving original, up, down, right, left
        marketShare = [0.0]*5
        marketShare[0] = self.company.getProfit(people, shops)
        
        #Test moving up
        if (self.position[1] < MAP_SIZE-1):
            match = False
            for othershops in shops: 
                if ((self.position[0], self.position[1]+1) == othershops.position):
                    match = True
            if not match:
                self.position = (self.position[0], self.position[1]+1)
                marketShare[1] = self.company.getProfit(people, shops)
                self.position = (self.position[0], self.position[1]-1)
        
        #Test moving down
        if (self.position[1] > 0):
            match = False
            for othershops in shops: 
                if ((self.position[0], self.position[1]-1) == othershops.position):
                    match = True
            if not match:
                self.position = (self.position[0], self.position[1]-1)
                marketShare[2] = self.company.getProfit(people, shops)
                self.position = (self.position[0], self.position[1]+1)
        
        #Test moving right 
        if (self.position[0] < MAP_SIZE-1):
            match = False
            for othershops in shops: 
                if ((self.position[0]+1, self.position[1]) == othershops.position):
                    match = True
            if not match:
                self.position = (self.position[0]+1, self.position[1])
                marketShare[3] = self.company.getProfit(people, shops)
                self.position = (self.position[0]-1, self.position[1])
            
        #Test moving left
        if (self.position[0] > 0):
            match = False
            for othershops in shops: 
                if ((self.position[0]-1, self.position[1]) == othershops.position):
                    match = True
            if not match:
                self.position = (self.position[0]-1, self.position[1])
                marketShare[4] = self.company.getProfit(people, shops)
                self.position = (self.position[0]+1, self.position[1])
        
        move = np.argmax(marketShare)
        
        if move == 1:
            self.position = (self.position[0], self.position[1]+1)
        elif move == 2:
            self.position = (self.position[0], self.position[1]-1)
        elif move == 3:
            self.position = (self.position[0]+1, self.position[1])
        elif move == 4:
            self.position = (self.position[0]-1, self.position[1])



class Company:
    
    def __init__(self, colour):
        self.stores = []
        self.colour = colour
        self.revenue = 0
        
    def __repr__(self):
        return "%s: %s" % (self.colour, self.revenue)
    
    def __str__(self):
        return "%s: %s" % (self.colour, self.revenue)
    
    def addStore(self, store):
        store.setCompany(self)
        self.stores.append(store)
        
    def getProfit(self, people, shops):
        
        profit = 0.0
        for store in self.stores:
            profit += store.getRevenue(people, shops)
           
        self.revenue = profit
        return profit



class drawWorld(object):
    
    def __init__(self, people, shops):
        self.root = Tk()
        self.canvas = Canvas(self.root, width=CANVAS_SIZE, height = CANVAS_SIZE)
        self.canvas.pack()
        self.root.after(0, self.animation(people, companies))
 
    def animation(self, people, companies):
        time.sleep(0.1)
        for pop in people:
            x = pop.position[0] * CANVAS_BLOCK_SIZE
            y = pop.position[1] * CANVAS_BLOCK_SIZE
            colour = 'white'
            if(DISPLAY_PRICE is True):
                colour = '#262626' #to avoid confusion with expensive stores (that are light coloured) and consumers who don't attend any shop 
            if pop.store is not None:
                colour = shops[pop.store].company.colour
            self.canvas.create_rectangle(x, y, x + CANVAS_BLOCK_SIZE, y + CANVAS_BLOCK_SIZE, fill=colour)

        for index, shop in enumerate(shops):
            x = shop.position[0] * CANVAS_BLOCK_SIZE
            y = shop.position[1] * CANVAS_BLOCK_SIZE

            if (DISPLAY_PRICE is False):
                self.canvas.create_rectangle(x, y, x + CANVAS_BLOCK_SIZE, y + CANVAS_BLOCK_SIZE, outline='white', fill=shop.company.colour)

            if (DISPLAY_PRICE is True):
                newrgbColour = [0] * 3
                
                multiplier =  (shop.price / MAX_START_PRICE)
                rgbColour = self.hexToRgb(shop.company.colour)
                
                for index, i in enumerate(rgbColour):
                    newrgbColour[index] = rgbColour[index] * multiplier
                    if(newrgbColour[index] > 255):
                        newrgbColour[index] = 255
   
                newHex = self.rgbToHex(newrgbColour[0],newrgbColour[1],newrgbColour[2])

                self.canvas.create_rectangle(x, y, x + CANVAS_BLOCK_SIZE, y + CANVAS_BLOCK_SIZE, outline='white', fill=newHex)
    
        self.canvas.update()

    def rgbToHex(self, red, green, blue):
        return '#%02x%02x%02x' % (red, green, blue)
    
    def hexToRgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))



STEPS = 100
COMPANY_NUM = 2
STORE_NUM = 5

MAP_SIZE = 20
MAX_START_PRICE = 2
CONSUMER_REJECTS = True 

CANVAS_SIZE = 400
CANVAS_BLOCK_SIZE = CANVAS_SIZE / MAP_SIZE

#LIMIT = MAP_SIZE/2 + MAX_START_PRICE
LIMIT = float("inf")

DISPLAY_PRICE = False 


parser = argparse.ArgumentParser(description='Initiate Companies')
parser.add_argument('companies', metavar='N', type=int, nargs='+', help='Number of shops for each company')

parser.add_argument('-l', '--limit',  type = int, nargs = '?',  const = MAP_SIZE/2 + MAX_START_PRICE,   help='Include flag to enable limits, defaults to equation MAP_SIZE/2 + MAX_START_PRICE but optional integer argument to set a limit')

parser.add_argument('-c', '--colour', action = 'store_true',   help='Include flag to display pricing of shops through colour opacity, where light indicates high prices and dark indicates low')

parser.add_argument('-s', '--size', type = int, nargs = 1, help = 'Include single integer argment to adjust grid size - default is 20')

args = parser.parse_args()

COMPANY_NUM = len(args.companies) #update default

if args.limit :
    print 'Limits are enabled' 
    LIMIT = args.limit  #update limit

if args.size: #update map and canvas block size 
    MAP_SIZE = args.size[0]
    CANVAS_BLOCK_SIZE = CANVAS_SIZE / MAP_SIZE
    

#Create companies
companies = []
COMPANY_NUM = min(COMPANY_NUM, 10) #Max companies is 10

if( not args.colour):
    colours = ['red','blue','green','orange','yellow','purple','pink','cyan','magenta','gray']    
    for i in range(COMPANY_NUM):
        companies.append(Company(colours[i])) 

if args.colour:
    print 'Colour pricing is enabled'
    DISPLAY_PRICE = True
    hexaColours = ['#FF6666','#6666FF','#b3ff66','#FFCC66', '#ffff66', '#cc66ff', '#ff66cc', '#85e0e0', '#8cd98c', '#b3b3b3'   ]
    for i in range(COMPANY_NUM):
        companies.append(Company(hexaColours[i])) 


print COMPANY_NUM, ' companies created with ', args.companies, ' shops each'    

#Create shops and assign to companies
shops = []
    
for index, i in enumerate(args.companies):
    for j in range(args.companies[index]):
        currshop = Store()
        companies[index].addStore(currshop)
        shops.append(currshop)
    
#Create customers and assign to shops
population = []
for i in range(MAP_SIZE):
    for j in range(MAP_SIZE):
        person = Consumer((i,j))
        person.setStore(shops)
        population.append(person)

#Draw World
world = drawWorld(population, shops)  

#Step
for step in range(STEPS):
    for shop in shops:
        shop.changePosition(population, shops)
        shop.changePrice(population, shops)
        world.animation(population, shops)
    
world.root.mainloop()


#Testing

'''
#Print World
for company in companies:
    company.getProfit(population, shops)
print companies
print shops
for shop in shops:
    print shop.getRevenue(population, shops)
print
'''

