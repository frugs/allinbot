from asyncio import AbstractEventLoop
from typing import List

import asyncio

from .task import Task


class TaskScheduler:

    def __init__(self, event_loop: AbstractEventLoop, tasks: List[Task], interval: int):
        """
        :param event_loop: event loop to execute tasks on
        :param tasks: list of tasks to schedule
        :param interval: interval in seconds
        """
        self.event_loop = event_loop
        self.tasks = tasks
        self.interval = interval

    def start(self):
        return asyncio.ensure_future(self.do_and_reschedule_tasks(), loop=self.event_loop)

    async def do_and_reschedule_tasks(self):
        for task in self.tasks:
            await task.perform_task()

        repeating_tasks = [task for task in self.tasks if task.should_repeat_task()]

        while True:
            await asyncio.sleep(self.interval)
            for task in repeating_tasks:
                await task.perform_task()


