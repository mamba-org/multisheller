# sh multiplexer

This project implements a simple DSL (in Python) to generate shell scripts for many different shells.
This is particularly useful for conda-recipes (specifically the sometimes used activation and deactivation scripts).

If one writes the activation or deactivation script using this project, it is trivial to generate the same activation flow for many different shells:

- bash
- powershell
- cmd.bat
- zsh
- fish
- xonsh

This grew out of a frustration on how hard it is to write bash / cmd.bat scripts that work cross-platform and for all shells that people use (esp. powershell).

Examples:

```py
import sh

conda_prefix = sh.env("CONDA_PREFIX")
print(sh.if_(conda_prefix == "test").then_(
	sh.export("TEST_VARIABLE", sh.path_join(sh.env("CONDA_PREFIX"), "test/for/something"))
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