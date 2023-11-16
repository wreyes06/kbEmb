from azure.storage.blob import BlobServiceClient
import os
import io

#Read file from source container
def read_stream_from_blob(blob_path):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("STORAGECONNECTIONSTRING"))
    container_client=blob_service_client.get_container_client(os.getenv("CONTAINERNAME")) 
    data = container_client.download_blob(blob_path).readall()
    return io.BytesIO(data)

#Write file to target container
def write_to_blob(outputjson,output_json_filename):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("STORAGECONNECTIONSTRING"))
    container_client=blob_service_client.get_container_client(os.getenv("OUTPUTVECTORCONTAINERNAME"))
    container_client.upload_blob(output_json_filename, outputjson, overwrite=True)
    container_client.upload_blob(output_json_filename, outputjson, overwrite=True)
