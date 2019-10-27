## This is an advanced Discord bot designed to offer an elegant Q&A experience!

### There are six commands built into the bot.

#### Public commands:

* ;askquestion question_text
* ;help

#### Administrative commands:

* ;respond question_ID
* ;set_channel -public/-private channel_name 
* ;set_owner @owner_name
* ;clear_question_cashe

Note that the public channel is the channel everyone sees (displaying selected questions and answers). The private channel is the channel only seen by the person giving the Q&A. It displays all questions submitted by users, allowing the owner to pick which questions they want to respond to.

#### Developer Note:

To start the bot, you must enter your Discord client secret into the APIKey field in the config.ini file. 
You can also change the bot's command prefix by changing the CommandPrefix field in the config.ini file. By default, the command prefix is ;

Further, the bot makes use of two .dat files to hold data. The formats are as follows:

* questions.dat: Message_ID | Author_ID | Question_text
* server_info.dat: Public_channel |  Private_channel | Owner_ID