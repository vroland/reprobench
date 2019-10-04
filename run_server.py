from reprobench.core.server import BenchmarkServer

s = BenchmarkServer("tcp://127.0.0.1:31313")

s.run()
