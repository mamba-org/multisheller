from textwrap import indent

def str_quote(x):
    if type(x) is str:
        return f"\"{x}\""
    else:
        return x

def join_expr(expr_list, visitor):
    final_expr = []
    for el in expr_list:
        final_expr.append(visitor(el))
    return indent('\n'.join(final_expr), '    ')

sh_path_functions = """
getpathlistseparator () {
        local PATHVARIABLE=${1:-PATH}
        # If on Windows and PATHVARIABLE is not PATH, 
        # the list separator is ";" otherwise is ":"
        local PATHSEP=":"
        if [ ! -z $COMSPEC ]; then
          if [ "$PATHVARIABLE" != "PATH" ]; then
            local PATHSEP=";"
          fi
        fi
        echo "$PATHSEP"
}

# Taken from http://www.linuxfromscratch.org/blfs/view/svn/postlfs/profile.html
# Functions to help us manage paths.  Second argument is the name of the
# path variable to be modified (default: PATH)
pathremove () {
        local NEWPATH
        local DIR
        local PATHVARIABLE=${2:-PATH}
        local PATHSEP=$(getpathlistseparator $PATHVARIABLE)
        local IFS=$PATHSEP
        for DIR in ${!PATHVARIABLE} ; do
                if [ "$DIR" != "$1" ] ; then
                  NEWPATH=${NEWPATH:+$NEWPATH${PATHSEP}}$DIR
                fi
        done
        export $PATHVARIABLE="$NEWPATH"
}

pathprepend () {
        # pathremove $1 $2
        local PATHVARIABLE=${2:-PATH}
        local PATHSEP=$(getpathlistseparator $PATHVARIABLE)
        export $PATHVARIABLE="$1${!PATHVARIABLE:+${PATHSEP}${!PATHVARIABLE}}"
}

pathappend () {
        # pathremove $1 $2
        local PATHVARIABLE=${2:-PATH}
        local PATHSEP=$(getpathlistseparator $PATHVARIABLE)
        export $PATHVARIABLE="${!PATHVARIABLE:+${!PATHVARIABLE}${PATHSEP}}$1"
}
"""

