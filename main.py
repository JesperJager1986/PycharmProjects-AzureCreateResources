from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
from azure.mgmt.resource import ResourceManagementClient

# Configuration class (SRP)
class AzureConfig:
    def __init__(self, subscription_id, resource_group, storage_account_name):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.storage_account_name = storage_account_name
        self.credential = DefaultAzureCredential()


class ResourceGroupService:
    def __init__(self, config: AzureConfig):
        self.config = config
        self.client = ResourceManagementClient(config.credential, config.subscription_id)

    def ensure_resource_group(self, location):
        try:
            self.client.resource_groups.get(self.config.resource_group)
            print(f"Resource group '{self.config.resource_group}' already exists.")
        except Exception as e:
            if "ResourceGroupNotFound" in str(e):
                print(f"Resource group '{self.config.resource_group}' does not exist. Creating it...")
                self.client.resource_groups.create_or_update(
                    self.config.resource_group,
                    {"location": location}
                )
                print(f"Resource group '{self.config.resource_group}' created successfully.")
            else:
                print(f"An error occurred: {e}")


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
        subscription_id="c33d8af8-0575-48a3-8044-61ece2e09fcb",
        resource_group="testRGJJ",
        storage_account_name="testsajj",
    )

    resource_service = ResourceGroupService(config)
    resource_service.ensure_resource_group(location="eastus")

    # Storage Account creation
    storage_service = StorageAccountService(config)
    storage_service.create_storage_account(location="eastus")

    # Container creation
    blob_service = BlobContainerService(config)
    blob_service.create_container(container_name="example-container")

if __name__ == "__main__":
    main()
