class Task:
    async def perform_task(self):
        raise NotImplementedError("This must be implemented!")

    def should_repeat_task(self) -> bool:
        raise NotImplementedError("This must be implemented!")