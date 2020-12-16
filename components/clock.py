from qunetsim.objects import DaemonThread


class Clock(object):
    """
    This is a clock simulator which synchronises the scheduled operations in computing
    hosts
    """

    def __init__(self):

        """
        Returns the important things for the clock object
        """

        self._ticks = 0
        self._maximum_ticks = 0
        self._response = 0
        self._stop = False

        self._computing_hosts = []

    @property
    def ticks(self):
        """
        Number of times the clock has ticked
        """
        return self._ticks

    def attach_host(self, computing_host):
        """
        This function attaches the computing host who will listen to the clock object
        tick

        Args:
            (ComputingHost): Computing host object which carries out the scheduled task
        """
        self._computing_hosts.append(computing_host)

    def detach_host(self, computing_host):
        """
        This function detached the computing host from the clock object

        Args:
            (ComputingHost): Computing host object which carries out the scheduled task
        """
        self._computing_hosts.append(computing_host)
        self._observers.remove(observer)

    def respond(self):
        """
        Track the number of responses received by the clock
        """
        self._response += 1

    def initialise(self, controller_host):
        """
        Obtain the maximum number of ticks for a clock from the controller host object

        Args:
            (ControllerHost): Controller host object which is the master node in the
                centralised distributed network system
        """

        self._stop = False

        maximum_ticks = controller_host._circuit_max_execution_time
        self._maximum_ticks = maximum_ticks

    def stop(self):
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