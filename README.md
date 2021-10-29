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

If you save:

```py
if_(conda_prefix == "test").then_(
	cmds.export("TEST_VARIABLE", path.join(cmds.env("CONDA_PREFIX"), "test/for/something"))
)
```

in a file called `project_activate.msh`, and you convert it with:

~~~
multisheller project_activate.msh
~~~

This will generate many shell files, such as `project_activate.bash`, `project_activate.bat`, one for each supported shell.

For example, if you open the `project_activate.bash` you will find:

```sh
# Taken from http://www.linuxfromscratch.org/blfs/view/svn/postlfs/profile.html
# Functions to help us manage paths.  Second argument is the name of the
# path variable to be modified (default: PATH)
pathremove () {
        local IFS=':'
        local NEWPATH
        local DIR
        local PATHVARIABLE=${2:-PATH}
        for DIR in ${!PATHVARIABLE} ; do
                if [ "$DIR" != "$1" ] ; then
                  NEWPATH=${NEWPATH:+$NEWPATH:}$DIR
                fi
        done
        export $PATHVARIABLE="$NEWPATH"
}

pathprepend () {
        # pathremove $1 $2
        local PATHVARIABLE=${2:-PATH}
        export $PATHVARIABLE="$1${!PATHVARIABLE:+:${!PATHVARIABLE}}"
}

pathappend () {
        # pathremove $1 $2
        local PATHVARIABLE=${2:-PATH}
        export $PATHVARIABLE="${!PATHVARIABLE:+${!PATHVARIABLE}:}$1"
}
if [[ $CONDA_PREFIX -eq test ]];
then
    export TEST_VARIABLE=$CONDA_PREFIX/test/for/something
fi;
```

while in `project_activate.ps1` :
~~~
if (($Env:CONDA_PREFIX) -eq (test)) {
    $Env:TEST_VARIABLE=$(Join-Path -Path $Env:CONDA_PREFIX -ChildPath test/for/something)
}
~~~

If you want to customize the name of the converted scripts, you can use the `--output` option of `multisheller` :
~~~
multisheller project_activate.msh --output setup
~~~

This will create the `setup.bash`, `setup.zsh`, `setup.bat`, ... files.
