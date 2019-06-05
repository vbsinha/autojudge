#!/bin/sh

# All required error codes
PASS=0
FAIL=1
NA=5

# Enter the testing script here.
# If the output "passes" the requirements, then
# return $PASS, otherwise return $FAIL
# Any technical glitch returns $NA
validate_submission_output() {
  diff -b -Z $1 $2 > /dev/null

  case "$?" in
    "0")
        return $PASS
        ;;
    "1")
        return $FAIL
        ;;
    *)
        return $NA
        ;;
  esac
}
