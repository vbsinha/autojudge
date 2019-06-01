#!/bin/sh

####################################################
# Using this script
#   ./main_compiler.sh $PROB_CODE $SUB_FILE
# where
# - $PROB_CODE is the problem code of the problem
# - $SUB_FILE is the file that is submitted
####################################################


# All Error Codes pertaining to Compilation
SUCCESS=0
FAILURE=1

SUB_FDR="submissions"
PROB_FDR="problems"

PROB_CODE=$1
SUB_FILE=$2

. ${PROB_FDR}/${PROB_CODE}/compilation_script.sh

# Now perform string-matching to get the extension
# and the corresponding "executable"
SUBPATH=${SUB_FDR}/${SUB_FILE}
EXECPATH=${SUBPATH%.*}

case "$SUBPATH" in
    *.c)
        EXTENSION=".c"
        compile_c $SUBPATH $EXECPATH
        chmod 555 $EXECPATH
        ;;
    *.cpp)
        EXTENSION=".cpp"
        compile_cpp $SUBPATH $EXECPATH
        chmod 555 $EXECPATH
        ;;
    *.py)
        EXTENSION=".py"
        compile_py $SUBPATH $EXECPATH
        chmod 555 $EXECPATH
        ;;
    *.go)
        EXTENSION=".go"
        compile_go $SUBPATH $EXECPATH
        chmod 555 $EXECPATH
        ;;
    *.hs)
        EXTENSION=".hs"
        compile_hs $SUBPATH $EXECPATH
        chmod 555 $EXECPATH
        ;;
    *)
        EXTENSION=".none"
        ;;
esac

# Return the return value of the 
return $?
