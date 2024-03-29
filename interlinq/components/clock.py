from qunetsim.objects import DaemonThread


class Clock(object):
    """
    This is a clock simulator which synchronises the scheduled operations in computing
    hosts
    """

    __instance = None

    @staticmethod
    def get_instance():
        if Clock.__instance is None:
            Clock()
        return Clock.__instance

    @staticmethod
    def reset_clock():
        if Clock.__instance is not None:
            Clock.__instance.stop_clock()
            Clock.__instance = None
        __instance = Clock()

    def __init__(self):
        """
        Returns the important things for the clock object
        """
        if Clock.__instance is None:
            self._ticks = 0
            self._maximum_ticks = 0
            self._response = 0
            self._stop = False
            self._computing_hosts = []
            Clock.__instance = self
        else:
            raise Exception("This is a singleton class. Use get_instance().")

    @property
    def ticks(self):
        """
        Number of times the clock has ticked
        """
        return self._ticks

    @property
    def has_stopped(self):
        """
        Check if the clock has stopped
        """
        return self._stop

    def attach_host(self, computing_host: "ComputingHost"):
        """
        Attach the computing host who will listen to the clock object tick

        Args:
            (ComputingHost): Computing host object which carries out the scheduled task
        """
        self._computing_hosts.append(computing_host)

    def detach_host(self, computing_host: "ComputingHost"):
        """
        Detach the computing host from the clock object

        Args:
            (ComputingHost): Computing host object which carries out the scheduled task
        """
        for host in self._computing_hosts:
            if host.host_id == computing_host.host_id:
                del host
                break

    def respond(self):
        """
        Track the number of responses received by the clock
        """
        self._response += 1

    def initialise(self, max_execution_time: int):
        """
        Initialise the clock with the maximum number of times the clock should tick

        Args:
            (int): Maximum number of times the clock should tick
        """
        self._stop = False
        self._maximum_ticks = max_execution_time

    def stop_clock(self):
        """
        Stop ticking the clock, due to an error being triggered
        """
        self._stop = True

    def start(self):
        """
        Starts the clock which triggers all the computing hosts to start performing
        the schedule
        """
        if not self._maximum_ticks:
            raise ValueError("Set the maximum number of ticks to start the clock")

        # Tick the clock
        while self._ticks <= self._maximum_ticks:
            self._response = 0

            if self._stop:
                print("Clock stopped ticking due to an error")
                break

            for host in self._computing_hosts:
                DaemonThread(host.perform_schedule, args=(self._ticks,))

            # Wait to receive responses from all the computing hosts
            while self._response < len(self._computing_hosts):
                pass
            self._ticks += 1
        self.stop_clock()
