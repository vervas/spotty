ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:3.15
FROM ${BUILD_FROM}

# Install uv for Python dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

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

# Install dependencies using uv
RUN uv pip install -e . --system

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
