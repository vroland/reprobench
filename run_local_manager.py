from reprobench.managers.local import LocalManager

m = LocalManager(num_workers=1, server_address="tcp://172.26.62.66:31313", output_dir="output", processes=2,
                 config="./benchmark.yml", tunneling=None, repeat=1, rbdir="")

m.run()
