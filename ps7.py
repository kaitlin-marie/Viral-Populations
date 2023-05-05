print("\033c")

import numpy
import random
import pylab
import statistics


# virus classes

class NoChildException(Exception):
    """
    NoChildException is raised by the reproduce() method in the SimpleVirus
    and ResistantVirus classes to indicate that a virus particle does not
    reproduce.
    """


# no drug resistance viruses
class SimpleVirus(object):
    def __init__(self, maxBirthProb, clearProb):
        self.maxBirthProb = maxBirthProb
        self.clearProb = clearProb       

    def doesClear(self):
        death = random.random()
        if death <= self.clearProb:
            return True
            # a True means the body cleared the virus particle, aka particle is dead

    def reproduce(self, popDensity):
        baby = random.random()
        if baby <= (self.maxBirthProb * (1 - popDensity)):
            return SimpleVirus(self.maxBirthProb, self.clearProb)
            # creates new virus kiddie
        else:
            raise NoChildException


# drug resistant viruses
class ResistantVirus(SimpleVirus):
    def __init__(self, maxBirthProb, clearProb, resistances, mutProb):
        self.maxBirthProb = maxBirthProb
        self.clearProb = clearProb
        self.resistances = resistances
        self.mutProb = mutProb

    def isResistantTo(self, drug):
        return self.resistances[drug]

    def reproduce(self, popDensity, activeDrugs):
        
        # if virus particle is not resistant to all active drugs, it does not reproduce
        for drug in activeDrugs:
            if self.resistances[drug] == False:
                raise NoChildException
           
        # if virus is drug resistant to all active drugs, reproduction probability follows
        baby = random.random()
        if baby <= (self.maxBirthProb * (1 - popDensity)):
            # first calculate offsprings resistances and mutations
            BabysResist = {}
            for key, value in self.resistances.items():
                # if parent has drug resistance, has 1-mutProb chance of keeping resistance
                if value == True:
                    KeepMut = random.random()
                    if KeepMut <= (1 - self.mutProb):
                        BabysResist[key] = True
                    else:
                        BabysResist[key] = False
                # if parent is not resistant, has mutProb chance of gaining resistance
                else:
                    NewMut = random.random()
                    if NewMut <= self.mutProb:
                        BabysResist[key] = True
                    else:
                        BabysResist[key] = False
            # create new virus kiddie
            return ResistantVirus(self.maxBirthProb, self.clearProb, BabysResist, self.mutProb)
            
        else:
            raise NoChildException






# patient classes


# non treated pt
class SimplePatient(object):
    def __init__(self, viruses, maxPop):
        self.viruses = viruses
        self.maxPop = maxPop
        self.popDensity = None

    def getTotalPop(self):
        return len(self.viruses)

    def update(self):
        # determine whether each particle survives
        for virus in self.viruses:
            if SimpleVirus.doesClear(virus) == True:
                self.viruses.remove(virus)
        
        # update pop density
        self.popDensity = (len(self.viruses))/self.maxPop

        # sexy time for the viruses
        tempVirus = []
        for virus in self.viruses:
            try:
                NewKid = SimpleVirus.reproduce(virus, self.popDensity)
                tempVirus.append(NewKid)
            except NoChildException:
                pass
        self.viruses.extend(tempVirus)
        
        return len(self.viruses)




# treated patient -- can take drugs, and viruses can develop resistance
class Patient(SimplePatient):
    def __init__(self, viruses, maxPop):
        self.viruses = viruses
        self.maxPop = maxPop
        self.activeDrugs = []

    def addPrescription(self, newDrug):
        if newDrug not in self.activeDrugs:
            self.activeDrugs.append(newDrug)

    def getPrescriptions(self):
        return self.activeDrugs
        
    def getResistPop(self, drugResist):
        resistPop = 0
        for virus in self.viruses:
            fullResist = all(virus.resistances[drug] for drug in drugResist)
            if fullResist == True:
                resistPop += 1

        return resistPop 

    def update(self):

        # determine survival of viruses
        for virus in self.viruses:
            if virus.doesClear() == True:
                self.viruses.remove(virus)

        # update population density
        self.popDensity = (len(self.viruses)) / self.maxPop

        # sexy time for the viruses
        tempVirus = []
        for virus in self.viruses:
            try:
                NewKid = virus.reproduce(self.popDensity, self.activeDrugs)
                tempVirus.append(NewKid)
            except NoChildException:
                pass
        self.viruses.extend(tempVirus)
        
        return len(self.viruses)
    






            

# simulations


# no drug treatment
def simulationWithoutDrug(maxPop, maxBirthProb, clearProb, numInitialVirus, time):

    # initialize viruses
    viruses = []
    for i in range(numInitialVirus):
        viruses.append(SimpleVirus(maxBirthProb, clearProb))

    # initialize patient
    patientZero = SimplePatient(viruses, maxPop)

    # start the infection growth!
    TotalPop = []
    Times = []
    for step in range(time):
        TotalPop.append(patientZero.update())
        Times.append(step)

    return Times, TotalPop

simulationWithoutDrug(4000, .1, .9, 300, 100)


# basic drug treatment
def simulationWithDrug(maxPop, maxBirthProb, clearProb, numInitialVirus, addedDrugs, addDrugAt, resistances, mutProb, time):

    # initialize viruses
    viruses = []
    for i in range(numInitialVirus):
        viruses.append(ResistantVirus(maxBirthProb, clearProb, resistances, mutProb))

    # initialize patient
    patientZero = Patient(viruses, maxPop)

    # start the infection growth!
    TotalPop = []
    ResistPop = []
    Times = []
    actingDrugs = []
    for step in range(time):
        # adds drug at specified time step
        for index, value in enumerate(addDrugAt):
            if value == step:
                patientZero.addPrescription(addedDrugs[index])
                actingDrugs.append(addedDrugs[index])
        # growth continues
        TotalPop.append(patientZero.update())
        ResistPop.append(patientZero.getResistPop(actingDrugs))
        Times.append(step)

    return Times, TotalPop, ResistPop
   

        




# graphs


# sim without drug, virus pop growth over time
def PlotNoDrug(numTrials):
    Times = []
    TotalPop = []
    for k in range(numTrials):
        # growth example:
        timehold, pop = simulationWithoutDrug(1000, .1, .05, 100, 300)
        
        # death example:
        # timehold, pop = simulationWithoutDrug(4000, .1, .9, 300, 100)

        Times.extend(timehold)
        TotalPop.extend(pop)

    # plot raw data points
    pylab.figure(1)
    pylab.plot(Times, TotalPop, 'bx')
    pylab.title('Virus Population Growth over Time')
    pylab.xlabel('Time')
    pylab.ylabel('Virus Population')
    pylab.show()



# sim with drugs added, total population growth and drug resistant population growth vs time
def PlotDrugs(numTrials, drugs, drugTime, resistances):

    # run sim trials
    for trial in range(numTrials):
        Times, totalPop, resistPop = simulationWithDrug(1000, .7, .2, 100, drugs, drugTime, resistances, .1, 300)

    # plot raw data
    pylab.figure(2)
    pylab.plot(Times, totalPop, 'bx', label = 'Total Population')
    pylab.plot(Times, resistPop, 'ro', label = 'Drug Resistant')
    pylab.title('Resistant and Total Virus Population Growth over Time')
    pylab.xlabel('Time')
    pylab.ylabel('Virus Population')
    pylab.legend()
    pylab.show()

 
    
# drug treatment at differing time steps
def PlotTreatmentDelay(numTrials, drugs, resistances):
    # drug admin times
    # done as small lists because drug sim takes a list as argument
    drugDelay= [0, 75, 150, 250]
    finalPop = []

    for h in drugDelay:
        # run sim trials
        for trial in range(numTrials):
            averagePop = []
            Times, totalPop, resistPop = simulationWithDrug(3000, .7, .1, 100, drugs, [h], resistances, .6, 300)
            endPop = totalPop[-1]
            averagePop.append(endPop)
        mean = statistics.mean(averagePop)
        finalPop.append(mean)
        
    pylab.figure(3)
    pylab.bar(drugDelay, finalPop)
    pylab.xlabel('Drug Added At')
    pylab.ylabel('Total Viral Population at 300 timestep')
    pylab.title('Viral Population after Different Drug Treatment Times')
    pylab.show()



drugTrial = ['guttagonol', 'gremfixin']
trialTimes = [100, 200]
trialResist = { 'guttagonol':False, 'gremfixin':False }
# PlotDrugs(30, drugTrial, trialTimes, trialResist)

delayDrug = ['guttagonol']
PlotTreatmentDelay(10, delayDrug, trialResist)