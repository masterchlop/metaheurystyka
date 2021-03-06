#Plik definiuje klasę Island odpowiedzialną za zarządzanie populacją oraz pomocniczą klasę Member

from random import randint,random
from xmlrpc.client import boolean
from Roulette import Roulette
import Paths
import krandom
import nearestNeighbour

from copy import copy, deepcopy
from Paths import fc
from crossover import OX,PMX, SPX, crossoverOperator

#klasa definiuje członka populacji
class Member():
    def __init__(self, permutation, pfc, death):
        self.perm = permutation
        self.fc = pfc
        self.death = death

    #wyświetl osobnika
    def print(self):
        # print(f"{self.fc}")
        ...
    #funkcja porównująca
    def __lt__(self, other):
        return self.fc < other.fc


class Island():
    '''
        Argumenty konstruktora:
        populationSize - rozmiar populacji
        instance - odniesienie do załadowanego pliku
        r_cross - szansa krzyżowania rodziców
        lifeExpectancy - maksymalna długość życia populacji
        name - nazwa wyspy
        ratio - stosunek członków NN a Krandom w generowanej populacji początkowej
    '''
    def __init__(self, populationSize, instance,r_cross, lifeExpectancy,name="Unnamed",ratio=0.5):
        self.populationSize = populationSize
        self.name = name
        self.instance = instance
        self.lifeExpectancy = lifeExpectancy
        self.ratio = ratio
        self.r_cross = r_cross

        #populacja
        self.population = []
        #generacja
        self.generation = 0
        #inicjuj ruletkę
        self.roulette = Roulette(self.populationSize)
        #wygeneruj populację początkową
        self.generateMembers(self.populationSize,True)
        

    def generateMembers(self, amount, useinvert):
        a1 = int(amount*self.ratio)
        a2 = amount - a1
        self.generateMembersKR(a1)
        self.generateMembersNN(a2,useinvert)
        
    #wygenereuj populację o danym rozmiarze
    def generateMembersKR(self, amount):
        for _ in range(amount):
            member,mfc = krandom.krandom(self.instance.size,self.instance.dis_mat,1)
            newMember = Member(member,mfc,self.generation + self.lifeExpectancy)
            self.population.append(newMember)
        self.population.sort()
        #print(f"Welcome {amount} new members to island {self.name}!")

    def generateMembersNN(self, amount, useInvert):
        newMembers = []

        #generuj
        for _ in range(amount):
            pt = randint(0,self.instance.size-1)
            path, pfc = nearestNeighbour.run(self.instance.size,self.instance.dis_mat,pt)
            newMember = Member(path,pfc,self.generation+self.lifeExpectancy)
            newMembers.append(newMember)

        #poddaj mutacji/om
        for i in range(amount):
            if random() < 0.25:
                mut = 1#randint(1,3)
                for _ in range(mut):
                    r1 = randint(0,self.instance.size-1)
                    r2 = randint(0,self.instance.size-1)
                    if r1>r2: (r1,r2) = (r2,r1)
                    if useInvert:
                        newpath = Paths.invert(newMembers[i].perm,[r1,r2])
                    else:
                        newpath = Paths.swap(newMembers[i].perm,r1,r2)
                    newMembers[i].perm = newpath
                    newMembers[i].fc = Paths.fc(self.instance.dis_mat,newMembers[i].perm)

        for m in newMembers:
            self.population.append(m)
        self.population.sort()
            
        

    #funkcja wykonuje selekcję członków za pomocą ruletki
    def select(self, amount):
        selected = []
        for _ in range(amount):
            ix = self.roulette.getOne()
            selected.append(self.population[ix])

        return selected

    #krzyżowanie osobników
    def crossover(self,parents,xmode) -> [Member]:
        children = []
        r_cross = self.r_cross

        parents = deepcopy(parents)
        parents: [Member,Member] = [[parents[i],parents[i+1]]for i in range(0,len(parents), 2)]
        for p in parents:
            # krzyżujemy czy nie?
            if random() < r_cross:
                while True:
                    p1 = randint(0,len(p[0].perm))
                    p2 = randint(0,len(p[0].perm)-1)
                    if p1 < p2:
                        break

                if xmode == 1:

                    # dziecko 1
                    c1 = OX(p[0].perm,p[1].perm,p1,p2)
                    c1 = Member(c1, fc(self.instance.dis_mat,c1), self.generation + self.lifeExpectancy)
                    children.append(c1)
                    # dziecko 2
                    c2 = OX(p[1].perm,p[0].perm,p1,p2)
                    c2 = Member(c2, fc(self.instance.dis_mat,c2), self.generation + self.lifeExpectancy)
                    children.append(c2)

                elif xmode == 2:

                    c1,c2 = PMX(p[0].perm,p[1].perm,p1,p2)
                    c1 = Member(c1, fc(self.instance.dis_mat,c1), self.generation + self.lifeExpectancy)
                    children.append(c1)
                    c2 = Member(c2, fc(self.instance.dis_mat, c2), self.generation + self.lifeExpectancy)
                    children.append(c2)
                elif xmode == 3:
                    c1 = SPX(p[0].perm,p[1].perm,p1)
                    c1 = Member(c1, fc(self.instance.dis_mat, c1), self.generation + self.lifeExpectancy)
                    children.append(c1)
                    c2 = SPX(p[1].perm, p[0].perm, p1)
                    c2 = Member(c2, fc(self.instance.dis_mat, c2), self.generation + self.lifeExpectancy)
                    children.append(c2)
                elif xmode == 4:



                    c1, c2 = crossoverOperator(p[0].perm, p[1].perm)

                    c1 = Member(c1, fc(self.instance.dis_mat, c1), self.generation + self.lifeExpectancy)
                    c2 = Member(c2, fc(self.instance.dis_mat, c2), self.generation + self.lifeExpectancy)

                    children.append(c1)
                    children.append(c2)


            else:
                c1 = Member(p[0].perm,p[0].fc,self.generation + self.lifeExpectancy)
                children.append(c1)

                c2 = Member(p[1].perm, p[1].fc, self.generation + self.lifeExpectancy)
                children.append(c2)
        return children

    #"ukradnij" osobników do migracji (szansa ruletką)
    def stealMembers(self,amount):
        stolenIx = []
        stolen = []
        a = 0
        while a < amount:
            ix = self.roulette.getOne()
            if ix not in stolenIx:
                stolenIx.append(ix)
                stolen.append(self.population[ix])
                a += 1

        stolenIx.sort(reverse=True)

        #print(stolenIx)
        #print(self.population[0].perm, "hej")
        for a, s in enumerate(stolenIx):

            # print(a)
            # print(len(self.population))
            self.population.pop(s)

        return stolen


    def putInOrder(self, newMember):
        self.population.append(newMember)
        self.population.sort()


    #mutacja (każdy osobnik rozpatrzany osobno)
    # chance = szansa mutacji
    def mutate(self, chance:float, useInvert:boolean):
        for i in range(self.populationSize):
            if random() < chance:

                #print(f"Mutation of member {i}: {self.population[i].fc}!")

                #wyizoluj osobnika
                mb = self.population[i]
                #self.population.pop(i)
                
                #mutacja
                r1 = randint(0,self.instance.size-1)
                r2 = randint(0,self.instance.size-1)
                if r1>r2: (r1,r2) = (r2,r1)

                if useInvert:
                    newpath = Paths.invert(mb.perm,[r1,r2])
                else:
                    newpath = Paths.swap(mb.perm,r1,r2)
                mb.perm = newpath

                #wstaw ponownie
                mb.fc = Paths.fc(self.instance.dis_mat,mb.perm)
                #self.putInOrder(mb)
        pass
    
    #zdarzenie wymierania najsłabszych osobników na wyspie
    # chance - szansa na eksterminację
    def nukeWorst(self,chance:float):
        #ilość wymarłych osobników
        nukedNb = int(self.populationSize * chance)
        for _ in range(nukedNb):
            self.population.pop(-1)
        self.generateMembers(nukedNb,True)

    #funkcja sprawdza czy populacja jest w kolejności rosnącej
    def isPopulationInOrder(self):
        m = self.population[0]
        for i in range(1,len(self.population)):
            if m.fc > self.population[i].fc: return False
            m = self.population[i]
        return True
        
    
    #zdarzenie wymierania losowych osobników na wyspie
    # chance - szansa na eksterminację
    def nukeRandom(self,chance:float):
        #ilość wymarłych osobników
        nukedNb = int(self.populationSize * chance)
        for i in range(nukedNb):
            r = randint(0,self.populationSize-i-1)
            self.population.pop(r)
        self.generateMembers(nukedNb,True)
    
    #oblicz "wartość" wyspy (sumę funkcji celu populacji)
    def islandValue(self):
        s=0
        for p in self.population:
            s+=p.fc
        return s
