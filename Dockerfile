ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:3.15
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    git

# Set up working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY spotty ./spotty/

# Create and use a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies in the virtual environment
RUN pip3 install .

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
