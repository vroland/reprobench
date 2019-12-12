import click

from reprobench.console.decorators import common, server_info, use_tunneling
from reprobench.utils import read_config

from .manager import SlurmManager


@click.command("slurm")
@click.option(
    "-d", "--output-dir", type=click.Path(), default="./output", show_default=True
)
@click.option("-r", "--repeat", type=int, default=1)
@click.argument("command", type=click.Choice(("run", "stop")))
@click.argument("config", type=click.Path(), default="./benchmark.yml")
@click.option("--multirun_cores", type=int, default=0)
@click.option("--additional_args", type=str, default="")
@click.option("--reserve_cores", type=int, default=0)
@click.option("--reserve_memory", type=int, default=0)
@click.option("--reserve_time", type=int, default=0)
@click.option("--reserve_hosts", type=int, default=1)
@server_info
@use_tunneling
@common
def cli(command, **kwargs):
    manager = SlurmManager(**kwargs)

    if command == "run":
        manager.run()
    elif command == "stop":
        manager.stop()


if __name__ == "__main__":
    cli()
