# Setting Up a Docker Registry

## Quick Start (Local Machine)

For testing/development on your laptop:

```bash
# Start a local registry on port 5000
docker run -d \
  -p 5000:5000 \
  --name registry \
  --restart always \
  registry:latest
```

Then use:
```bash
export DOCKER_REGISTRY="localhost:5000"
./build_and_push.sh --both
```

## Production Setup (On Your Server)

### Option 1: Simple Registry (No Persistence)

```bash
ssh your-server
docker run -d \
  -p 5000:5000 \
  --name registry \
  --restart always \
  registry:latest
```

Then from your laptop:
```bash
export DOCKER_REGISTRY="your-server.com:5000"
./build_and_push.sh --both
```

### Option 2: Registry with Storage Persistence

Create a directory for registry data:
```bash
ssh your-server
mkdir -p /var/lib/registry

docker run -d \
  -p 5000:5000 \
  --name registry \
  -v /var/lib/registry:/var/lib/registry \
  --restart always \
  registry:latest
```

### Option 3: Registry with SSL/TLS (Recommended for Production)

First, generate self-signed certificates:
```bash
ssh your-server

# Create cert directory
mkdir -p /var/lib/registry/certs

# Generate certificate (valid for 365 days)
openssl req -x509 -newkey rsa:4096 -keyout /var/lib/registry/certs/key.pem \
  -out /var/lib/registry/certs/cert.pem -days 365 -nodes \
  -subj "/CN=your-server.com"

# Fix permissions
chmod 600 /var/lib/registry/certs/key.pem
chmod 644 /var/lib/registry/certs/cert.pem
```

Then run the registry with SSL:
```bash
docker run -d \
  -p 5000:5000 \
  --name registry \
  -v /var/lib/registry:/var/lib/registry \
  -v /var/lib/registry/certs:/certs \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/cert.pem \
  -e REGISTRY_HTTP_TLS_KEY=/certs/key.pem \
  --restart always \
  registry:latest
```

### Option 4: Registry with Docker Compose

Create `docker-compose-registry.yml` on your server:

```yaml
version: '3'

services:
  registry:
    image: registry:latest
    ports:
      - "5000:5000"
    environment:
      REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY: /data
    volumes:
      - registry-data:/data
    restart: always

volumes:
  registry-data:
```

Then:
```bash
docker compose -f docker-compose-registry.yml up -d
```

## Using the Registry

### From your laptop/dev machine:

```bash
# Set the registry URL
export DOCKER_REGISTRY="your-server.com:5000"

# Build and push images
./build_and_push.sh --both

# Later, run images from the registry
./start_website.sh --dev migrate
```

### Verify images were pushed:

```bash
# List images in registry
curl http://your-server.com:5000/v2/_catalog

# List tags for a specific image
curl http://your-server.com:5000/v2/beobgrp_site/tags/list
```

## Troubleshooting

### If you get "Error response from daemon: Get "https://...": x509: certificate signed by unknown authority"

You need to trust the self-signed certificate. On your laptop:

```bash
# Create the certs directory
mkdir -p ~/.docker/certs.d/your-server.com:5000

# Copy the certificate from your server
scp your-server:/var/lib/registry/certs/cert.pem ~/.docker/certs.d/your-server.com:5000/ca.crt

# On macOS, add to Docker Desktop's trusted certs
# Or on Linux, Docker should automatically trust it
```

### If registry is not accessible from your laptop

Check firewall rules:
```bash
# From laptop, test connection
telnet your-server.com 5000
# or
nc -zv your-server.com 5000
```

Make sure port 5000 is open in your server's firewall:
```bash
ssh your-server
sudo ufw allow 5000/tcp  # if using UFW
# or
sudo firewall-cmd --permanent --add-port=5000/tcp  # if using firewalld
```

## Cleanup

If you need to stop/remove the registry:

```bash
docker stop registry
docker rm registry
```

If using volumes:
```bash
docker compose -f docker-compose-registry.yml down -v
```
