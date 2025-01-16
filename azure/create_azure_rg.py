from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError
from threading import Timer

class AzureConfig:
    def __init__(self, subscription_id, resource_group, storage_account_name, location: str):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.storage_account_name = storage_account_name
        self.credential = DefaultAzureCredential()
        self.location: str = location


class ResourceGroupService:
    def __init__(self, config: AzureConfig):
        self.config: AzureConfig = config
        self.client = ResourceManagementClient(config.credential, config.subscription_id)

    def ensure_resource_group(self):
        try:
            self.client.resource_groups.get(self.config.resource_group)
            print(f"Resource group '{self.config.resource_group}' already exists.")
        except Exception as e:
            if "ResourceGroupNotFound" in str(e):
                print(f"Resource group '{self.config.resource_group}' does not exist. Creating it...")
                self.client.resource_groups.create_or_update(
                    self.config.resource_group,
                    {"location": self.config.location}
                )
                print(f"Resource group '{self.config.resource_group}' created successfully.")
            else:
                print(f"An error occurred: {e}")


class StorageAccountService:
    def __init__(self, config: AzureConfig):
        self.config: AzureConfig = config
        self.client = StorageManagementClient(config.credential, config.subscription_id)

    def create_storage_account(self, sku_name="Standard_LRS", enable_hns=True):
        print(f"Creating storage account: {self.config.storage_account_name}")
        async_create = self.client.storage_accounts.begin_create(
            self.config.resource_group,
            self.config.storage_account_name,
            {
                "location": self.config.location,
                "sku": {"name": sku_name},
                "kind": "StorageV2",
                "properties": {
                    "isHnsEnabled": enable_hns  # Enable Hierarchical Namespace

                },
            },
        )
        return async_create.result()


class BlobContainerService:
    def __init__(self, config: AzureConfig):
        self.config = config
        self.blob_client = BlobServiceClient(
            f"https://{config.storage_account_name}.blob.core.windows.net",
            credential=config.credential,
        )

    def create_container(self, container_name: str):
        print(f"Creating container: {container_name}")
        container_client = self.blob_client.get_container_client(container_name)

        try:
            container_client.create_container()
            print(f"Container '{container_name}' created successfully.")
        except HttpResponseError as e:
            if e.status_code == 409:  # HTTP 409 Conflict means the container already exists
                print(f"Container '{container_name}' already exists.")
            else:
                print(f"Failed to create container '{container_name}': {e.message}")

        return container_client


class BlobContainerUploaderService:
    def __init__(self, config: AzureConfig):
        self.config: AzureConfig = config
        self.blob_client = BlobServiceClient(
            f"https://{config.storage_account_name}.blob.core.windows.net",
            credential=config.credential,
        )

    def upload_file(self, container_name, file_path, blob_name):
        print(f"Uploading file '{file_path}' to container '{container_name}' as blob '{blob_name}'")
        container_client = self.blob_client.get_container_client(container_name)

        try:
            with open(file_path, "rb") as data:
                container_client.upload_blob(blob_name, data, overwrite=True)  # overwrites if blob exists
            print(f"File '{file_path}' uploaded successfully as '{blob_name}'.")
        except HttpResponseError as e:
            print(f"Failed to upload file '{file_path}': {e.message}")


class CsvFileUploader:
    def __init__(self, blob_service: BlobContainerUploaderService, container_name, file_path, blob_name, interval_minutes):
        self.blob_service = blob_service
        self.container_name = container_name
        self.file_path = file_path
        self.blob_name = blob_name
        self.interval_minutes = interval_minutes

    def upload_file_periodically(self):
        """Uploads the file to the storage container every x minutes."""
        self.blob_service.upload_file(self.container_name, self.file_path, self.blob_name)

        # Set the Timer to upload the file again after the specified interval
        Timer(self.interval_minutes * 60, self.upload_file_periodically).start()