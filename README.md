## This is an advanced Discord bot designed to offer an elegant Q&A experience!

### There are six commands built into the bot.

#### Public commands:

* $askquestion question_text
* $help

#### Administrative commands:

* $respond question_ID
* $set_channel -public/-private channel_name
* $set_owner @owner_name
* $clear_question_cashe

#### Developer Note:
The program makes use of two .dat files to hold data. The formats are as follows:

* questions.dat: Message_ID | Author_ID | Question_text
* server_info.dat: Public_channel |  Private_channel | Owner_ID