import pandas as pd
import io
import ast
import os
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import Vector  
from azure.search.documents.indexes.models import (  
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    PrioritizedFields,  
    SemanticField,  
    SearchField,  
    SemanticSettings,  
    VectorSearch,  
    VectorSearchAlgorithmConfiguration,  
) 

service_endpoint = os.getenv("SEARCHENDPOINT")
index_name = os.getenv("INDEXNAME") 
key =os.getenv("SEARCHKEY")
credential = AzureKeyCredential(key)
connect_str = os.getenv("STORAGECONNECTIONSTRING")
embedding_container_name = os.getenv("EMPCONTAINERNAME")


def Create_Search_Index():
    index_client = SearchIndexClient(
    endpoint=service_endpoint, credential=credential)
    fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, searchable= True),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchableField(name="category", type=SearchFieldDataType.String,
                    filterable=True),
    SearchField(name="contentVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, dimensions=1536, vector_search_configuration="my-vector-config"),
                ]
    vector_search = VectorSearch(
        algorithm_configurations=[
            VectorSearchAlgorithmConfiguration(
                name="my-vector-config",
                kind="hnsw",
                hnsw_parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ]
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=PrioritizedFields(
            title_field=SemanticField(field_name="title"),
            prioritized_keywords_fields=[SemanticField(field_name="category")],
            prioritized_content_fields=[SemanticField(field_name="content")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_settings = SemanticSettings(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=index_name, fields=fields,
                        vector_search=vector_search, semantic_settings=semantic_settings)
    result = index_client.create_or_update_index(index)

def Load_Doc_to_Index(output_json_filename):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=embedding_container_name, blob=output_json_filename)
    data = blob_client.download_blob().readall()
    df = pd.read_json(io.BytesIO(data))
    json_obj =df.to_json(orient='records')
    input_data = ast.literal_eval(json_obj)
    
    search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
    result = search_client.upload_documents(input_data)