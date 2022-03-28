import inspect
import os.path
import subprocess
import sys
import json
import simple_slurm
from .guard import guard_recursive_distribution
from .conf import _get_conf


class SlurmFunction:
    function_map = {}
    mainf = None

    def __init__(self, slurm_conf, func):
        conf = _get_conf(slurm_conf)
        self.slurm = simple_slurm.Slurm(**conf)
        self.fname = func.__name__
        self.func = func
        if func.__name__ in self.function_map:
            raise RuntimeError("Slurminade functions must have unique names!")
        self.function_map[func.__name__] = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def _serialize_args(self, *args, **kwargs):
        inspect.signature(self.func).bind(*args, **kwargs)
        data = {"args": args, "kwargs": kwargs}
        serialized = json.dumps(data)
        if len(serialized) > 300:
            print(f"WARNING: Using slurminde function {self.fname} with long function "
                  f"arguments ({len(serialized)}. This can be bad.")
        return serialized

    def _get_command(self, *args, **kwargs):
        import __main__
        mainf = __main__.__file__
        if not os.path.isfile(mainf) or not mainf.endswith(".py"):
            raise RuntimeError("Cannot reproduce function call from command line.")

        argd = self._serialize_args(*args, **kwargs)
        slurm_task = f"{sys.executable} -m slurminade.execute {mainf} {self.fname} '{argd}'"
        return slurm_task

    def distribute(self, *args, **kwargs):
        guard_recursive_distribution()
        slurm_task = self._get_command(*args, **kwargs)
        self.slurm.sbatch(slurm_task)

    def local(self, *args, **kwargs):
        """
        This function simulates a distribution but runs on the local computer.
        Great for debugging.
        """
        slurm_task = self._get_command(*args, **kwargs)
        process = subprocess.Popen(slurm_task, shell=True)
        process.wait()


    @staticmethod
    def call(func_id, argj):
        argd = json.loads(argj)
        SlurmFunction.function_map[func_id](*argd["args"], **argd["kwargs"])


def slurmify(f=None, **args):
    if f:  # use default parameters
        return SlurmFunction({}, f)
    else:
        def dec(func):
            return SlurmFunction(args, func)

        return dec
