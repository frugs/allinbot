import discord


class Handler:
    def can_handle_message(self, message: discord.Message) -> bool:
        """
        Messages will be passed to this function for the handler to decide whether it is interested in or not - this
        function should return true if and only if this is the case.

        Messages for which this function returned true will then be passed to the asynchronous handle_message()
        function.
        """
        raise NotImplementedError("handlers must implement this")

    async def handle_message(self, client: discord.Client,
                             message: discord.Message):
        """
        Messages for which can_handle_message() returned true will be passed to this handler for the handler to deal
        with as appropriate.
        """
        raise NotImplementedError("handlers must implement this")

    async def description(self, client: discord.Client) -> str:
        """
        Should return a user friendly description detailing how this handler is used, shown to the user.
        """
        raise NotImplementedError("handlers must implement this")
