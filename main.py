from azure.create_azure_rg import AzureConfig, ResourceGroupService, StorageAccountService, BlobContainerService, \
    CsvFileUploader, BlobContainerUploaderService

from csvHandler.cvs_handler import CsvFileGenerator

# Main function applying DIP
def main():
    config = AzureConfig(
        subscription_id="c33d8af8-0575-48a3-8044-61ece2e09fcb",
        resource_group="testRGJJ",
        storage_account_name="testsajj",
        location = "eastus"
    )
    container_name = "example-container"
    resource_service = ResourceGroupService(config)
    resource_service.ensure_resource_group()

    storage_service = StorageAccountService(config)
    storage_service.create_storage_account()

    blob_service = BlobContainerService(config)
    blob_service.create_container(container_name=container_name)

    file_path = "/Users/jesperthoftillemannjaeger/PycharmProjects/PycharmProjects-AzureCreateResources/dummyFolder"  # Path to the CSV file to upload
    blob_name = "uploaded-csv-file.csv"  # The name you want to give to the blob in storage
    interval_minutes = 1  # Set the interval in minutes

    # Azure configuration
    blob_service2 = BlobContainerUploaderService(config)
    cvs_file_generator = CsvFileGenerator(file_path)
    path = cvs_file_generator.generate_csv()
    # Create and start the CSV file uploader
    uploader = CsvFileUploader(blob_service2, container_name, path, container_name, interval_minutes)
    uploader.upload_file_periodically()  # Start the periodic upload

if __name__ == "__main__":
    main()
