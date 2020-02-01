import itertools
import json
from pathlib import Path

from loguru import logger
from peewee import chunked
from tqdm import tqdm

from reprobench.core.db import (
    MODELS,
    Limit,
    Observer,
    Parameter,
    ParameterGroup,
    Run,
    Step,
    Task,
    TaskGroup,
    Tool,
    db,
    Task2Tool)
from reprobench.utils import (
    check_valid_config_space,
    get_db_path,
    import_class,
    init_db,
    is_range_str,
    parse_pcs_parameters,
    str_to_range,
)

try:
    from ConfigSpace.read_and_write import pcs
except ImportError:
    pcs = None


def bootstrap_db(output_dir):
    db_path = get_db_path(output_dir)
    init_db(db_path)
    db.connect()
    db.create_tables(MODELS, safe=True)


def bootstrap_limits(config):
    # TODO: handle limit changes
    query = Limit.insert_many(
        [{"key": key, "value": value} for (key, value) in config["limits"].items()]
    ).on_conflict("ignore")
    query.execute()


def bootstrap_steps(config):
    count = Step.select().count()
    new_steps = config["steps"]["run"][count:]
    if len(new_steps) > 0:
        query = Step.insert_many(
            [
                {
                    "category": "run",
                    "module": step["module"],
                    "config": json.dumps(step.get("config", None)),
                }
                for step in new_steps
            ]
        )
        query.execute()


def bootstrap_observers(config, server):
    count = Observer.select().count()
    new_observers = config["observers"][count:]
    if len(new_observers) > 0:
        query = Observer.insert_many(
            [
                {
                    "module": observer["module"],
                    "config": json.dumps(observer.get("config", None)),
                }
                for observer in new_observers
            ]
        )
        query.execute()

        for observer in new_observers:
            observer_class = import_class(observer["module"])
            observer_class.observe(server)


def register_steps(config):
    logger.info("Registering steps...")
    for step in itertools.chain.from_iterable(config["steps"].values()):
        import_class(step["module"]).register(step.get("config", {}))


def bootstrap_tasks(config):
    for (name, tasks) in config["tasks"].items():
        logger.error(f"{name}, {tasks}")
        TaskGroup.insert(name=name).on_conflict("ignore").execute()
        with db.atomic():
            for batch in chunked(tasks, 100):
                query = Task.insert_many(
                    [{"path": task[0], "instance": task[1], "group": name} for task in batch]
                ).on_conflict("ignore")
                query.execute()


# TODO: merge all this into one entity (if we move to a document storage)
# does conceptually only make partially sense
def bootstrap_tasks2tools(config):
    tasks2tools = []
    for (tool_name, run_config) in config["runs"].items():
        logger.error(tool_name)
        if Tool.select().where(Tool.name == tool_name).count() != 1:
            logger.warning("Tool not found or multiple entries. Things might go wrong. "
                           "Pls check your configuration file.")
        for group, tasks in run_config.items():
            logger.warning(group)
            logger.warning(tasks)
            for task in tasks:
                if TaskGroup.select().where(TaskGroup.name == task).count() != 1:
                    logger.warning(
                        "Benchmark task missing or duplicate entry. Things might go wrong. "
                        "Pls check your configuration file.")
                tasks2tools.append(dict(benchmark_name=config["title"], tool=tool_name, task=task, pg=group))
    logger.debug(f"Inserting tasks: {tasks2tools}")
    query = Task2Tool.insert_many(tasks2tools).on_conflict_ignore()
    query.execute()


def create_parameter_group(tool, group, parameters):
    PCS_KEY = "__pcs"
    pcs_parameters = {}
    use_pcs = PCS_KEY in parameters
    config_space = None

    if use_pcs:
        pcs_text = parameters.pop(PCS_KEY)
        lines = pcs_text.split("\n")
        config_space = pcs.read(lines)
        pcs_parameters = parse_pcs_parameters(lines)

    ranged_enum_parameters = {
        key: value
        for key, value in parameters.items()
        if isinstance(parameters[key], list)
    }

    ranged_numbers_parameters = {
        key: str_to_range(value)
        for key, value in parameters.items()
        if isinstance(value, str) and is_range_str(value)
    }

    ranged_parameters = {
        **pcs_parameters,
        **ranged_enum_parameters,
        **ranged_numbers_parameters,
    }

    if len(ranged_parameters) == 0:
        parameter_group, _ = ParameterGroup.get_or_create(name=group, tool=tool)

        for (key, value) in parameters.items():
            query = Parameter.insert(
                group=parameter_group, key=key, value=value
            ).on_conflict("replace")
            query.execute()
        return

    constant_parameters = {
        key: value for key, value in parameters.items() if key not in ranged_parameters
    }

    tuples = [
        [(key, value) for value in values] for key, values in ranged_parameters.items()
    ]

    for combination in itertools.product(*tuples):
        parameters = {**dict(combination), **constant_parameters}

        if use_pcs:
            check_valid_config_space(config_space, parameters)

        combination_str = ",".join(f"{key}={value}" for key, value in combination)
        group_name = f"{group}[{combination_str}]"

        parameter_group, _ = ParameterGroup.get_or_create(name=group_name, tool=tool)

        for (key, value) in parameters.items():
            query = Parameter.insert(
                group=parameter_group, key=key, value=value
            ).on_conflict("replace")
            query.execute()


def bootstrap_tools(config):
    logger.info("Bootstrapping tools...")

    # FIXME
    for tool_name, tool in config["tools"].items():
        query = Tool.insert(name=tool_name, module=tool["module"]).on_conflict(
            "replace"
        )
        query.execute()

        if "parameters" not in tool or tool["parameters"] is None:
            create_parameter_group(tool_name, "default", {})
            continue

        for group, parameters in tool["parameters"].items():
            create_parameter_group(tool_name, group, parameters)


def bootstrap_runs(benchmark_name, output_dir, repeat=1, cluster_job_id=-1):
    tasks = Task.select().iterator()
    logger.warning([x for x in tasks])
    tasks2tools = Task2Tool.select().where(Task2Tool.benchmark_name == benchmark_name)

    logger.error([x for x in tasks2tools.namedtuples()])
    # collect task groups
    params = {}
    for tt_id, benchmark_name, task, tool, group in tasks2tools.namedtuples():
        logger.trace(f"Considering: tt_id: {tt_id}, benchmark_name: {benchmark_name}, task: {task}, "
                     f"tool: {tool}, group: {group}")
        for pg_id, pg_name, pg_tool in \
            ParameterGroup.select().where(ParameterGroup.tool_id == tool).namedtuples():
            logger.trace(f"pg_id: {pg_id}, pg_name:{pg_name}, pg_tool: {pg_tool}")
            # TODO: fixme here...
            if group != 'all':
                configs = [x for x in group.split("/")]
                if any([c not in pg_name for c in configs]):
                    continue
            p = dict(tt_id=tt_id, pg_id=pg_id, benchmark_name=benchmark_name, tool=tool, parameters=pg_name)
            if task in params:
                params[task].append(p)
            else:
                params[task] = [p]
            logger.trace(p)

    logger.trace("Merging task groups with tasks.")
    with db.atomic():
        for t_id, group, path, instance in tqdm(Task.select().namedtuples(), desc="Bootstrapping runs"):
            logger.trace(f"group:{group}, path:{path}, instance:{instance}")
            if group not in params:
                continue
            for e in params[group]:
                # tt_id, benchmark_name, tool, parameters
                logger.info(f"|path| {path}")
                logger.info(f"|group| {group} |e| {e}")
                for iteration in range(repeat):
                    logger.error(path)
                    directory = (
                        Path(output_dir)
                        / e['tool']
                        / e['parameters']
                        / group
                        / instance
                        / str(iteration)
                    )
                    myrun = dict(id=str(directory), cluster_job_id=cluster_job_id, tool=e['tool'],
                                 task=t_id, parameter_group=e['pg_id'], status=Run.PENDING,
                                 iteration=iteration)
                    logger.debug(myrun)
                    query = Run.insert(myrun)  # .on_conflict("ignore")
                    query.execute()
    return


def bootstrap(config=None, output_dir=None, repeat=1, server=None, cluster_job_id=-1):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    bootstrap_db(output_dir)
    bootstrap_limits(config)
    bootstrap_steps(config)
    bootstrap_observers(config, server)
    register_steps(config)
    bootstrap_tasks(config)
    bootstrap_tools(config)
    bootstrap_tasks2tools(config)
    logger.critical(output_dir)
    bootstrap_runs(config['title'], output_dir, repeat, cluster_job_id)
