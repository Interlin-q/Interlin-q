class Clock(object):
    """
    This is a clock simulator which synchronises the scheduled operations in computing
    hosts
    """

    def __init__(self):
        self._ticks = 0
        self._maximum_ticks = 0

        self._computing_hosts = []

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

    def tick(self) -> None:
        """
        Tick the clock and trigger operations in the computings hosts
        """

        for host in self._computing_host:
            host.update(self)

    def initialise_clock(self, controller_host):
        """
        Obtain the maximum number of ticks for a clock from the controller host object

        Args:
            (ControllerHost): Controller host object which is the master node in the
                centralised distributed network system
        """

        maximum_ticks = controller_host._circuit_max_execution_time
        self._maximum_ticks = maximum_ticks
