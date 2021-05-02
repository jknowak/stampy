import discord
from git import Repo
from config import ENVIRONMENT_TYPE, bot_dev_channel_id, discord_token

client = discord.Client()

offline_message = (
    "I'm going offline for maintenance. %s is updating me.\n"
    + "This is their latest commit message that I've received: \n'%s'\n"
    + "This message was committed at %s\nI'll be back!"
)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    repo = Repo(".")
    master = repo.head.reference
    actor = master.commit.author
    git_message = master.commit.message.strip()
    date = master.commit.committed_datetime.strftime("%A, %B %d, %Y at %I:%M:%S %p UTC%z")
    message = offline_message % (actor, git_message, date)
    print(message)
    await client.get_channel(bot_dev_channel_id[ENVIRONMENT_TYPE]).send(message)
    print("------")
    exit()


client.run(discord_token)
