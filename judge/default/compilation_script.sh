# Enter the compilation script here.
# For every language, write a function named "compile_<extension>()"
# SUBPATH is the path of the file that has been submitted
# EXPATH is the path for the executable generated

# All required error codes
SUCCESS=0
FAILURE=1

# This is the function to compile .c files using gcc
compile_c() {
  SUBPATH=$1
  EXPATH=$2
  if gcc $SUBPATH -lm -o $EXPATH ; then
    return $SUCCESS
  else
    return $FAILURE
  fi
}

# This is the function to compile .cpp files using g++
compile_cpp() {
  SUBPATH=$1
  EXPATH=$2
  if g++ $SUBPATH -lm -o $EXPATH ; then
    return $SUCCESS
  else
    return $FAILURE
  fi
}

# This is the function to "compile" Python files
compile_py() {
  SUBPATH=$1
  EXPATH=$2
  echo "#!/usr/bin/python3.6" > $EXPATH
  cat $SUBPATH >> $EXPATH
  return $SUCCESS
}

# This is the function to compile .go files using go build
compile_go() {
  SUBPATH=$1
  EXPATH=$2
  if go build $SUBPATH -o $EXPATH ; then
    return $SUCCESS
  else
    return $FAILURE
  fi
}

# This is the function to compile .hs files using ghc
compile_hs() {
  SUBPATH=$1
  EXPATH=$2
  if ghc $SUBPATH -o $EXPATH ; then
    rm -f $EXPATH.hi $EXPATH.o
    return $SUCCESS
  else
    return $FAILURE
  fi
}
