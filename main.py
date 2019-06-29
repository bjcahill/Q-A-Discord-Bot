import discord
from discord.ext import commands

from file_io import *

BOT_API_KEY = 'NTkxNDM4MTc2MDY5ODc3Nzcz.XQwyCg.J4evGoO5rraFIObK1idN3ypl7Rk'

# These three variables are populated using 
# user input. See $set_channel and $set_owner.

# public_quesiton_id = -1
# private_quesiton_id = -1
# owner_id = -1

# Creates the bot with the $ command prefix.

client = commands.Bot(command_prefix = "$")
client.remove_command('help')

# When the bot starts up, it changes it's
# Discord presense to tell users to submit
# quetsions. It also populates the three id
# fields above with the correct values.

@client.event
async def on_ready():
    print('Bot is ready!')
    await client.change_presence(activity=discord.Game(name = "Use $askquestion or $help!"))

    bot_info_list = file_to_list("bot_info.dat")

    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])
        #459149381942378496|459628370666455072|245020637230268428

    write_list_to_file("bot_info.dat",bot_info_list)

# The command for users to submit a question.
# The question must be sent in using a DM to 
# the bot. All arguemnts besides askquestion
# are joined into one string.

@client.command()
async def help(ctx):

    # If the user is an admin, 
    # displays a different menu

    admin = "**Viewing administrative version.**" if ctx.message.author.guild_permissions.administrator else ""

    embed = discord.Embed(title="Q&A Bot", 
    description="A Bot designed to facilitate an ongoing Q&A with PyroJoe! Created by TheVirtualEconomist. " + admin, 
    color=discord.Color.red())

    embed.add_field(name="$askquestion -a question_text", value="Use this command to submit a question to PyroJoe! " + 
    "**The -a parameter is optional.** Use it if you want to submit a question anonymously. Make sure to DM the bot, as using the " + 
    "command does not work in a public channel. **Example:** $askquestion Do you like pineapple on pizza?")
    

    if ctx.message.author.guild_permissions.administrator == True:

        embed.add_field(name="$respond question_id", value="Administrative Command: The bot owner can use this command to respond " + 
        "to questions submitted to the Q&A. If set up properly, the specified question will appear in the public Q&A channel " + 
        "where the owner can respond to it like a normal discord conversation. " + "**Example:** $respond 594296975806169102")

        embed.add_field(name="$set_channel -public/-private channel_id", value="Administrative Command: Use this command to " + 
        "designate which channels will be used in the Q&A. The public channel is the channel all users see with the questions and " + 
        "answers. The private channel is the channel where the bot owner will receive questions decide which ones to respond to. " +
        "**Example** $set_channel -public #ongoing-q-and-a") 

        embed.add_field(name="$set_owner @owner", value="Administrative Command: Use this command to set a bot owner (Probably PyroJoe). " +
        "**Example** $set_owner @PyroJoe")

        embed.add_field(name="$clear_question_cashe", value="Administrative Command: Use this command to erase all questions submitted. " +
        "Using this command is not recommended unless you are experiencing performance issues with the bot. **Example:** $clear_question_cashe")

    embed.add_field(name="$help", value="Gives this message.")

    await ctx.send(embed=embed) 


@client.command()
async def askquestion(ctx, *args):

    usage_message = "\n\n**Usage:** $askquestion question_text"
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
        "\n\n **Note:** If this wasn't what you intended to submit, feel free to submit a another question.")

    # Notifying the #private-questions-channel.

    private_quesiton_channel = client.get_channel(private_quesiton_id)
    user_name = "Anonymous" if anonymous else "<@!" + str(ctx.message.author.id) + ">"

    private_text = ("**" + user_name +
    " sent in the following question:** (ID = " + str(ctx.message.id) + ")\n\n*" + question_text + "*") 
    await private_quesiton_channel.send(private_text)

@client.command()
async def respond(ctx,*args):

    usage_message = "\n\n**Usage:** $askquestion message_id"

    # Checks to see if the command user
    # has the proper privilages and 
    # everything is set up properly.

    if ctx.message.author.guild_permissions.administrator == False:
        error_message = "**Sorry, you must have administrator privilages to use this command.**"

        await ctx.send(error_message)
        return

    owner_id = get_owner()
    public_quesiton_id = get_public_channel()

    if owner_id == -1:
        error_message = "**A bot owner has not been set yet. Use $set_owner to set one.**"
        await ctx.send(error_message)
        return

    if owner_id != ctx.message.author.id:
        error_message = "**Sorry, you must be the owner of the bot to use this command.**"

        await ctx.send(error_message)
        return

    if(public_quesiton_id == -1):
        error_message = "**The public questions channel has not been set up correctly yet. Use $set_channel**"

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

    # Now the bot owner will respond 
    # to the question and it will be
    # posted to the public channel.

    public_quesiton_channel = client.get_channel(public_quesiton_id)

    user_name = "Anonymous" if question_submitter_id == 0 else "<@!" + str(question_submitter_id) + ">"

    public_text = ("**" + user_name + " asks:** " + 
                  "\n\n*" + question_text + "*")
    await public_quesiton_channel.send(public_text)

@client.command()
async def set_channel(ctx,*args):

    # Parses the command for errors. Command format
    # is specified in the usage_message.

    usage_message = ("\n\n**Usage:** $set_channel -private #channel-name" + 
                    "\n      **OR:** $set_channel -public #channel-name")

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

    # Saves the entered channel.

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

@client.command()
async def set_owner(ctx,*args):
        
    # Parses the command for errors. Command format
    # is specified in the usage_message.

    usage_message = ("\n\n**Usage:** $set_owner @owner")

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
    
    # Saves the entered user.

    bot_info_list = file_to_list("bot_info.dat")
    if len(bot_info_list) == 0:
        bot_info_list.append([-1,-1,-1])

    owner_id = ctx.message.mentions[0].id

    bot_info_list[0][2] = owner_id
    write_list_to_file("bot_info.dat",bot_info_list)

    await ctx.send("**Correctly set the owner to <@!" + str(owner_id) +">!**")

@client.command()
async def clear_question_cashe(ctx,*args):

    if ctx.message.author.guild_permissions.administrator == False:
        error_message = "**Sorry, you must have administrator privilages to use this command.**"

        await ctx.send(error_message)
        return

    line_list = file_to_list("questions.dat")
    num_questions_removed = len(line_list)

    line_list = []
    write_list_to_file("questions.dat",line_list)

    await ctx.send("**Cleared the question cashe.** " + str(num_questions_removed) + " questions removed.")

client.run(BOT_API_KEY)