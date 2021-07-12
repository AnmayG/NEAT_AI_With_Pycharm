# Libraries
import random
import numpy as np

# CONSTANTS DECLARATION
inputnum = 2


class Node:
    # The way that I'm making the networks is by having each node be a class and each connection be a class
    # Bias is set to 0 because I don't think there'll be anything to lose
    # There's no real thing to bias towards
    def __init__(self, idnum, layer, bias):
        self.id = idnum
        self.input = 0
        self.output = 0
        self.outto = []
        self.layer = layer
        self.bias = bias

    def calcoutput(self):
        # This gets the node's output
        # It does this by "activating" the data, or totalling it and normalizing it
        # I'm using a tanh function, which keeps it between -1 and 1
        self.output = self.input
        if self.layer != 0:
            self.output = np.tanh(self.input)
        for connect in self.outto:
            if connect.enabled:
                connect.n2.input += connect.weight * self.output + self.bias

    def connected(self, yeet):
        # This checks if 2 nodes are connected
        foo = [i.n2 for i in self.outto]
        return yeet in foo

    def duplicate(self):
        return Node(self.id, self.layer, self.bias)


class Connection:
    def __init__(self, fro, to, w, inno):
        # Each connection has an innovation number to show how cool it is and how it should be saved
        self.n1 = fro
        self.n2 = to
        self.weight = w
        self.inno = inno
        self.enabled = True

    def mutate(self):
        if random.random() < 0.1:
            self.weight = random.uniform(0, 1)
        else:
            self.weight += random.gauss(0, 1) / 50
            self.weight = np.maximum(self.weight, 0)
            self.weight = np.minimum(self.weight, 1)

    def duplicate(self, n1, n2):
        return Connection(n1, n2, self.weight, self.inno)


class Conh:
    def __init__(self, fro, to, inno, innonum):
        # Each connection also has a history, which will keep its numbers in an array
        # It'll also check if 2 connections match
        self.fro = fro
        self.to = to
        self.inno = inno
        self.innonums = innonum.copy()

    def match(self, student, fro, to):
        if len(student.cons) == len(self.innonums):
            if fro.id == self.fro and to.id == self.to:
                for g in student.cons:
                    if g.inno not in self.innonums:
                        return False
                return True
        return False


class Student:
    def __init__(self, bads, idnum, champ, player):
        # This is a student, which is essentially all the important stuff that a player needs
        # Each student has a brain that covers all the neural network junk
        self.champ = champ
        self.bads = bads
        self.score = 0
        self.id = idnum
        self.player = player
        self.badscoords = []
        # It parses everything
        self.inputs = inputnum * len(bads) + 1
        self.outputs = 1
        self.brain = ItsALIVE(self.inputs, self.outputs, False)
        self.best = 0

    def move(self, bads):
        return self.brain.move(self.player.x, self.player.y + 38, bads)

    def crossover(self, badparent, bads, idnum, newplayer):
        kid = Student(bads, idnum, self.champ, newplayer)
        kid.brain = self.brain.crossover(badparent)
        kid.brain.gennet()
        return kid

    def makenew(self, pl):
        clone = Student(self.bads, self.id, self.champ, pl)
        clone.brain = self.brain.duplicate()
        clone.brain.gennet()
        clone.best = self.best
        return clone


class Overall:
    def __init__(self, bads, pops):
        # This is the overall population of a 1000 students that does stuff
        self.students = [Student(bads, i, False, pops.sprites()[i]) for i in range(len(pops.sprites()))]
        self.innohis = []
        # After making a bunch of students, it mutates it and organizes the nodes
        for p in self.students:
            p.brain.mutate(self.innohis)
            p.brain.gennet()
        self.best = 0
        self.bestscore = 0
        self.globalbest = 0
        self.gen = 1
        self.genpl = []
        self.species = []
        self.killemall = False

    def themanthemysterythelegend(self):
        # This gets the best student in the current moment
        # It does this through the very scientific method of checking if it's dead or not
        for s in self.students:
            if not s.player.dead:
                return s
        return self.students[0]

    def updatestudents(self, bads, printjunk):
        # This runs the current values through the networks and gets back the movements
        moves = []
        for s in self.students:
            if not s.player.dead:
                moves.append(s.move(bads))
            else:
                moves.append(1000000)
            if s.score > self.globalbest:
                self.globalbest = s.score
        if printjunk:
            for s in self.species:
                s.bestbrain.printingisfun()
        return moves

    def magic(self):
        # I want to be able to say that it works through magic

        # It saves the current best student
        prev = list(self.students)[0]
        # It then sorts the players into schools/species
        for s in self.species:
            s.players = []
        for p in self.students:
            notfoundschool = True
            for s in self.species:
                if s.sameschool(p.brain):
                    s.students.append(p)
                    notfoundschool = False
                break
            if notfoundschool:
                self.species.append(Species(p))
        # It sorts the species by their score
        for s in self.species:
            s.sort()
        self.species = sorted(self.species, key=lambda s2: s2.bestscore, reverse=True)
        # Few more print statements and a purge function for when things get out of hand or just plain stuck Also,
        # the first result will always be the best score in the entire program Please use this result to determine if
        # it's been doing good, as over time the high score can still diminish The connections and weights would
        # still continue into the next generation, but it can dip if it just gets really unlucky (there are a few
        # instant-death scenarios that most students won't try to resolve because they're so rare).
        print("Complete Scores: " + str([s.bestscore for s in self.species]) + str(
            [[s2.score for s2 in s.students] for s in self.species]))
        if self.killemall:
            i = 5
            while i < len(self.species):
                self.species.pop(i)
            self.killemall = False
            print("RIP our species")
        # This tells the species to kill off their bottom half, share their scores, and set average
        for s in self.species:
            s.eliminate()
            s.sharescore()
            s.setavg()
        # This updates the current best score
        temp = self.species[0].students[0]
        temp.gen = self.gen
        if temp.score >= self.bestscore:
            self.genpl.append(temp.makenew(temp.player))
            print(f"Old Best: {self.bestscore} New Best: {temp.score}")
            self.bestscore = temp.score
        # This gets rid of the schools that just don't do anything for 15 generations
        # It does keep the best 2 schools though
        i = 2
        while i < len(self.species):
            if self.species[i].nochange >= 15:
                self.species.pop(i)
                i -= 1
            i += 1
        # This checks if a "school" gets no "funding", basically checking if a school will be allocated nothing
        # If so, it's eliminated
        avgsum = np.sum([s.avg for s in self.species])
        i = 1
        while i < len(self.species):
            if self.species[i].avg / avgsum * len(self.students) < 1:
                self.species.pop(i)
                i -= 1
            i += 1
        # This will give each school a certain number of students
        # This student number is calculated by just taking the total average and dividing it by the species average
        # This gives you the ratio of how important the species is, then gives it that many students
        print(f"Generation: {self.gen} Number of Changes: {len(self.innohis)} Schools: {len(self.species)}")
        avg = np.sum([s.avg for s in self.species])
        kids = []
        for s in self.species:
            # It also attaches a clone of the first player because the first player is always the best
            kids.append(s.champ.makenew(s.champ.player))
            studentnum = int(np.floor(s.avg / avg * len(self.students)) - 1)
            kids = [s.newstudent(self.innohis) for i in range(studentnum)]
        # If there's a rounding error or something, I plug in the best student and then only the best people
        if len(kids) < len(self.students):
            kids.append(prev.makenew(prev.player))
        while len(kids) < len(self.students):
            kids.append(self.species[0].newstudent(self.innohis))
        self.students = kids.copy()
        self.gen += 1
        # This organizes all the nodes, essentially from [0, 1, 2, 3, 4, 5, 6, 7] it's [0, 1, 2, 3, 4, 6, 7, 5]
        for p in self.students:
            p.brain.gennet()

    def parsepop(self, newplayers):
        # This gives each student a plane
        for p in range(len(self.students)):
            self.students[p].player = newplayers.sprites()[p]
            self.students[p].id = p


# School and species are interchangeable by the way, I have very inconsistent wording
class Species:
    def __init__(self, firstplayer):
        # Each species is based off of its first person, and they'll change over time
        self.students = [firstplayer]
        self.bestscore = 0
        self.champ = firstplayer.makenew(firstplayer.player)
        self.avg = 0
        self.nochange = 0
        self.bestbrain = firstplayer.brain.duplicate()
        self.bestbrain.gennet()
        self.excess = 1
        self.wdiffs = 0.5
        self.closeenough = 3

    def sameschool(self, itsabrain):
        # This checks if a new student is in this species
        # It does so by checking if there's any new connections and then if the weights are a big change
        changed = self.extracons(itsabrain)
        wchange = self.weightcons(itsabrain)
        # Bigbecomesmall makes sure that if you have like 200 connections you don't get immediately deleted
        bigbecomesmall = len(itsabrain.cons) - 20
        if bigbecomesmall < 1:
            bigbecomesmall = 1
        # If you think about this as a threshold, essentially I'm saying that # of new cons + amount of weight change*0.5 is how close the student is to the species
        # If the change is more than 3 (which means it has at least a new node and a new con) it's a new species
        # The change > 3 means that at the very least a new node is created.
        # The 1 is just so that I can change it later.
        # And the 0.5 is because weights shouldn't be as important as connections
        isitclose = (self.excess * changed / bigbecomesmall) + (self.wdiffs * wchange)
        return self.closeenough > isitclose

    def weightcons(self, brain):
        # This checks to see how different the weights are per connection
        # The inno doubles as an id for the connections
        if len(brain.cons) == 0 or len(self.bestbrain.cons) == 0:
            return 0
        m = 0
        td = 0
        for i in brain.cons:
            for j in self.bestbrain.cons:
                if i.inno == j.inno:
                    m += 1
                    td += abs(i.weight - j.weight)
                    break
        # Dividing by zero sucks
        if m == 0:
            m = 100
        return td / m

    def extracons(self, brain):
        # This checks for excess connections
        # If the brains match exactly it returns 0
        m = 0
        for i in brain.cons:
            for j in self.bestbrain.cons:
                if i.inno == j.inno:
                    m += 1
                    break
        return len(brain.cons) + len(self.bestbrain.cons) - 2 * m

    def sort(self):
        # This sorts everything and checks if there's a new high score
        self.students = sorted(self.students, key=lambda s: s.score, reverse=True)
        if len(self.students) == 0:
            self.nochange = 100000000000000000000000000000000000000000000
            return
        if self.students[0].score > self.bestscore:
            self.nochange = 0
            self.bestscore = self.students[0].score
            self.bestbrain = self.students[0].brain.duplicate()
            self.champ = self.students[0].makenew(self.students[0].player)
        else:
            self.nochange += 1

    def setavg(self):
        # I should delete this, but I'm scared of doing so
        self.avg = np.sum([s.score for s in self.students]) / len(self.students)

    def newstudent(self, innohis):
        # This is crossover, or essentially how I make my new students
        # There's a 25% chance of it just getting cloned
        if random.random() <= 0.25:
            child = self.choosepl()
            child = child.makenew(child.player)
        else:
            # And the rest is actually doing stuff
            p1 = self.choosepl()
            p2 = self.choosepl()
            if p1.score < p2.score:
                child = p2.crossover(p1, p1.bads, p1.id, p1.player)
            else:
                child = p1.crossover(p2, p2.bads, p2.id, p2.player)
        # So there's 2 ways that you can change your people, one is crossover, which changes the connections
        # And the other is actually changing the weights, or mutating it
        child.brain.mutate(innohis)
        return child

    def choosepl(self):
        # In order to give everyone a chance, the scores are totalled and a random threshold is chosen
        # As soon as you're above that threshold, you're chosen
        # This creates a 2 parent system that biases towards the better people
        # But everyone will get a chance
        # This is especially good for the complex but low-scoring ones that need more time
        totscore = np.sum([p.score for p in self.students])
        threshold = random.uniform(0, totscore)
        currentnum = 0
        for p in self.students:
            currentnum += p.score
            if currentnum > threshold:
                return p

    def eliminate(self):
        # This eliminates the bottom half of students
        if len(self.students) > 2:
            t = int(np.floor(len(self.students) / 2))
            while t < len(self.students):
                self.students.pop(t)

    def sharescore(self):
        # This makes it a nice ratio that I can work with rather than an objective number
        for i in self.students:
            i.score /= len(self.students)


class ItsALIVE:
    # This is our student's brain
    def __init__(self, ins, outs, cross):
        self.ihateerrors = -1
        self.cons = []
        self.badscoords = []
        self.nodes = []
        self.inputs = ins
        self.outputs = outs
        self.layers = 2
        self.next = 0
        self.network = []
        self.conval = 1
        if cross:
            return
        # If it's the first generation it just makes a blank network, otherwise it's free for crossover to mod it
        self.nodes = [Node(i, 0, 0) for i in range(self.inputs)]
        self.nodes.append(Node(self.inputs + 1, 1, 0))
        self.next = self.inputs + 2

    def nodebyid(self, idnum):
        # Title explains it
        # This needs to be a function in case I don't find the node
        for node in self.nodes:
            if node.id == idnum:
                return node
        return

    def connodes(self):
        # This makes sure that the nodes know what they're sending info to
        for node in self.nodes:
            node.outto = []
        for con in self.cons:
            if con.n1 is not None:
                con.n1.outto.append(con)
            else:
                # This is essentially error detection that's going to yell at you
                # I don't know what the problem is, but it appears so rarely that it only appeared after 5 days of runtime
                print("Something messed up")

    def move(self, x, y, bads):
        # Wow, it moves!
        def mapr(r1, r2, val):
            # This is just a mapr I found on the internet, it essentially takes in 2 ranges and a value
            # Then, it puts the value from one range into the next
            (a1, a2), (b1, b2) = r1, r2
            return b1 + ((val - a1) * (b2 - b1) / (a2 - a1))

        # Don't know why these are still here, but they are
        comps2 = (-x, 825 - x)
        comps3 = (-600, 600)
        # This avoids divide by 0 errors
        # And it calculates the wall distance
        if y > 300:
            dy2 = y - 600
        else:
            dy2 = y
        if dy2 == 0:
            dy2 = 1 / 300
        # This is the input array, I plug in the inverse of delta w, delta x, and delta y by doing 1/d
        badscoords = [[1 / mapr((-300, 300), (-1, 1), dy2), 1 / mapr(comps2, (1, -1), bad.rect.left - x + 1 / 600),
                       1 / mapr(comps3, (-1, 1), (y - bad.rect.top + 1 / 600))] for bad in bads]
        badscoords = sorted(badscoords, key=lambda temp: np.sqrt(temp[1] ** 2 + (1 / temp[2]) ** 2), reverse=True)
        badscoords = np.asarray(badscoords)
        badscoords = list(badscoords.flatten())
        # This gets rid of the duplicate wall nodes
        for e in range(len(bads) - 1):
            badscoords.pop(3 * (e + 1) + 1)
        self.badscoords = badscoords
        # After processing the information, I actually run the numbers, get the output, and reset
        for i in range(self.inputs):
            self.nodes[i].input = badscoords[i]
        for n in self.nodes:
            n.calcoutput()
        output = self.network[-1].output
        for n in self.network:
            n.input, n.output = 0, 0
        return output

    def gennet(self):
        # This organizes the network into layers
        self.connodes()
        self.network = []
        for l in range(self.layers):
            for n in self.nodes:
                if n.layer == l:
                    self.network.append(n)

    def addnode(self, innohis):
        # This adds a node to the network by taking a random connection and replacing it with a node and 2 more
        # One from the original to the new node and one from the new to the next node
        # The first one has a weight of 1 so the overall weight stays the same, there's just a node now
        if len(self.cons) == 0:
            self.addcon(innohis)
            return
        rcon = random.randint(0, len(self.cons) - 1)
        self.cons[rcon].enabled = False
        newn = self.next
        self.nodes.append(Node(newn, self.cons[rcon].n1.layer + 1, 0))
        self.next += 1
        newconnum = self.getinnonum(innohis, self.cons[rcon].n1, self.nodebyid(newn))
        self.cons.append(Connection(self.cons[rcon].n1, self.nodebyid(newn), 1, newconnum))
        newconnum = self.getinnonum(innohis, self.nodebyid(newn), self.cons[rcon].n2)
        self.cons.append(Connection(self.nodebyid(newn), self.cons[rcon].n2, self.cons[rcon].weight, newconnum))
        if self.nodebyid(newn).layer == self.cons[rcon].n2.layer:
            for n in self.nodes:
                if n.layer >= self.nodebyid(newn).layer and n != self.nodebyid(newn):
                    n.layer += 1
            self.layers += 1
        self.connodes()

    def addcon(self, innohis):
        # This adds a connection by taking 2 random nodes and connecting them
        if self.full():
            return
        rn1 = random.randint(0, len(self.nodes) - 1)
        rn2 = random.randint(0, len(self.nodes) - 1)
        while self.nodes[rn1].layer == self.nodes[rn2].layer or self.nodes[rn1].connected(rn2) or self.nodes[
            rn2].connected(rn1):
            rn1 = int(np.floor(random.uniform(0, len(self.nodes))))
            rn2 = int(np.floor(random.uniform(0, len(self.nodes))))
        if self.nodes[rn1].layer > self.nodes[rn2].layer:
            # Literally textbook
            temp = rn2
            rn2 = rn1
            rn1 = temp
        coninnonum = self.getinnonum(innohis, self.nodes[rn1], self.nodes[rn2])
        self.cons.append(Connection(self.nodes[rn1], self.nodes[rn2], random.uniform(0, 1), coninnonum))
        self.connodes()

    def getinnonum(self, innohis, fro, to):
        # This gets a new innonum by checking if there's any duplicates in the past
        new = True
        coninnonum = self.conval
        for n in innohis:
            if n.match(self, fro, to):
                new = False
                coninnonum = n.inno
                break
        if new:
            innonums = [c.inno for c in self.cons]
            innohis.append(Conh(fro.id, to.id, coninnonum, innonums))
            self.conval += 1
        return coninnonum

    def full(self):
        # This checks if the network is full by finding the number of maximum connections
        maxcons = 0
        ninlayers = [0 * l for l in range(self.layers)]
        for n in self.nodes:
            if n.layer >= len(ninlayers):
                print(n.layer, len(ninlayers))
            ninlayers[n.layer] += 1
        for i in range(self.layers):
            nextnodes = 0
            j = i + 1
            while j < self.layers:
                nextnodes += ninlayers[j]
                j += 1
            maxcons += ninlayers[i] * nextnodes
        return maxcons <= len(self.cons)

    def mutate(self, innohis):
        # This is varying the individual networks more, either changing their weights or their structure
        if len(self.cons) == 0:
            self.addcon(innohis)
        if random.random() < 0.8:
            for c in self.cons:
                c.mutate()
        if random.random() < 0.05:
            self.addcon(innohis)
        if random.random() < 0.01:
            self.addnode(innohis)

    def crossover(self, p2):
        # This makes a brain and uses Punnett Square logic to determine who gets what genes
        itsaboy = ItsALIVE(self.inputs, self.outputs, True)
        itsaboy.cons = []
        itsaboy.nodes = []
        itsaboy.layers = self.layers
        itsaboy.next = self.next
        kidsgenes = []
        enabled = []
        for c in self.cons:
            setenable = True
            p2gene = self.matchgene(p2, c.inno)
            if p2gene != -1:
                if not c.enabled or not p2.brain.cons[p2gene].enabled:
                    # Technically False is a dominant gene, plus if something is disabled I want it to mostly stay that way
                    if random.random() < 0.75:
                        setenable = False
                if random.random() < 0.5:
                    # It's a 50-50 chance on what weights the kid starts off with
                    kidsgenes.append(c)
                else:
                    # "You have your mother's missile-dodging logic"
                    kidsgenes.append(p2.brain.cons[p2gene])
            else:
                # If one parent has a new gene, it's automatically passed on
                # A lot of NEAT is just making sure that the complex ones keep on going
                kidsgenes.append(c)
                setenable = c.enabled
            enabled.append(setenable)
        # Duolicates and setting all the genes
        itsaboy.nodes = [n.duplicate() for n in self.nodes]
        itsaboy.cons = [c.duplicate(itsaboy.nodebyid(c.n1.id), itsaboy.nodebyid(c.n2.id)) for c in kidsgenes]
        for c in range(len(itsaboy.cons)):
            itsaboy.cons[c].enabled = enabled[c]
            if itsaboy.cons[c].n1 is None or itsaboy.cons[c].n2 is None:
                # This is a really weird error that I don't know how to fix or how it even happens
                print("Something screwed up, please try again")
        itsaboy.connodes()
        return itsaboy

    def matchgene(self, p2, innonum):
        # This checks if both parents have the same gene
        t = self.ihateerrors
        c = [c.inno for c in p2.brain.cons]
        if innonum in c:
            thing = c.index(innonum)
            return thing
        return t

    def printingisfun(self):
        # fstrings are the MVP
        print(f"Layers: {self.layers} Network: {[n.id for n in self.network]} Connections: {self.cons}")
        for c in self.cons:
            print("Gene: " + str(c.inno) + " From: " + str(c.n1.id) + " To: " + str(c.n2.id) + " Enabled: " + str(
                c.enabled) + " From layer: " + str(c.n1.layer) + " To layer: " + str(c.n2.layer) + " Weight: " + str(
                c.weight))

    def duplicate(self):
        # Cloning technology has reached its true apex - a .duplicate feature
        clone = ItsALIVE(self.inputs, self.outputs, True)
        clone.nodes = [n.duplicate() for n in self.nodes]
        clone.cons = [c.duplicate(clone.nodebyid(c.n1.id), clone.nodebyid(c.n2.id)) for c in self.cons]
        clone.layers = self.layers
        clone.next = self.next
        clone.connodes()
        return clone
