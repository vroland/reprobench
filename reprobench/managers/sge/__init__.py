import click
import sys
from .manager import SgeManager
from reprobench.console.decorators import server_info, common, use_tunneling


@click.command("sge")
@click.option(
    "-d", "--output-dir", type=click.Path(), default="./output", show_default=True
)
@click.option("-r", "--repeat", type=int, default=1)
@click.option("--multirun_cores", type=int, default=0)
@click.argument("command", type=click.Choice(("run", "stop")))
@click.argument("config", type=click.Path(), default="./benchmark.yml")
@click.option("--additional_args", type=str, default="")
@server_info
@use_tunneling
@common
def cli(command, **kwargs):
    manager = SgeManager(**kwargs)

    if command == "run":
        manager.run()
    elif command == "stop":
        manager.stop()


if __name__ == "__main__":
    cli()
