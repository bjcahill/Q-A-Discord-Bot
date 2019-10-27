import discord
from discord.ext import commands

from file_io import *

import datetime
import configparser

config = configparser.ConfigParser()

config.read("config.ini")

BOT_API_KEY = config.get('Settings', 'APIKey')
COMMAND_PREFIX = config.get('Settings', 'CommandPrefix')

# Creates the bot with the specified command prefix.

client = commands.Bot(command_prefix = COMMAND_PREFIX)
client.remove_command('help')

# When the bot starts up, it changes it's
# Discord presense to tell users to submit
# quetsions.

@client.event
async def on_ready():
    print('Bot is ready!')
    await client.change_presence(activity=discord.Game(name = "Use " + COMMAND_PREFIX + "askquestion or " + COMMAND_PREFIX + "help!"))

    bot_info_list = file_to_list("bot_info.dat")

    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])

    write_list_to_file("bot_info.dat",bot_info_list)

# The command for users to submit a question.
# The question must be sent in using a DM to 
# the bot. All arguemnts besides askquestion
# are joined into one string.

@client.command()
async def askquestion(ctx, *args):

    usage_message = "\n\n**Usage:** " + COMMAND_PREFIX + "askquestion question_text"
    anonymous = False

    # Checks to see if the message is a DM and
    # if it is not, the bot will give an error.

    if not isinstance(ctx.message.channel, discord.DMChannel):                      
        error_message = ("**This command does not work in a public channel. " +
        "**\n\nDirect message the bot to submit a question. " + usage_message)

        await ctx.send(error_message)
        return

    # Checks to see if the question has content.
    # If not, it gives the corresponding error.
    # If -a is set, the question is handled 
    # anonymously. 

    if len(args) > 0 and args[0] == '-a':
        anonymous = True
        question_text = " ".join(args[1:])
    else:
        question_text = " ".join(args)

    if len(question_text) == 0:
        error_message = "**No question detected. **" + usage_message

        await ctx.send(error_message)
        return

    # If the above conditions pass, the question
    # is saved to file.

    question_list = file_to_list("questions.dat")

    if anonymous:
        question_list.append([0,ctx.message.id,question_text])
    
    else:
        question_list.append([ctx.message.author.id,ctx.message.id,question_text])

    write_list_to_file("questions.dat",question_list)

    # Checks to see if the required 
    # channels are set up properly.

    private_quesiton_id = get_private_channel()

    if private_quesiton_id == -1:
        error_message = "**Admins have not set up the bot properly. Contact an admin for help.**"
        await ctx.send(error_message)
        return

    # Feedback to the user

    anon_text = " anonymously" if anonymous else ""
    await ctx.send("**You submitted the following question" + anon_text + ":**\n\n"+ question_text + 
        "\n\n**Note:** If this wasn't what you intended to submit, feel free to submit a another question.")

    # Notifying the #private-questions-channel.

    private_quesiton_channel = client.get_channel(private_quesiton_id)

    embed = discord.Embed(title="Question Submitted",value = "",
    color=discord.Color.red())

    embed.add_field(name="User", value = "<@!" + str(ctx.message.author.id) + ">")
    embed.add_field(name="Question", value = question_text)
    embed.add_field(name="Anonymous", value = "Yes" if anonymous else "No")
    embed.add_field(name="ID", value = str(ctx.message.id))
    embed.add_field(name="Time Submitted", value = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S UTC'))

    await private_quesiton_channel.send(embed=embed)

# Allows the owner of the bot to
# "respond" to a question, causing 
# it to appear in the public channel.

@client.command()
async def respond(ctx,*args):

    usage_message = "\n\n**Usage:** " + COMMAND_PREFIX + "askquestion message_id"

    # Checks to see if the command user
    # has the proper privilages and 
    # everything is set up properly.

    if isinstance(ctx.message.channel, discord.DMChannel):                      
        error_message = "**This command only works when used on a server.**" + usage_message

        await ctx.send(error_message)
        return

    if ctx.message.author.guild_permissions.administrator == False:
        error_message = "**Sorry, you must have administrator privilages to use this command.**"

        await ctx.send(error_message)
        return

    owner_id = get_owner()
    public_quesiton_id = get_public_channel()

    if owner_id == -1:
        error_message = "**A bot owner has not been set yet. Use " + COMMAND_PREFIX + "set_owner to set one.**"
        await ctx.send(error_message)
        return

    if owner_id != ctx.message.author.id:
        error_message = "**Sorry, you must be the owner of the bot to use this command.**"

        await ctx.send(error_message)
        return

    if(public_quesiton_id == -1):
        error_message = "**The public questions channel has not been set up correctly yet. Use " + COMMAND_PREFIX + "set_channel**"

        await ctx.send(error_message)
        return

    # Handles the input entered 

    if len(args) != 1:
        error_message = "**Incorrect number of parameters.**\n\n" + usage_message

        await ctx.send(error_message)
        return

    question_list = file_to_list("questions.dat")
    question_submitter_id = -1
    question_text = "N/A"
    found = False

    for line in question_list:
        if int(line[1]) == int(args[0]):
            question_submitter_id = int(line[0])
            question_text = line[2]
            found = True

    if not found:
        error_message = "**Question with the specified ID not found.** " + usage_message

        await ctx.send(error_message)
        return

    # Now the question will be
    # posted to the public channel.

    public_quesiton_channel = client.get_channel(public_quesiton_id)

    user_name = "Anonymous" if question_submitter_id == 0 else "<@!" + str(question_submitter_id) + ">"

    public_text = ("**" + user_name + " asks:** " + 
                  "\n\n*" + question_text + "*")
    await public_quesiton_channel.send(public_text)

# Allows server administrators to
# set which channels will be used
# for the Q&A.

@client.command()
async def set_channel(ctx,*args):

    # Parses the command for errors. Command format
    # is specified in the usage_message.

    usage_message = ("\n\n**Usage:** " + COMMAND_PREFIX + "set_channel -private #channel-name" + 
                    "\n      **OR:** " + COMMAND_PREFIX + "set_channel -public #channel-name")

    if isinstance(ctx.message.channel, discord.DMChannel):                      
        error_message = "**This command only works when used on a server.**" + usage_message

        await ctx.send(error_message)
        return

    if ctx.message.author.guild_permissions.administrator == False:
        error_message = "**Sorry, you must have administrator privilages to use this command.**"

        await ctx.send(error_message)
        return

    if len(args) != 2:
        error_message = "**Incorrect number of parameters.**" + usage_message

        await ctx.send(error_message)
        return

    if not ((args[0] == "-public") or (args[0] == "-private")):
        error_message = "**Type of channel incorrectly specified.**" + usage_message

        await ctx.send(error_message)
        return

    if len(ctx.message.channel_mentions) != 1:
        error_message = "**Channel not found.**" + usage_message

        await ctx.send(error_message)
        return

    # Saves the entered channel

    bot_info_list = file_to_list("bot_info.dat")
    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])

    if(args[0] == "-public"):
        public_quesiton_id = ctx.message.channel_mentions[0].id

        bot_info_list[0][0] = public_quesiton_id
        write_list_to_file("bot_info.dat",bot_info_list)

        await ctx.send("**Correctly set the public questions channel!**")
        return

    elif args[0] == "-private":
        private_quesiton_id = ctx.message.channel_mentions[0].id

        bot_info_list[0][1] = private_quesiton_id
        write_list_to_file("bot_info.dat",bot_info_list)

        await ctx.send("**Correctly set the private questions channel!**")
        return

# Allows server administrators to
# set which user is the bot owner
# for the Q&A.

@client.command()
async def set_owner(ctx,*args):
        
    # Parses the command for errors. Command format
    # is specified in the usage_message.

    usage_message = ("\n\n**Usage:** " + COMMAND_PREFIX + "set_owner @owner")

    if isinstance(ctx.message.channel, discord.DMChannel):                      
        error_message = "**This command only works when used on a server.**" + usage_message

        await ctx.send(error_message)
        return

    if ctx.message.author.guild_permissions.administrator == False:
        error_message = "**Sorry, you must have administrator privilages to use this command.**"

        await ctx.send(error_message)
        return

    if len(args) != 1:
        error_message = "**Incorrect number of parameters.**" + usage_message

        await ctx.send(error_message)
        return

    if len(ctx.message.mentions) != 1:
        error_message = "**User not found.**" + usage_message

        await ctx.send(error_message)
        return
    
    # Saves the entered user

    bot_info_list = file_to_list("bot_info.dat")
    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])

    owner_id = ctx.message.mentions[0].id

    bot_info_list[0][2] = owner_id
    write_list_to_file("bot_info.dat",bot_info_list)

    await ctx.send("**Correctly set the owner to <@!" + str(owner_id) +">!**")

# Allows server administrators to
# clear the history of questions 
# asked. Questions are not deleted
# when they are responded too, so 
# this can be used to clear data 
# that is no longer being used.

@client.command()
async def clear_question_cashe(ctx,*args):
    
    # Error handling

    if isinstance(ctx.message.channel, discord.DMChannel):                      
        error_message = "**This command only works when used on a server.**"

        await ctx.send(error_message)
        return

    if ctx.message.author.guild_permissions.administrator == False:
        error_message = "**Sorry, you must have administrator privilages to use this command.**"

        await ctx.send(error_message)
        return

    # Clearing the questions.dat file

    line_list = file_to_list("questions.dat")
    num_questions_removed = len(line_list)

    line_list = []
    write_list_to_file("questions.dat",line_list)

    await ctx.send("**Cleared the question cashe.** " + str(num_questions_removed) + " questions removed.")

# Shows the bot's functionality
# in a Discord Embed.

@client.command()
async def help(ctx):

    # If the user is an admin, 
    # displays a different menu.

    if isinstance(ctx.message.channel, discord.DMChannel):                      
        error_message = "**This command only works when used on a server.**"

        await ctx.send(error_message)
        return

    admin = "**Viewing administrative version.**" if ctx.message.author.guild_permissions.administrator else ""

    embed = discord.Embed(title="Q&A Bot", 
    description="A Bot designed to facilitate an ongoing Q&A! Created by TheVirtualEconomist. " + admin, 
    color=discord.Color.red())

    embed.add_field(name= COMMAND_PREFIX + "askquestion -a question_text", value="Use this command to submit a question! " + 
    "**The -a parameter is optional.** Use it if you want to submit a question anonymously. Make sure to DM the bot, as using the " + 
    "command does not work in a public channel. **Example:** " + COMMAND_PREFIX + "askquestion Do you like pineapple on pizza?")
    
    if ctx.message.author.guild_permissions.administrator == True:

        embed.add_field(name=COMMAND_PREFIX + "respond question_id", value="Administrative Command: The bot owner can use this command to respond " + 
        "to questions submitted to the Q&A. If set up properly, the specified question will appear in the public Q&A channel " + 
        "where the owner can respond to it like a normal discord conversation. " + "**Example:** " + COMMAND_PREFIX + "respond 594296975806169102")

        embed.add_field(name=COMMAND_PREFIX + "set_channel -public/-private channel_id", value="Administrative Command: Use this command to " + 
        "designate which channels will be used in the Q&A. The public channel is the channel all users see with the questions and " + 
        "answers. The private channel is the channel where the bot owner will receive questions decide which ones to respond to. " +
        "**Example** " + COMMAND_PREFIX + "set_channel -public #ongoing-q-and-a") 

        embed.add_field(name=COMMAND_PREFIX + "set_owner @owner", value="Administrative Command: Use this command to set a bot owner. " +
        "**Example** " + COMMAND_PREFIX + "set_owner @Username")

        embed.add_field(name=COMMAND_PREFIX + "clear_question_cashe", value="Administrative Command: Use this command to erase all questions submitted. " +
        "Using this command is not recommended unless you are experiencing performance issues with the bot. **Example:** " + COMMAND_PREFIX + "clear_question_cashe")

    embed.add_field(name=COMMAND_PREFIX + "help", value="Gives this message.")

    await ctx.send(embed=embed) 

# Runs the bot

client.run(BOT_API_KEY)