#!/usr/bin/env bash
set -euo pipefail
: "${AZURE_RESOURCE_GROUP:?export AZURE_RESOURCE_GROUP}"
: "${AZURE_LOCATION:?export AZURE_LOCATION}"
: "${COSMOS_ACCOUNT_NAME:?export COSMOS_ACCOUNT_NAME}"
az group create --name "$AZURE_RESOURCE_GROUP" --location "$AZURE_LOCATION" --output none
az deployment group create --resource-group "$AZURE_RESOURCE_GROUP" \
  --template-file infra/cosmos.bicep \
  --parameters cosmosName="$COSMOS_ACCOUNT_NAME" location="$AZURE_LOCATION" \
  --query properties.outputs -o json
