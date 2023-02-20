FROM alpine:latest as tailscale
WORKDIR /app
ARG TAILSCALE_VERSION=1.36.0
RUN wget https://pkgs.tailscale.com/stable/tailscale_${TAILSCALE_VERSION}_amd64.tgz && \
  tar xzf tailscale_${TAILSCALE_VERSION}_amd64.tgz --strip-components=1

FROM python:3

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    ca-certificates \
    iptables \
    software-properties-common \
  && add-apt-repository -u ppa:gijzelaar/snap7 \
  && apt-get install -y -t bullseye \
    libsnap7-1 \
    libsnap7-dev \
  && rm -rf /var/lib/apt/lists/*
COPY --from=tailscale /app/tailscaled /usr/src/app/tailscaled
COPY --from=tailscale /app/tailscale /usr/src/app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [".fly/start.sh"]
