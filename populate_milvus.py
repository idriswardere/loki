from milvus import default_server
from pymilvus import connections, utility

default_server.cleanup()
default_server.start()

connections.connect(host='127.0.0.1', port=default_server.listen_port)
# TODO: get data into db from _details modules and make index (collection?) for each character

default_server.stop()