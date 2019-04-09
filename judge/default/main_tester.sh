#!/bin/bash

########################################################
# Using this script
#    ./test_script.sh $PROB_CODE $SUB_ID [$TESTCASE_ID]+
# where
# - $PROB_CODE is the problem code
# - $SUB_ID is the submission ID
# - $TESTCASE_ID is the testcase ID (pass atleast 1)
########################################################

# All Error Codes pertaining to Testing
PASS=0
FAIL=1
TLE=2
OOM=3
RE=4
NA=5

# Assume a directory structure
# content/
# ├── problems
# ├── submissions
# ├── testcases
# └── tmp

PROB_FDR="problems"
SUB_FDR="submissions"
TEST_FDR="testcases"
TMP="tmp"

# Problem code
PROB_CODE=$1
shift

# Submission ID
SUB_ID=$1
shift

# Effectively importing the testing function : validate_submission_output()
. ${PROB_FDR}/${PROB_CODE}/test_script.sh

# Run submission function
# If the executable runs fine, then the output validation is done
# Otherwise, an appropriate error code is returned
run_submission() {
  SID=$1
  TID=$2
  TLIMIT=$3
  MLIMIT=$4

  # First two lines specify the flags required
  # -w /dev/null pipes output of the tool to /dev/null, --vsize-limit gives the virtual size limit
  # --cores 0 limits to only one core, --wall-clock-limit handles the time limit
  # --var provides a file with specific flags which are used for checking
  # The last line runs the process
  timer_tool -w /dev/null --vsize-limit $MLIMIT --cores 0 --wall-clock-limit $TLIMIT \
             --var ${TMP}/submission_status_${SID}_${TID}.txt \
             ${SUB_FDR}/submission_${SID} < ${TEST_FDR}/inputfile_${TID}.txt > ${TMP}/sub_output_${SID}_${TID}.txt

  # Make all the flags as env vars for checking and remove this file
  . ${TMP}/submission_status_${SID}_${TID}.txt
  rm ${TMP}/submission_status_${SID}_${TID}.txt

  # This is what we do:
  # - Run it with the timer_tool, and then check if the limits are maintained
  #     - If no, return the appropriate errors
  #     - If yes, re-run again to get the final submission output
  #       This is then checked normally using a diff
  if [ "$TIMEOUT" = true ] ; then
    return $TLE
  elif [ "$MEMOUT" = true ] ; then
    return $OOM
  else
    clean_generated_output ${SID} ${TID}  # Delete the generated file to prevent any mismatch
    ${SUB_FDR}/submission_${SID} < ${TEST_FDR}/inputfile_${TID}.txt > ${TMP}/sub_output_${SID}_${TID}.txt

    case "$?" in
      "0")
          validate_submission_output ${TEST_FDR}/outputfile_${TID}.txt ${TMP}/sub_output_${SID}_${TID}.txt
          return $?
          ;;
      "1")
          return $RE
          ;;
      *)
          return $NA
          ;;
    esac
  fi
}

clean_generated_output() {
  rm ${TMP}/sub_output_${1}_${2}.txt
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

# To be set from the env, in seconds
TIMELIMIT=1

# To be set from the env, in MB
MEMLIMIT=100

# Iterate over all testcase IDs passed as command line arguments
for TESTCASE_ID in "$@";
  do
    # Run the submission using run_submission
    run_submission ${SUB_ID} ${TESTCASE_ID} ${TIMELIMIT} ${MEMLIMIT}

    # The return value of the function will determine what goes into the submission status
    error_code_to_string $? ${TESTCASE_ID} >> submission_${SUB_ID}_status.txt

    # Remove the generated output files
    clean_generated_output ${SUB_ID} ${TESTCASE_ID}
  done
