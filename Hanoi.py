import ccm  
import random
log=ccm.log(html=True)   

from ccm.lib.actr import *  

class Hanoi(ccm.Model):        # items in the environment look and act like chunks - but note the syntactic differences
    disk1=ccm.Model(isa='disk1',location='PegA')#large disk
    disk2=ccm.Model(isa='disk2',location='PegA')
    disk3=ccm.Model(isa='disk3',location='PegA')

    disk1Stack=ccm.Model(isa='disk1Stack',location=0)#from bottom to top
    disk2Stack=ccm.Model(isa='disk1Stack',location=1)
    disk3Stack=ccm.Model(isa='disk1Stack',location=2)

    disk1Size=ccm.Model(isa='disk1Stack',size=3)#biggest disk
    disk2Size=ccm.Model(isa='disk1Stack',size=2)
    disk3Size=ccm.Model(isa='disk1Stack',size=1)




class MotorModule(ccm.Model):     # create a motor module do the actions 
    #get set function for the values
    def SetDiskLocation(self,disk, to):
        if disk is 'disk1':
            self.parent.parent.disk1.location = to
        if disk is 'disk2':
            self.parent.parent.disk2.location = to
        if disk is 'disk3':
            self.parent.parent.disk3.location = to 

    def GetDiskLocation(self,disk):
        if disk is 'disk1':
            return self.parent.parent.disk1.location   
        if disk is 'disk2':
            return self.parent.parent.disk2.location   
        if disk is 'disk3':
            return self.parent.parent.disk3.location  

    def GetStackLocation(self,disk):
        if disk is 'disk1':
            return self.parent.parent.disk1Stack.location   
        if disk is 'disk2':
            return self.parent.parent.disk2Stack.location   
        if disk is 'disk3':
            return self.parent.parent.disk3Stack.location  

    def getdiskSize(self,disk):
        if disk is 'disk1':
            return self.parent.parent.disk1Size.size   
        if disk is 'disk2':
            return self.parent.parent.disk2Size.size   
        if disk is 'disk3':
            return self.parent.parent.disk3Size.size  

    
    def GetAllLocations(self):
        return self.parent.parent.disk1.location, self.parent.parent.disk2.location, self.parent.parent.disk3.location

    def GetAllStackLocations(self):
        return self.parent.parent.disk1Stack.location, self.parent.parent.disk2Stack.location, self.parent.parent.disk3Stack.location
    
    def GetAllsizes(self):
        return self.parent.parent.disk1Size.size, self.parent.parent.disk2Size.size, self.parent.parent.disk3Size.size
    #end of get set functions




    #see if the moce done is possible
    def possibleToMove(self, from_, to, disk):
        #see if disk is at the locatioin we wanna move from
        CurDiskLocation = self.GetDiskLocation(disk)
        if from_ is not CurDiskLocation:
            #print("Wrong move!")
            #print(disk + " is not on " +from_+ " but at " + CurDiskLocation)
            return False


        #see if disk is upper disk
        CurStackLocation = self.GetStackLocation(disk)

        locations = self.GetAllLocations()
        stackPos = self.GetAllStackLocations()

        for stackNr in range(len(locations)):
            #check if something is ontop of it
            if CurDiskLocation is locations[stackNr] and CurStackLocation < stackPos[stackNr]:
                
                return False;

        #see if disk moves at all
        if to is from_:
           # print("can't move to same peg")
            return False

        #check if we don't move on to a a peg with a smaller disk
        diskSizes = self.GetAllsizes()
        Cursize = self.getdiskSize(disk)
        for stackNr in range(len(locations)):
            if to is locations[stackNr] and Cursize > diskSizes[stackNr]:
                #print("cant put small disk on big one at" + to)
                return False;

        #no rules violated
        return True


    #function to move the disk and print the movement and current state
    def move_disk(self, from_, to, disk):     
        self.SetDiskLocation(disk, to)
        print("-"+disk+" was moved to "+ to + ".")
        
        locs = self.GetAllLocations()
        pegADisks= []
        pegBDisks= []
        pegCDisks= []
        for loc in range(len(locs)):
            if locs[loc] is 'PegA':
                pegADisks.append("Disk"+ str(loc+1))
            if locs[loc] is 'PegB':
                pegBDisks.append("Disk"+ str(loc+1))
            if locs[loc] is 'PegC':
                pegCDisks.append("Disk"+ str(loc+1))

        print("-Peg A has disks: " + str(pegADisks) + " Peg B has disks: " + str(pegBDisks) + " Peg C has disks: " + str(pegCDisks))
      
    #to determine if we are done
    def win(self):
        locations = self.GetAllLocations()
        for Nr in range(len(locations)):
            if locations[Nr] is not 'PegC':
                return False
        return True
            
    
class MyAgent(ACTR):    
    focus=Buffer()
    motor=MotorModule()
   

    def init():
        focus.set('getGoal')
        
    def move1(focus='getGoal'):
        #defaults
        from_ = 'PegA'
        to = 'PegA'
        disk = 'disk1'

        disks = 'disk1','disk2','disk3'
        locations = motor.GetAllLocations()
        stackPos = motor.GetAllStackLocations()
        Pegs = 'PegA','PegB','PegC'
        
            
        #get all the highest disks, we can move those.
        movableStacks = list(set(locations))
        movableDisks = []
        for stack in movableStacks:
            highest = -1
            addisk = 'error'
            for loc in range(0,len(locations)):
                if stack is locations[loc]:
                    if highest < stackPos[loc]:
                        highest = stackPos[loc]
                        addisk = loc
            movableDisks.append(addisk)


        #Biggest disk not on pegC
        if locations[0] is not 'PegC':
            #can we move disk1 to pegC? than do that
            if 0 in movableDisks and 'PegC' not in locations:
                from_ = locations[0]
                to = 'PegC'
                disk = 'disk1'
                #else take a random   
            else:
                randomdisNr = random.choice(movableDisks)
                disk = disks[randomdisNr]
                from_ = locations[randomdisNr]
                to = Pegs[random.randrange(0,3)]

                #find a random choice that is possible
                while not motor.possibleToMove(from_, to, disk):
                    randomdisNr = random.choice(movableDisks)
                    disk = disks[randomdisNr]
                    from_ = locations[randomdisNr]
                    to = Pegs[random.randrange(0,3)]


        #if we still need to get disk 2 to pegC(disk3 is there already)
        elif locations[1] is not 'PegC':
            
            newMovableDisks = []
            for d in movableDisks:
                if d is not 0:
                    newMovableDisks.append(d)

            #if we can move disk 2 to PegC
            if 1 in movableDisks and locations[2] is not 'PegC':
                from_ = locations[1]
                to = 'PegC'
                disk = 'disk2'
                
            else:
                #random move outof possible moves
                randomdisNr = random.choice(newMovableDisks)
                disk = disks[randomdisNr]
                from_ = locations[randomdisNr]
                to = Pegs[random.randrange(0,3)]


                #find a random choice that is possible
                while not motor.possibleToMove(from_, to, disk):
                    randomdisNr = random.choice(newMovableDisks)
                    disk = disks[randomdisNr]
                    from_ = locations[randomdisNr]
                    to = Pegs[random.randrange(0,3)]

        #only the smallest disk is left over, simply move this on to pegC
        elif locations[2] is not 'PegC':        
           from_ = locations[2]
           to = 'PegC'
           disk = 'disk3' 
           #exit(1)

        #the algortihem in words:           
           
        #disk 3 not on PegC
        #give all possible moves  
        #if disk 3 is free and PegC
        #move 3 to pegC
        #else
        #chose move randomly
       
        
        #disk 2 not on PegC
        #give possible moves  
        #if disk 2 is free and PegC accept for disk 3
        #move 2 to pegC
        #else
        #chose move randomly
        

        #disk1 is not on pegC
        #move disk 1 to pegC

        #print "I wanna move: " + disk + " from: " + from_ + " to: " +to   
        possible = motor.possibleToMove(from_, to, disk)
         
        if(possible):
            
            motor.move_disk(from_, to, disk)   
            #motor.print
            #check: we won?
            focus.set('won')
        else:
            #chose other move        
            print "error, this wasn't supposed to happen"
            exit(1)
        
    def win(focus='won'):
        if motor.win():
            focus.set('stop')
        else:
            focus.set('getGoal')

    def stop_production(focus='stop'):  

        print "we solved The tower of Hanoi problem, bye for now!"
        self.stop()

          

Thomas=MyAgent()
env=Hanoi()
env.agent=Thomas
ccm.log_everything(env)

env.run()
ccm.finished()
