"""Discord bot definition for Chip"""
import os
import asyncio
import discord
import emoji
from dotenv import load_dotenv
load_dotenv()

import config
if config.FEAT_ADVISOR:
    from uwin_ai_assistant import inference

if config.FEAT_AUTOMOD:
    from automod import AutomodInterface
    
from messages import info, error, success, log

# Setup

intents = discord.Intents.all()
bot = discord.Bot(command_prefix="c!", intents=intents, help_command=None)

if config.FEAT_AUTOMOD: 
    automod = AutomodInterface()

ADVISOR_CHANNEL_ID = int(os.getenv("ADVISOR_CHANNEL"))
AUTOMOD_CHANNEL_ID = int(os.getenv("AUTOMOD_CHANNEL"))

# Events

@bot.event
async def on_ready():
    """Triggers when the bot is running"""
    activity = discord.Game(name="Being cool | /ask", type=2)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Discord bot online")

@bot.event
async def on_message(message):
    """Event handler for messages, flags problematic content"""
    if not config.FEAT_AUTOMOD or message.author == bot.user:
        return
    else:
        score = automod.analyze_message(emoji.demojize(message.content))
        if float(score[1]) > 0.8:
            await log(message, float(score[1]), AUTOMOD_CHANNEL_ID)

@bot.event
async def on_message_edit(message_before, message_after):
    """Event handler for message edits, flags problematic content"""
    if not config.FEAT_AUTOMOD or message_before.author == bot.user:
        return
    else:
        score = automod.analyze_message(emoji.demojize(message_after.content))
        if float(score[1]) > 0.8:
            await log(message_after, float(score[1]), AUTOMOD_CHANNEL_ID)

# Commands

@bot.slash_command(name="help", description="Help command")
async def help(ctx):
    """Displays a help message"""
    message = """
        **Chip is an AI powered discord moderation bot and chatbot. It uses machine learning to detect toxic messages and automatically flag for the moderators, and is also available to assist with any queries you may have about Computer Science at The University of Windsor! (Double check important information, AI can make mistakes)**
                            
        **/help** - Displays this message
        **/ask** - Ask Chip anything about Computer Science at the University of Windsor!
    """
    await info(ctx, "Info", message)

@bot.slash_command(name="ask", description="Ask Chip anything about Computer Science at the University of Windsor!")
async def ask(ctx, query: str):
    """Respond to a user query using the RAG model"""
    if not config.FEAT_ADVISOR:
        await error(ctx, "Error", "This feature is currently disabled")
        return
    if ctx.channel.id == ADVISOR_CHANNEL_ID:
        await ctx.defer() # Prevent timeout
        author_id = ctx.author.id
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, inference.generate_response, query)
        if len(query) < 256:
            await success(ctx, query, f"<@{author_id}> \n\n {response}")
        else:
            await error(ctx, "Error", "Query must be fewer than 256 characters")
    else:
        await error(ctx, "Error", f"This command can only be used in the advisor channel: <#{ADVISOR_CHANNEL_ID}>")

bot.run(os.getenv("DISCORD_TOKEN"))
