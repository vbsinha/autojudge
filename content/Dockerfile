# Official Python 3
FROM python:3

# Install dependencies for timer_tool (a.k.a. runsolver)
RUN apt-get update && apt-get install -y libnuma-dev && \
    rm -rf /var/lib/apt/lists/*

# Install timer_tool (a.k.a. runsolver)
RUN curl https://www.cril.univ-artois.fr/~roussel/runsolver/runsolver-3.4.0.tar.bz2 -o ~/runsolver.tar.bz2 && \
    tar -xjf ~/runsolver.tar.bz2 -C ~/ && \
    rm ~/runsolver.tar.bz2 && \
    sed -i 's/include/-include/g' ~/runsolver/src/Makefile && \
    make -C ~/runsolver/src runsolver && \
    mv ~/runsolver/src/runsolver ~/timer_tool && \
    rm -r ~/runsolver/ && \
    mv ~/timer_tool /bin/timer_tool

# Submission ID, to be set at runtime in `docker run` calls
ENV SUB_ID=0

# Set working directory
WORKDIR /app

# Run the meta script
CMD python compile_and_test.py --submission_config tmp/sub_run_${SUB_ID}.txt
