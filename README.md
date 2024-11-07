# GraphRAG Kit

## Requirements

- Ubuntu 24
    - [Azure Virtual Machines](https://portal.azure.com/#browse/Microsoft.Compute%2FVirtualMachines)
- Docker & Docker Compose
    - [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

## Set Env

Copy and set your environment variables:

```bash
cp .env.example .env
```

Configure the environment variables in the .env file.

## Start App

```bash
bash start.sh
```

When the applications are started, you will have access to 3 URLs:

- Management App: http://localhost:9000/
- Test App: http://localhost:9001/
- API Documentation: http://localhost:9002/docs

## Make App as your Service

If you want to make the app as your service, run:

```bash
bash service.sh
```

## Deploy

Before deploying the applications, run:

```bash
az login
```

### Deploy Test App

```bash
bash deploy_test.sh
```

### Deploy API

```bash
bash deploy_api.sh
```
