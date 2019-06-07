# Official Ubuntu 18.04
FROM ubuntu:18.04

### LANGUAGE SUPPORT BELOW
### Currently we support C, C++, Python3.6, Java, Go and Haskell

# Install basic dependencies
# Installing build-essential installs gcc-7 and g++-7 for C / C++ and
# Installing software-properties-common installs python3.6 for Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    make \
    curl \
    wget \
    ca-certificates \
    software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Install golang for Go
RUN apt-get update && apt-get install -y --no-install-recommends \
    golang && \
    rm -rf /var/lib/apt/lists/*

# Set the PATH variables after golang install
ENV GOPATH=${HOME}/go
ENV PATH=${PATH}:${GOPATH}/bin

# Install ghc for Haskell
RUN add-apt-repository -y ppa:hvr/ghc && \
    apt-get update && apt-get install -y --no-install-recommends \
    ghc-8.6.5 && \
    rm -rf /var/lib/apt/lists/*

# Set the PATH variables after ghc install
ENV PATH=${PATH}:/opt/ghc/bin

### TIMER_TOOL SUPPORT BELOW

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
ENV SUB_ID=-1

# Set working directory
WORKDIR /app

# Run the meta script
CMD python3.6 compile_and_test.py --submission_config tmp/sub_run_${SUB_ID}.txt
