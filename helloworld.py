import sqlalchemy
from sqlalchemy import create_engine

print("We are on sqlalchemy version:")
print(sqlalchemy.__version__)

engine = create_engine("sqlite+pysqlite:///:memory:")
print(dir(engine))
"""
Output methods for engine:
['__annotations__', '__class__', '__class_getitem__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__orig_bases__', '__parameters__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_compiled_cache', '_connection_cls', '_echo', '_execution_options', '_has_events', '_is_future', '_lru_size_alert', '_option_cls', '_optional_conn_ctx_manager', '_run_ddl_visitor', '_schema_translate_map', '_should_log_debug', '_should_log_info', '_sqla_logger_namespace', 'begin', 'clear_compiled_cache', 'connect', 'dialect', 'dispatch', 'dispose', 'driver', 'echo', 'engine', 'execution_options', 'get_execution_options', 'hide_parameters', 'logger', 'logging_name', 'name', 'pool', 'raw_connection', 'update_execution_options', 'url']
"""
print(engine)
print(engine.url)
print(engine.name)
