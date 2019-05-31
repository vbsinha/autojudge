# Official Ubuntu 18.04
FROM ubuntu:18.04

# Install basic dependencies
# Installing build-essential installs gcc-7 and g++-7 for C / C++
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    make \
    curl \
    wget \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install python3.7 for Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.7 && \
    rm -rf /var/lib/apt/lists/*

# Install jdk and jre for Java
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre \
    default-jdk && \
    rm -rf /var/lib/apt/lists/*

# Install golang for Go
RUN apt-get update && apt-get install -y --no-install-recommends \
    golang && \
    echo 'export GOPATH=${HOME}/go' >> ~/.bashrc && \
    echo 'export PATH=${PATH}:${GOPATH}/bin' >> ~/.bashrc && \
    source ~/.bashrc && \
    rm -rf /var/lib/apt/lists/*

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
