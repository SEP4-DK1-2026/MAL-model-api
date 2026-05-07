FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    make \
    git \
    curl \
    lsb-release \
    libicu72 \
    && rm -rf /var/lib/apt/lists/*

# Install azure cli
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install azure function tools
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
RUN mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
RUN sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/debian/$(lsb_release -rs 2>/dev/null | cut -d'.' -f 1)/prod $(lsb_release -cs 2>/dev/null) main" > /etc/apt/sources.list.d/dotnetdev.list'
RUN apt-get update && apt-get install -y azure-functions-core-tools-4

# Create the user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

# Set working directory
WORKDIR /workspaces

# Set line endings
RUN git config --global core.autocrlf true

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt