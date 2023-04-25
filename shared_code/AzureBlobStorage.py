import os
from azure.cosmosdb.table.tableservice import TableService

table_name = ''
account_name = os.getenv("TABLE_STORAGE_NAME") # 'storageaccount***'
account_key = os.getenv("TABLE_STORAGE_KEY") # '********...***=='
table_service = None

def get_values_from(key):
    global table_service
    if not table_service:
        table_service = TableService(account_name=account_name, account_key=account_key)

    entities = table_service.query_entities(table_name, filter=f"PartitionKey eq '{key}'")
    values = [ x['RowKey'] for x in entities]
    return values

if __name__ == "__main__":
    table_name = 'TwitterEgoSearch'
    account_name = os.getenv("TABLE_STORAGE_NAME")
    account_key = os.getenv("TABLE_STORAGE_KEY")

    values = get_values_from('Keyword')
    for val in values:
        print(f'- {val}')
