""" It requires simpy and matplotlib. This example code showing a use of
SimPy simulation with the starting idea below:
##
                                SimPy environment
                                    (Switch)
               +-----------+            |            +-----------+
               |           |            |            |           |
               |  Client2  | <<------+Buffer ------- |  Client1  |
               |           |          Queue          |           |
               +-----------+            |            +-----------+
                Process RX              |              Process TX

Author: xoujez03
Only supports Python3.x
This file is distributed WITHOUT ANY WARRANTY.
Inspired by SimPy https://simpy.readthedocs.org/
"""

import simpy                        # simulation, is needed to install it with pip
import simpy.rt                     # simulation in real time, is needed to install it with pip
import time                         # included
import matplotlib.pyplot as pyplot  # plotting graph, is needed to install it with pip
import sys                          #
from termcolor import colored       # colored command line output


SIM_DURATION = 300      # Simulation duration
BUFFER = 1000           # Maximum capacity
LIMIT_BUFFER = 100      # Buffer limit
QUEUE = 1               # Queue processes
PER = []
TIME_DURATION = []


def drop(switch):
    dropped = 1
    yield switch.fifo.get(dropped)


def rx(num, env, switch):
    with switch.send.request() as req:  # Generate a request event
        yield req                       # Wait for process access
        print('Packet %s was posted as %sth' % (num, env.now))
        switch.fifo.put(1)
        percent = switch.fifo.level
        PER.append(percent)
        print('TX %s done PUT packet in %s order > fifo is from %s%% full' % (num, env.now, percent))


def tx(num, env, switch):
    with switch.transmit.request() as tr_req:
        yield tr_req
        percent = switch.fifo.level
        print('RX %s done GET packet in %s order > fifo is from %s%% full' % (num, env.now, percent))
    yield switch.fifo.get(1)


def tx_generator(env, switch):
    for i in range(SIM_DURATION):
        env.process(tx(i, env, switch))
        yield env.timeout(2)


def rx_generator(env, switch):
    start = time.perf_counter()
    for i in range(SIM_DURATION - 1):
        env.process(rx(i, env, switch))
        yield env.timeout(1)  # duration steps
    end = time.perf_counter()
    print(colored('Duration of one simulation time unit: %.7fs' % (end - start), 'blue'))
    TIME_DURATION.append((end - start))


def plots():
    """
    This plots(): plots the graph of buffer capacity during a simulation
    """
    font = {'fontname': 'Cambria'}
    pyplot.axis([0, 300, 0, 5 + LIMIT_BUFFER / BUFFER * 1000])
    pyplot.title('Scenario SimPy buffer', font)
    pyplot.line = pyplot.plot(PER, label=TIME_DURATION)
    pyplot.legend(loc=2)
    pyplot.ylabel("Messages in queue (num)", font)
    pyplot.xlabel("Simulation Time (s)", font)
    pyplot.grid(True)
    pyplot.show()


class Switch():
    """

    """

    def __init__(self, env):
        self.send = simpy.Resource(env, capacity=QUEUE)  # ??? like access with semaphore
        self.fifo = simpy.Container(env, init=0, capacity=BUFFER)
        self.transmit = simpy.Resource(env, capacity=QUEUE)
        self.monitor_fifo = env.process(self.monitor_fifo(env))

    def monitor_fifo(self, env):
        while True:
            if self.fifo.level >= LIMIT_BUFFER:
                print(colored('Buffer overflow! Smash it', 'red'))
                env.process(drop(self))
            yield env.timeout(1)


# main

def main():
    """Program entry point."""
    import cProfile  # for testing purpose
    import pstats

    """
    Note that this only works in Python 3.x

    """
    profiler = cProfile.Profile()
    profiler.enable()
    env = simpy.Environment()  # is possible use rt.RealtimeEnvironment(factor=0.1)  {REAL TIME} instead
    switch = Switch(env)
    rx_proc = env.process(rx_generator(env, switch))
    env.process(tx_generator(env, switch))
    env.run(until=rx_proc)

    plots()  # for plot the result erase hash

    # Testing
    profiler.create_stats()
    stats = pstats.Stats(profiler)
    stats.strip_dirs().sort_stats("cumulative").print_stats()
    stats.print_callers()

if __name__ == '__main__':
    status = main()
    sys.exit(status)
