# Enter the compilation script here.
# For every language, write a function named "compile_<extension>()"

# All required error codes
SUCCESS=0
FAILURE=1

# This is the function to compile CPP files using g++
compile_cpp() {
  SUBPATH=$1
  EXPATH=$2
  if g++ $SUBPATH -o $EXPATH 2> /dev/null ; then
    return $SUCCESS
  else
    return $FAILURE
  fi
}

# This is the function to "compile" Python files
compile_py() {
  SUBPATH=$1
  EXPATH=$2
  echo "#!/usr/local/bin/python" > $EXPATH
  cat $SUBPATH >> $EXPATH
  return $SUCCESS
}
