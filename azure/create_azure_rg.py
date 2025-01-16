from datetime import datetime
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError
from threading import Timer
import requests


from csvHandler.cvs_handler import CsvFileGenerator


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
    def __init__(self, blob_service: BlobContainerUploaderService,
                 container_name,
                 interval_minutes):
        self.blob_service = blob_service
        self.container_name = container_name
        self.interval_minutes = interval_minutes
        self.cvs_file_generator = CsvFileGenerator()

    def upload_file_periodically(self):
        """Uploads the file to the storage container every x minutes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"data_{timestamp}.csv"
        print(file_name)
        path = self.cvs_file_generator.generate_csv(file_name=file_name)
        self.blob_service.upload_file(self.container_name, path, file_name)

        # Set the Timer to upload the file again after the specified interval
        Timer(self.interval_minutes * 60, self.upload_file_periodically).start()


import uuid
from azure.identity import DefaultAzureCredential


class AzureRoleAssigner:
    def __init__(self, config):
        """
        Initialize the AzureRoleAssigner with an AzureConfig instance.
        """
        self.subscription_id = config.subscription_id
        self.resource_group = config.resource_group
        self.storage_account_name = config.storage_account_name
        self.location = config.location
        self.credentials = config.credential
        self.contributor_role_id = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"  # Contributor RoleDefinition ID

    def get_access_token(self):
        """
        Get an access token for Azure Resource Management.
        """
        return self.credentials.get_token("https://management.azure.com/.default").token

    def get_storage_account_resource_id(self):
        """
        Retrieve the resource ID of the storage account using Azure REST API.
        """
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Storage/storageAccounts/{self.storage_account_name}?api-version=2022-09-01"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()["id"]
        else:
            raise Exception(f"Failed to get storage account resource ID: {response.status_code} {response.text}")

    def assign_contributor_role(self, resource_id: str, principal_id: str) -> None:
        """
        Assign the Contributor role to the given Service Principal for the specified resource.
        """
        role_assignment_id = str(uuid.uuid4())  # Unique ID for the role assignment
        url = f"https://management.azure.com{resource_id}/providers/Microsoft.Authorization/roleAssignments/{role_assignment_id}?api-version=2020-04-01-preview"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        body = {
            "properties": {
                "roleDefinitionId": f"/subscriptions/{self.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{self.contributor_role_id}",
                "principalId": principal_id,  # Ensure this is the Service Principal ID
                "principalType": "ServicePrincipal"  # Explicitly specify the principal type
            }
        }

        try:
            # Make the PUT request to assign the role
            response = requests.put(url, headers=headers, json=body)

            # Check for successful response
            if response.status_code == 201:
                print("Role assignment successful!")
                #return response.json()

            # Handle 409 Conflict specifically
            elif response.status_code == 409:
                print("Role assignment already exists. Ignoring the conflict.")
                #return {"status": "conflict", "message": "Role assignment already exists."}

            # Raise an error for other status codes
            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            # Catch and log unexpected errors
            print(f"Failed to assign role due to an error: {e}")
            raise

    def assign_contributor_to_storage(self, principal_id):
        """
        High-level method to assign Contributor role for storage account.
        """
        print(f"Fetching resource ID for storage account '{self.storage_account_name}'...")
        storage_account_id = self.get_storage_account_resource_id()
        print(f"Assigning Contributor role to principal '{principal_id}'...")
        return self.assign_contributor_role(storage_account_id, principal_id)





