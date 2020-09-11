#!/bin/sh

#############################################################################
# Using this script
#    ./main_tester.sh $PROB_CODE $SUB_ID $TIMELIMIT $MEMLIMIT [$TESTCASE_ID]+
# where
# - $PROB_CODE is the problem code
# - $SUB_ID is the submission ID
# - $TIMELIMIT is the time limit
# - $MEMLIMIT is the memory limit
# - $TESTCASE_ID is the testcase ID (pass atleast 1)
#############################################################################

# All Error Codes pertaining to Testing
PASS=0
FAIL=1
TLE=2
OOM=3
RE=4
NA=5

# Assume a directory structure
# content/
# ├── problems/
# ├── submissions/
# ├── testcase/
# ├── tmp/
# ├── compile_and_test.py
# ├── main_compiler.sh
# ├── main_tester.sh
# └── Dockerfile

PROB_FDR="problems"
SUB_FDR="submissions"
TEST_FDR="testcase"
TMP="tmp"

# Problem code
PROB_CODE=$1
shift

# Submission ID
SUB_ID=$1
shift

# Time Limit
TIMELIMIT=$1
shift

# Memory Limit
MEMLIMIT=$1
shift

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
             ${SUB_FDR}/submission_${SID} < ${TEST_FDR}/inputfile_${TID}.txt > ${TMP}/sub_output_${SID}_${TID}.txt 2> /dev/null

  # Make all the flags as env vars for checking and remove this file
  . ${TMP}/submission_status_${SID}_${TID}.txt
  rm ${TMP}/submission_status_${SID}_${TID}.txt

  # This is what we do:
  # - Run it with the timer_tool, and then check if the limits are maintained
  #     - If no, return the appropriate errors
  #     - If yes, re-run again to get the final submission output
  #       This is then checked normally using a diff
  #       The status is appended to the verdict_string along with the memory and time consumed
  VERDICT=""
  if [ "$TIMEOUT" = true ] ; then
    VERDICT=$(error_code_to_string $TLE ${TID})
    echo "Time limit exceeded" > ${TMP}/sub_run_${SID}_${TID}.log
  elif [ "$MEMOUT" = true ] ; then
    VERDICT=$(error_code_to_string $OOM ${TID})
    echo "Memory limit exceeded" > ${TMP}/sub_run_${SID}_${TID}.log
  else
    clean_generated_output ${SID} ${TID}  # Delete the generated file to prevent any mismatch
    ${SUB_FDR}/submission_${SID} < ${TEST_FDR}/inputfile_${TID}.txt > ${TMP}/sub_output_${SID}_${TID}.txt 2> ${TMP}/sub_run_${SID}_${TID}.log

    case "$?" in
      "0")
          ./${PROB_FDR}/${PROB_CODE}/test_script ${TEST_FDR}/outputfile_${TID}.txt ${TMP}/sub_output_${SID}_${TID}.txt > /dev/null
          VERDICT=$(error_code_to_string $? ${TID})
          ;;
      "1")
          VERDICT=$(error_code_to_string $RE ${TID})
          ;;
      *)
          VERDICT=$(error_code_to_string $NA ${TID})
          ;;
    esac
  fi
  VERDICT="${VERDICT} ${WCTIME} ${MAXVM} sub_run_${SID}_${TID}.log"
  echo ${VERDICT}
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

  echo "$TESTCASE_ID $STRCODE"
}

# Add executable permission
chmod +x ${PROB_FDR}/${PROB_CODE}/test_script

# Iterate over all testcase IDs passed as command line arguments
for TESTCASE_ID in "$@";
  do
    # Run the submission using run_submission
    run_submission ${SUB_ID} ${TESTCASE_ID} ${TIMELIMIT} ${MEMLIMIT} >> ${TMP}/sub_run_${SUB_ID}.txt

    # Remove the generated output files
    clean_generated_output ${SUB_ID} ${TESTCASE_ID}
  done
