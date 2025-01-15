from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient

# Configuration class (SRP)
class AzureConfig:
    def __init__(self, subscription_id, resource_group, storage_account_name):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.storage_account_name = storage_account_name
        self.credential = DefaultAzureCredential()

# Service class for managing storage accounts (SRP)
class StorageAccountService:
    def __init__(self, config: AzureConfig):
        self.config = config
        self.client = StorageManagementClient(config.credential, config.subscription_id)

    def create_storage_account(self, location, sku_name="Standard_LRS"):
        print(f"Creating storage account: {self.config.storage_account_name}")
        async_create = self.client.storage_accounts.begin_create(
            self.config.resource_group,
            self.config.storage_account_name,
            {
                "location": location,
                "sku": {"name": sku_name},
                "kind": "StorageV2",
                "properties": {},
            },
        )
        return async_create.result()

# Service class for managing blob containers (SRP)
class BlobContainerService:
    def __init__(self, config: AzureConfig):
        self.config = config
        self.blob_client = BlobServiceClient(
            f"https://{config.storage_account_name}.blob.core.windows.net",
            credential=config.credential,
        )

    def create_container(self, container_name):
        print(f"Creating container: {container_name}")
        container_client = self.blob_client.get_container_client(container_name)
        container_client.create_container()
        return container_client

# Main function applying DIP
def main():
    config = AzureConfig(
        subscription_id="your_subscription_id",
        resource_group="your_resource_group",
        storage_account_name="your_storage_account_name",
    )

    # Storage Account creation
    storage_service = StorageAccountService(config)
    storage_service.create_storage_account(location="eastus")

    # Container creation
    blob_service = BlobContainerService(config)
    blob_service.create_container(container_name="example-container")

if __name__ == "__main__":
    main()
