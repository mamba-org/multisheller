# sh multiplexer

This project implements a simple DSL (in Python) to generate shell scripts for many different shells.
This is particularly useful for conda-recipes (specifically the sometimes used activation and deactivation scripts).

If one writes the activation or deactivation script using this project, it is trivial to generate the same activation flow for many different shells:

- bash
- powershell
- cmd.bat
- zsh
- xonsh

This grew out of a frustration on how hard it is to write bash / cmd.bat scripts that work cross-platform and for all shells that people use (esp. powershell).

Examples:

```py
from multisheller import cmds, path

conda_prefix = cmds.env("CONDA_PREFIX")
print(cmds.if_(conda_prefix == "test").then_(
	cmds.export("TEST_VARIABLE", path.join(cmds.env("CONDA_PREFIX"), "test/for/something"))
))
```

This prints:

```sh
if [ $CONDA_PREFIX == test ];
then;
    export TEST_VARIABLE=$CONDA_PREFIX/test/for/something
fi;
```

Which, at this point, might not even be correct bash. But it hopefully helps to illustrate the idea.
Only a rudimentary bash backend has been implemented so far!
