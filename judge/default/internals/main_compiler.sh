#!/bin/sh

####################################################
# Using this script
#   ./compilation_script.sh $PROB_CODE $SUB_FILE
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

case "$SUBPATH" in
    *.py)
        EXECPATH=${SUBPATH%.*}
        EXTENSION=".py"
        compile_py $SUBPATH $EXECPATH
        ;;
    *.cpp)
        EXECPATH=${SUBPATH%.*}
        EXTENSION=".cpp"
        compile_cpp $SUBPATH $EXECPATH
        ;;
    *)
        EXECPATH=${SUBPATH%.*}
        EXTENSION=".none"
        ;;
esac

# Return the return value of the 
return $?
