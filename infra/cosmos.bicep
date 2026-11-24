@description('Nombre globalmente único de la cuenta Cosmos DB')
param cosmosName string
param location string = resourceGroup().location

resource account 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [{ locationName: location, failoverPriority: 0 }]
    capabilities: [{ name: 'EnableServerless' }]
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
}
resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: account
  name: 'enterprise-support'
  properties: { resource: { id: 'enterprise-support' } }
}
resource tickets 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: 'tickets'
  properties: {
    resource: {
      id: 'tickets'
      partitionKey: { paths: ['/id'], kind: 'Hash' }
    }
  }
}
output cosmosEndpoint string = account.properties.documentEndpoint
output cosmosId string = account.id
