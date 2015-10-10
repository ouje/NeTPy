# NeTPy

This is example of Simpy 3 simulation. 

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
