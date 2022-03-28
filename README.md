# slurminade

*slurminade* makes using der workload manager [slurm](https://slurm.schedmd.com/documentation.html) with Python beautiful.
It is based on [simple_slurm](https://github.com/amq92/simple_slurm), but instead of just allowing to comfortably execute shell commands in slurm, it allows to directly distribute Python-functions.
A function decorated with `@slurminade.slurmify(partition="alg")` will automatically be executed by a node of the partition `alg` by just calling `.distribute(yes_also_args_are_allowed)`.
The general idea is that the corresponding Python-code exists on both machines, thus, the slurm-node can also call the functions of the original code if you tell if which one and what arguments to use.
This is similar to [celery](https://github.com/celery/celery) but you do not need to install anything, just make sure the same Python-environment is available the nodes (usually the case in a proper slurm setup).

A simple script that executes a function three times on slurm-nodes could look like this:
```python

import slurminade
import datetime

# Settings for slurm
slurminade.update_default_configuration(partition="alg", constraint="alggen02")


@slurminade.slurmify()
def test(file_name, text):
    with open("slurminade_example.txt", "w") as f:
        f.write(hello_world)

# Without the `if`, the node would also execute this part (*slurminade* will abort automatically)
if __name__ == "__main__":
    # Call the function remotely.
    test.distribute("slurminade_test_1.txt", f"Hello World from slurminade! {str(datetime.datetime.now())}")
    test.distribute("slurminade_test_2.txt", f"Hello World from slurminade! {str(datetime.datetime.now())}")
    test.distribute("slurminade_test_3.txt", f"Hello World from slurminade! {str(datetime.datetime.now())}")
```

> :warning: You should not use this to spam your slurm environment with tasks. Only distribute a function call if it takes at least a few seconds, otherwise it will be faster to run it locally.

We recommend to use *slurminade* with [conda](https://docs.conda.io/en/latest/).
We have not tested it with other virtual environments.

The code is super simple and open source, don't be afraid to create a fork that fits your own needs.

## Installation

You can install *slurminade* with `pip install slurminade`.

> :warning: *slurminade* is still under development. I tested it only for some simple use cases. Please expect some bugs.

## Usage

You can set task specific slurm arguments within the decorator, e.g., `@slurminade.slurmify(constraint="alggen03")`.
This arguments are directly passed to *simple_slurm*, such that all its arguments are supported.

In order for *slurminade* to work, the code needs to be in a Python file/project shared by all slurm-nodes.
Otherwise, *slurminade* will not find the corresponding function.
The function must also be on the top level of Python such that it is available after a simple `import` of the main-file.
Currently, all function names must be unique as *slurminade* will only transmit the function's name.

## Debugging

You can use `.local` instead of `.distribute` to run the task on the local computer, 
without slurm. If there is a bug, you will directly see it in the output (at least for most bugs).
