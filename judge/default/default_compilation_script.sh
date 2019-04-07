#!/bin/sh

####################################################
# Using this script
#   ./compilation_script.sh submission_file
# where
# - submission file is the file that is submitted
####################################################


# All Error Codes
SUCCESS=0
FAILURE=1

SUB_FDR="submissions"

# This is the function to compile CPP files using g++
compile_cpp() {
  SUBFILE=$1
  EXFILE=$2
  if g++ $SUBFILE -o $EXFILE 2> /dev/null ; then
    return $SUCCESS
  else
    return $FAILURE
  fi
}

# This is the function to "compile" Python files
compile_py() {
  SUBFILE=$1
  EXFILE=$2
  echo "#!/usr/local/bin/python" > $EXFILE
  cat $SUBFILE >> $EXFILE
  return $SUCCESS
}

# Now perform string-matching to get the extension
# and the corresponding "executable"
SUBNAME=${SUB_FDR}/$1

case "$SUBNAME" in
    *.py)
        EXECNAME=${SUBNAME%.*}
        EXTENSION=".py"
        compile_py $SUBNAME $EXECNAME
        ;;
    *.cpp)
        EXECNAME=${SUBNAME%.*}
        EXTENSION=".cpp"
        compile_cpp $SUBNAME $EXECNAME
        ;;
    *)
        EXEC_NAME=${SUBNAME%.*}
        EXTENSION=".none"
        ;;
esac

# Return the return value of the 
return $?
