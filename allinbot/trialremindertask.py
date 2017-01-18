import discord
import datetime

from .task import Task


TRIAL_PERIOD_IN_DAYS = 12
TRIAL_MEMBER_ROLE_ID = "183243538425839617"


class TrialPeriodReminderTask(Task):

    def __init__(self, reminder_channel_id: str, reminder_mention: str):
        self.reminder_channel_id = reminder_channel_id
        self.reminder_mention = reminder_mention

    async def perform_task(self, client: discord.Client):
        await client.wait_until_login()

        trial_finished_members = [
            member
            for member
            in client.get_all_members()
            if TrialPeriodReminderTask._should_trial_be_over(member)]

        trial_finished_members.sort(key=lambda x: x.joined_at)

        if trial_finished_members:
            mentions = [member.mention + " joined on " + member.joined_at.strftime("**%d %h %Y**")
                        for member
                        in trial_finished_members]
            message = self.reminder_mention + " Trial members due to finish their trials:\n" + "\n".join(mentions)

            channel = client.get_channel(self.reminder_channel_id)

            # fixme: seems like we can sometimes be logged in but not fully connected to server (so no channel list)
            if channel:
                await client.send_message(channel, message)

    @staticmethod
    def _should_trial_be_over(member: discord.Member):
        def is_trial_member():
            return any(TRIAL_MEMBER_ROLE_ID == role.id for role in member.roles)

        def twelve_days_elapsed_since_joining_server():
            delta = datetime.datetime.utcnow() - member.joined_at
            return delta.days >= TRIAL_PERIOD_IN_DAYS

        return is_trial_member() and twelve_days_elapsed_since_joining_server()

