from reprobench.core.server import BenchmarkServer
from loguru import logger
import sys

logger.add(sys.stderr, level="TRACE")
s = BenchmarkServer("tcp://127.0.0.1:31313", verbosity=2)

s.run()
