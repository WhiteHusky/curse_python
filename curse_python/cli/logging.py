import progressbar
import logging
progressbar.streams.wrap_stderr()

logger = logging.getLogger("Curse Python")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(' %(name)s - [%(levelname)s] %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)