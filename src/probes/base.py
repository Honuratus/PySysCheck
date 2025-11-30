class Probe:
    """
    base interface for all hardware probes
    """

    def __init__(self):
        self.data = {}

    def run_probe(self):
        """
        main method to execute the probin logic
        must be implemented by child classes
        """
        raise NotImplementedError('Subclasses must implement run_probe()')
    