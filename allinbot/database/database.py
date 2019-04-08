import typing
import pickle
import asyncio
import firebase_admin
import firebase_admin.credentials
import firebase_admin.db
import os
import json

T = typing.TypeVar('T')

FIREBASE_CONFIG = json.loads(os.getenv("FIREBASE_CONFIG", {}))

firebase_admin.initialize_app(
    credential=firebase_admin.credentials.Certificate(FIREBASE_CONFIG.get("serviceAccount", {})),
    options=FIREBASE_CONFIG)

class QueryBuilder:
    def __init__(self):
        self._path = []
        self._order_by_child_path = None
        self._equal_to_val = None
        self._is_shallow_query = False

    def _clone(self) -> "QueryBuilder":
        clone = QueryBuilder()
        clone._path = [] + self._path
        clone._order_by_child_path = self._order_by_child_path
        clone._equal_to_val = self._equal_to_val
        clone._is_shallow_query = self._is_shallow_query
        return clone

    def child(self, path: str) -> "QueryBuilder":
        clone = self._clone()
        clone._path.append(path)
        return clone
        
    def order_by_child(self, path: str) -> "QueryBuilder":
        clone = self._clone()
        clone._order_by_child_path = path
        return clone

    def equal_to(self, value) -> "QueryBuilder":
        clone = self._clone()
        clone._equal_to_val = value
        return clone
    
    def set_shallow(self, value: bool) -> "QueryBuilder":
        clone = self._clone()
        clone._is_shallow_query = bool(value)
        return clone

    def get(self) -> dict:
        ref = firebase_admin.db.reference()
        
        for child in self._path:
            ref = ref.child(child)
        
        if self._order_by_child_path:
            query = ref.order_by_child(self._order_by_child_path)

            if self._equal_to_val:
                query.equal_to(self._equal_to_val)
        else:
            query = None
        
        if query:
            return query.get()
        else:
            return ref.get(shallow=self._is_shallow_query)


class DatabaseTask(typing.Generic[T]):
    def execute_with_database(self, query_builder: QueryBuilder) -> T:
        raise NotImplementedError("This must be implemented!")

    async def perform_task(self, event_loop: asyncio.AbstractEventLoop) -> T:
        return await event_loop.run_in_executor(None, self._process_func)

    def _process_func(self) -> T:
        return self.execute_with_database(QueryBuilder())


async def perform_database_task(event_loop: asyncio.AbstractEventLoop,
                                task: DatabaseTask[T]) -> T:
    return await task.perform_task(event_loop)
