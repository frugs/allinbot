import typing
import pickle
import asyncio
import pyrebase

T = typing.TypeVar('T')


class DatabaseTask(typing.Generic[T]):
    def __init__(self, db_config: dict):
        self._db_config = db_config

    def execute_with_database(self, db: pyrebase.pyrebase.Database) -> T:
        raise NotImplementedError("This must be implemented!")

    async def perform_task(self, event_loop: asyncio.AbstractEventLoop) -> T:
        return await event_loop.run_in_executor(None, self._process_func)

    def _process_func(self) -> T:
        db = open_db_connection(self._db_config)
        return self.execute_with_database(db)


def open_db_connection(config) -> pyrebase.pyrebase.Database:
    return pyrebase.initialize_app(config).database()


async def perform_database_task(event_loop: asyncio.AbstractEventLoop,
                                task: DatabaseTask[T]) -> T:
    return await task.perform_task(event_loop)
