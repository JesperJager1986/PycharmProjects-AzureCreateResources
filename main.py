from azure.create_azure_rg import AzureConfig, ResourceGroupService, StorageAccountService, BlobContainerService, \
    CsvFileUploader, BlobContainerUploaderService, AzureRoleAssigner


def main():
    config = AzureConfig(
        subscription_id="c33d8af8-0575-48a3-8044-61ece2e09fcb",
        resource_group="rg_for_databricks",
        storage_account_name="datafordatabricks",
        location = "westeurope"
    )
    container_name = "example-container"
    resource_service = ResourceGroupService(config)
    resource_service.ensure_resource_group()

    storage_service = StorageAccountService(config)
    storage_service.create_storage_account()

    blob_service = BlobContainerService(config)

    blob_service.create_container(container_name=container_name)

    service_principal_object_id = "19d8869f-a8e7-4c08-a775-b5529927a181" #from Enterprise application in Azure
    role_assigner = AzureRoleAssigner(config)
    # Assign the Contributor role to the Service Principal
    result = role_assigner.assign_contributor_to_storage(
        principal_id=service_principal_object_id
    )

    # Output the result
    print(f"Role Assignment Result: {result}")


    interval_minutes = 1  # Set the interval in minutes

    # Azure configuration
    blob_service2 = BlobContainerUploaderService(config)

    uploader = CsvFileUploader(blob_service2, container_name, interval_minutes)
    uploader.upload_file_periodically()  # Start the periodic upload

if __name__ == "__main__":
    main()
