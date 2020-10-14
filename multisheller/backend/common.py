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
"""

