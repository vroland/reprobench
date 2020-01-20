from datetime import datetime
from reprobench.core.db import BaseModel, Run
from playhouse.apsw_ext import (
    ForeignKeyField,
    FloatField,
    CharField,
    IntegerField,
    DateTimeField,
    TextField
)


class RunStatistic(BaseModel):
    TIMEOUT = "TLE"
    MEMOUT = "MEM"
    RUNTIME_ERR = "RTE"
    OUTPUT_LIMIT = "OLE"
    SUCCESS = "OK"

    VERDICT_CHOICES = (
        (TIMEOUT, "Time Limit Exceeded"),
        (MEMOUT, "Memory Limit Exceeded"),
        (RUNTIME_ERR, "Runtime Error"),
        (OUTPUT_LIMIT, "Output Limit Exceeded"),
        (SUCCESS, "Run Successfully"),
    )

    created_at = DateTimeField(default=datetime.now)
    run = ForeignKeyField(
        Run, backref="statistics", on_delete="cascade", primary_key=True
    )
    cpu_time = FloatField(help_text="CPU Time (s)", null=True)
    wall_time = FloatField(help_text="Wall Clock Time (s)", null=True)
    max_memory = FloatField(help_text="Max Memory Usage (KiB)", null=True)
    return_code = IntegerField(help_text="Process Return Code", null=True)
    verdict = CharField(choices=VERDICT_CHOICES, max_length=3, null=True)


class RunStatisticExtended(BaseModel):
    TIMEOUT = "TLE"
    MEMOUT = "MEM"
    RUNTIME_ERR = "RTE"
    OUTPUT_LIMIT = "OLE"
    SUCCESS = "OK"

    VERDICT_CHOICES = (
        (TIMEOUT, "Time Limit Exceeded"),
        (MEMOUT, "Memory Limit Exceeded"),
        (RUNTIME_ERR, "Runtime Error"),
        (OUTPUT_LIMIT, "Output Limit Exceeded"),
        (SUCCESS, "Run Successfully"),
    )

    created_at = DateTimeField(default=datetime.now)
    run = ForeignKeyField(
        Run, backref="statistics", on_delete="cascade", primary_key=True
    )
    runsolver_WCTIME = FloatField(help_text="Wall Clock Time (s)", null=True)
    runsolver_CPUTIME = FloatField(help_text="CPU Time (s)", null=True)
    runsolver_USERTIME = FloatField(null=True)
    runsolver_SYSTEMTIME = FloatField(null=True)
    runsolver_CPUUSAGE = FloatField(null=True)
    runsolver_MAXVM = FloatField(help_text="Max Memory Usage (MiB)", null=True)
    runsolver_TIMEOUT = TextField(null=True)
    runsolver_MEMOUT = TextField(null=True)
    runsolver_STATUS = IntegerField(null=True)
    runsolver_SEGFAULT = CharField(null=True)
    runsolver_error = CharField(null=True)

    perf_dTLB_load_misses = FloatField(null=True)
    perf_dTLB_loads = FloatField(null=True)
    perf_dTLB_store_misses = FloatField(null=True)
    perf_dTLB_stores = FloatField(null=True)
    perf_iTLB_load_misses = FloatField(null=True)
    perf_iTLB_loads = FloatField(null=True)
    perf_cycles = FloatField(null=True)
    perf_cache_misses = FloatField(null=True)
    perf_stall_cycles = FloatField(null=True)
    perf_elapsed = FloatField(null=True)
    perf_cpu_migrations = FloatField(null=True)
    perf_page_faults = FloatField(null=True)
    perf_context_switches = FloatField(null=True)
    return_code = IntegerField(null=True)

    #think about removing; but duplicate data helps here to work faster...
    platform = CharField(null=True)
    hostname = CharField(null=True)

    cpu_time = FloatField(help_text="CPU Time (s)", null=True)
    wall_time = FloatField(help_text="Wall Clock Time (s)", null=True)
    max_memory = FloatField(help_text="Max Memory Usage (KiB)", null=True)
    return_code = IntegerField(help_text="Process Return Code", null=True)
    verdict = CharField(choices=VERDICT_CHOICES, max_length=3, null=True)
