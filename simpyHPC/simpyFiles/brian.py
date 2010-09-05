
from SimPy.SimulationTrace import * ## Only change in program!
#from SimPy.Simulation import *
#from SimPy.SimPlot import *
from random import expovariate, seed
import math, sqlite3

## Model components ------------------------

class Generator(Process):
    """Generates Users which arrive at the application cluster"""

    def execute(self, maxCustomers, rate, stime, cluster):

        for i in range(maxCustomers):
            L = User("User "+`i`,sim=self.sim)
            self.sim.activate(L, L.execute(stime, cluster), delay=0)
            yield hold,self,expovariate(rate)

class User(Process):
        
    NoTotal = 0
    NoAccepted = 0
    NoDenied = 0
    def execute(self, stime, cluster):
        """Simulate a single user

        Parameters:
        stime -- the parameter to a Poisson distribution (in seconds)
            which defines the service time process
        cluster -- the cluster this user is to arrive at

        """
        User.NoTotal += 1
        server = cluster.find_server()
        if server is None:
            User.NoDenied += 1
            self.sim.mBlockingProbability.observe(float(User.NoDenied) / User.NoTotal)
            self.sim.mBlocked.observe(1)
            #print 'I am customer %s and I have been denied' % User.NoTotal
        else:
            yield request, self, server
            User.NoAccepted += 1
            #print 'NoDenied = %s and NoTotal = %s and bp = %s' % (User.NoDenied, User.NoTotal, float(User.NoDenied) / User.NoTotal)
            self.sim.mBlockingProbability.observe(float(User.NoDenied) / User.NoTotal)
            self.sim.mBlocked.observe(0)
            #self.trace("Getting Service ")
            t = expovariate(1.0/stime)
            self.sim.msT.observe(t)
            yield hold, self, t
            yield release, self, server
        #self.trace("Leaving   ")
       
    def trace(self,message):
        FMT="%7.4f %6s %10s (%2d)"
        if TRACING:
            print FMT%(self.sim.now(),self.name,message,User.NoTotal)


class Cluster(object):


    total_prov = 0
    total_put_into_service = 0
    total_deleted = 0
    def __init__(self, sim, density=1):
        self.booting = []
        self.active = []
        self.shutting_down = []
        self.density = density
        self.sim = sim

    def __str__(self):
        """Prints a brief, one-liner about the Cluster

        cluster

        """
        return 'Cluster(booting=%d, active=%d, shutting_down=%d)' % \
             (len(self.booting), len(self.active), len(self.shutting_down))

    def create_VM(self):
        """Create a Resource of size self.density and return it

        The Resource created will be assigned the appropriate _next_priority

        """
        r = Resource(capacity=self.density, name='',sim=self.sim, qType=PriorityQ)
        r.rank = self._next_priority()
        #raw_input('creating VM with priority %s' % self._next_priority())
        return r

    def find_server(self):

        for VM in sorted(self.active, key=lambda r: r.rank):
            if VM.n > 0:
                return VM
        return None

    @property
    def capacity(self):

        return (len(self.booting) + len(self.active)) * self.density

    @property
    def n(self):
        
        return reduce(lambda x, y: x + y.n, self.booting + self.active, 0)

    def _next_priority(self):

        in_order = sorted(self.booting + self.active + self.shutting_down, 
            key=lambda r: r.rank)
        for i in range(len(in_order)):
            if i != in_order[i].rank:
                return i
        return len(in_order)

class Scale(Process):


    def execute(self, cluster, scale_rate, reserved):
    

        while True:
            # Put the existing 'booting' VMs into service
            # @TODO, not ALL VMs are really finsihed booting so this should be more accurate
            # Put the booting VMs into service
            not_to_be_shut_off_list = []
            for s in cluster.booting:
                if self.sim.now() > s.ready_time:
                    #raw_input('Server %d is now active' % s.rank)
                    cluster.booting.remove(s)
                    cluster.active.append(s)
                    not_to_be_shut_off_list.append(s)

            diff = cluster.n - reserved
            if diff < 0:
                servers_to_start = int(math.ceil(abs(float(diff) / cluster.density)))
                for server in range(servers_to_start):
                    if cluster.shutting_down:
                        new_vm = cluster.shutting_down.pop()
                        not_to_be_shut_off_list.append(new_vm)
                        #raw_input('removing server %d from shutting down state and putting back in ACTIVE' % new_vm.rank)
                        cluster.active.append(new_vm)
                    else:
                        new_vm = cluster.create_VM()
                        new_vm.ready_time = self.sim.now() + 300
                        cluster.booting.append(new_vm)
                        Cluster.total_prov += 1
                        #raw_input('server booting.  it will be READY AT %s' % new_vm.ready_time)

            for server in cluster.shutting_down:
                if self.sim.now() > server.power_off_time:
                    #raw_input('DELETING server %d' % server.rank)
                    Cluster.total_deleted += 1
                    cluster.shutting_down.remove(server)

            for server in cluster.active:
                if server.activeQ == [] and server not in not_to_be_shut_off_list:
                    server.power_off_time = self.sim.now() + 300
                    #raw_input('Server %d is empty, shutting it down.  It will be powered off at %d' % (server.rank, server.power_off_time))
                    cluster.active.remove(server)
                    cluster.shutting_down.append(server)

            self.sim.mClusterActive.observe(len(cluster.active))  # monitor cluster.active
            self.sim.mClusterBooting.observe(len(cluster.booting))  # monitor cluster.booting
            self.sim.mClusterShuttingDown.observe(len(cluster.shutting_down))  # monitor cluster.shutting_down

            # Wait an amount of time to allow the scale function to run periodically
            yield hold, self, scale_rate

## Experiment data -------------------------

#TRACING = True
#reserved = 3 # the reserved param for the cluster
#density = 3 # number of servers per VM
#stime = 1.0 # mean service time
#rate  = 4.0 # mean arrival rate 
#maxCustomers = 24000 # total number of customers to simulate for
#simulationLength = (maxCustomers + 2) * (1.0 / rate)
#scale_rate = 18.0 # Rate of scale arrivals
#seed(333555777) ## seed for random numbers

## Model -----------------------------------
class MMCCmodel(Simulation):
    name = "app_sim.tasks.MMCCmodel"
    def run(self, reserved, density, stime, rate, maxCustomers, scale_rate, rand_seed):
        seed(rand_seed)
        simulationLength = (maxCustomers + 2) * (1.0 / rate)
        self.initialize()
        self.msT = Monitor(sim=self)  # monitor for the generated service times
        self.mClusterActive = Monitor(sim=self)  # monitor cluster.active with each scale event
        self.mClusterBooting = Monitor(sim=self)  # monitor cluster.booting with each scale event
        self.mClusterShuttingDown = Monitor(sim=self)  # monitor cluster.shutting_down with each scale event
        self.mBlockingProbability = Monitor(sim=self, ylab='BP(t)', 
            tlab='seconds')  # monitor for the cumulative observed blocking probability
        self.mBlocked = Monitor(sim=self)  # monitor observing if a customer is blocked or not
        self.cluster = Cluster(self, density)
        s = Scale(name='Scale Function', sim=self)
        g = Generator(name='User Arrival Generator',sim=self)
        self.activate(s,s.execute(cluster=self.cluster, scale_rate=scale_rate, reserved=reserved))
        self.activate(g,g.execute(maxCustomers=maxCustomers, rate=rate, 
            stime=stime, cluster=self.cluster))
        self.simulate(until=simulationLength)
    
        size = (len(self.mBlocked) / 31)
        lower = 0
        estimates = []
        for batch in range(0,31):
            upper = lower + size
            #print 'batch %s has [%s:%s]' % (batch, lower, upper)
            slice = self.mBlocked[lower:upper]
            lower = upper


        return 9
