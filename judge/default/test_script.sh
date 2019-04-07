#!/bin/sh

# All Error Codes
PASS=0
FAIL=1
TLE=2
OOM=3
CE=4
RE=5
NA=6

# Run submission function
# If the executable runs fine, then the output validation is done
# Otherwise, an appropriate error code is returned
run_submission() {
  SID=$1
  TID=$2
  TLIMIT=$3

  timeout ${TLIMIT} python submission_${SID}.py < inputfile_${TID}.txt > sub_output_${SID}_${TID}.txt

  case "$?" in
    "0")
        validate_submission_output outputfile_${TID}.txt sub_output_${SID}_${TID}.txt
        return $?
        ;;
    "1")
        return $RE
        ;;
    "124")
        return $TLE
        ;;
    *)
        return $NA
        ;;
  esac
}

clean_generated_output() {
  rm sub_output_${1}_${2}.txt
}


# This requires poster input.
# The diff command below can be replaced with a function that takes in
# two arguments and returns 0 when the files match, 1 when they don't
# and > 1 when there is an issue
validate_submission_output() {

  # Enter the testing script here.
  # A default choice could be diff
  diff $1 $2 > /dev/null


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

# Convert error code to character string
error_code_to_string() {
  ERRCODE=$1
  TID=$2

  case "$ERRCODE" in
    "$PASS")
        STRCODE="P"
        ;;
    "$FAIL")
        STRCODE="F"
        ;;
    "$TLE")
        STRCODE="TE"
        ;;
    "$OOM")
        STRCODE="ME"
        ;;
    "$CE")
        STRCODE="CE"
        ;;
    "$RE")
        STRCODE="RE"
        ;;
    "$NA")
        STRCODE="NA"
        ;;
    *)
        STRCODE="NA"
        ;;
  esac

  echo "$TESTCASE_ID: $STRCODE"
}

# Submission ID is passed to the script
SUB_ID=$1

# Number of inputfiles = Number of outputfiles = Number of testcases
N_TEST=$(ls | grep -c "inputfile_")

TIMELIMIT=1

# Iterate arbitrarily over testcases
for INPFILE in $(ls | grep "inputfile_");
  do
    # Get the TESTCASE_ID from the basename of the input file
    # Replace "inputfile_" with "" to get the ID alone
    TESTCASE_ID=$(basename $INPFILE ".txt" | sed 's/^inputfile_//g')

    # Run the submission using run_submission
    run_submission ${SUB_ID} ${TESTCASE_ID} ${TIMELIMIT}

    # The return value of the function will determine what goes into the submission status
    error_code_to_string $? ${TESTCASE_ID} >> submission_${SUB_ID}_status.txt

    # Remove the generated output files
    clean_generated_output ${SUB_ID} ${TESTCASE_ID}
  done
