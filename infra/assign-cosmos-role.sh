#!/usr/bin/env bash
# Asignar rol de DATOS, diferente del rol Azure Contributor (control plane).
set -euo pipefail
: "${AZURE_RESOURCE_GROUP:?}"
: "${COSMOS_ACCOUNT_NAME:?}"
PRINCIPAL_ID="${PRINCIPAL_ID:-$(az ad signed-in-user show --query id -o tsv)}"
COSMOS_ID=$(az cosmosdb show -g "$AZURE_RESOURCE_GROUP" -n "$COSMOS_ACCOUNT_NAME" --query id -o tsv)
# Rol BUILT-IN Cosmos DB Data Contributor: 00000000-0000-0000-0000-000000000002
az cosmosdb sql role assignment create \
  --account-name "$COSMOS_ACCOUNT_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --scope / --principal-id "$PRINCIPAL_ID" \
  --role-definition-id "$COSMOS_ID/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
echo "Asignación de rol de datos solicitada para $PRINCIPAL_ID"
