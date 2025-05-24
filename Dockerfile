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

# Install dependencies using standard pip
RUN pip3 install .

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
