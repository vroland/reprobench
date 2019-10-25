from reprobench.core.server import BenchmarkServer
from loguru import logger
import sys

logger.add(sys.stderr, level="TRACE")
s = BenchmarkServer("tcp://*:31313", verbosity=2)

s.run()
