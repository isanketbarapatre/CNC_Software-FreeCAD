FROM ubuntu:24.04 AS builder
 
ENV DEBIAN_FRONTEND noninteractive
 
ENV PYTHON_VERSION 3.11.4
ENV PYTHON_MINOR_VERSION 3.11
ENV PYTHON_BIN_VERSION python3.11
 
ENV FREECAD_VERSION releases/FreeCAD-0-21
ENV FREECAD_REPO https://github.com/FreeCAD/FreeCAD.git
 
RUN apt update && \
    apt install -y \
    libyaml-cpp-dev \
    git \
    python$PYTHON_MINOR_VERSION \
    python$PYTHON_MINOR_VERSION-dev \
    python$PYTHON_MINOR_VERSION-distutils \
    python3-pip \
    wget \
    build-essential \
    cmake \
    libtool \
    lsb-release \
    libboost-dev \
    libboost-date-time-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-iostreams-dev \
    libboost-program-options-dev \
    libboost-python-dev \
    libboost-regex-dev \
    libboost-serialization-dev \
    libboost-thread-dev \
    libcoin-dev \
    libeigen3-dev \
    libgts-bin \
    libgts-dev \
    libkdtree++-dev \
    libmedc-dev \
    libopencv-dev \
    libproj-dev \
    libx11-dev \        
    libvtk9-dev \
    libxerces-c-dev \
    libzipios++-dev \
    libocct-data-exchange-dev \
    libocct-draw-dev \
    libocct-foundation-dev \
    libocct-modeling-algorithms-dev \
    libocct-modeling-data-dev \
    libocct-ocaf-dev \
    libocct-visualization-dev \
    occt-draw \
    netgen-headers \
    netgen \
    libmetis-dev \
    gmsh \
    qtbase5-dev \
    libqt5xmlpatterns5-dev \
    python3-venv \  
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
 
ENV PYTHONPATH "/usr/local/lib:$PYTHONPATH"
 
# Clone FreeCAD repository
# ARG GITHUB_TOKEN
# ENV GITHUB_TOKEN=$GITHUB_TOKEN
RUN git clone --branch "$FREECAD_VERSION" "https://github.com/FreeCAD/FreeCAD.git" /FreeCAD && \
    mkdir /freecad-build \
    && cd /freecad-build \
    && cmake \
        -DBUILD_GUI=OFF \
        -DBUILD_QT5=OFF \
        -DPYTHON_EXECUTABLE=/usr/bin/python${PYTHON_VERSION} \
        -DPYTHON_INCLUDE_DIR=/usr/include/python${PYTHON_VERSION} \
        -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython${PYTHON_VERSION}.so \
        -DCMAKE_BUILD_TYPE=Release \
        # -DBUILD_FEM_NETGEN=ON \
        -DENABLE_DEVELOPER_TESTS=OFF \
        /FreeCAD \
    && make -j$(nproc --ignore=2) \
    && make install \
    && cd / \
    && rm -rf /FreeCAD /freecad-build
 
RUN ln -s /usr/lib/python3/dist-packages/PySide2 /usr/lib/python3/dist-packages/PySide
 
# Fixed import MeshPart module due to missing libnglib.so
# https://bugs.launchpad.net/ubuntu/+source/freecad/+bug/1866914
RUN echo "/usr/lib/x86_64-linux-gnu/netgen" >> /etc/ld.so.conf.d/x86_64-linux-gnu.conf
RUN ldconfig
 
ENV FREECAD_STARTUP_FILE /.startup.py
RUN echo "import FreeCAD" > ${FREECAD_STARTUP_FILE}
ENV PYTHONSTARTUP ${FREECAD_STARTUP_FILE}
# Make Python already know all FreeCAD modules / workbenches.
# Clean
RUN apt-get clean \
    && rm /var/lib/apt/lists/* \
    /usr/share/doc/* \
    /usr/share/locale/* \
    /usr/share/man/* \
    /usr/share/info/* -fR
 
# Activate the virtual environment
ENV PATH="/venv/bin:$PATH"
 
# Use python3 -m venv to create the virtual environment
RUN python3 -m venv /venv
 
RUN mkdir /app
 
# Copy your Python script to the container
COPY . /app
 
# Change permissions for the inputFiles directory
RUN chmod -R 755 /app/inputFiles
 
WORKDIR /app
 
# RUN pip install backports.zoneinfo
# RUN pip install --upgrade pip setuptools
RUN pip3 install -r requirements.txt
 
# Grant read-write permissions to /usr/local/Mod/
RUN chmod -R 777 /usr/local/Mod/
 
## Clone the FreeCAD_SheetMetal repository into /usr/local/Mod/
RUN git clone https://github.com/shaise/FreeCAD_SheetMetal /usr/local/Mod/SheetMetal
 
COPY SheetMetalUnfolderCopy.py /usr/local/Mod/SheetMetal/
 
RUN rm -rf SheetMetalUnfolderCopy.py
 
# Expose port 80 to allow communication with the container
EXPOSE 80
 
RUN chmod +x start.sh
CMD ["/app/start.sh"]p