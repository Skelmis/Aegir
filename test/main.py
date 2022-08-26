@bot.event()
async def on_message(message: nextcord.Message):
    if bot.is_debug_mode and message.author.id not in COMBINED_ACCOUNTS:
        # During dev only run commands from us so as to not impact the end user
        return

    # Ignore messages sent by bots
    if message.author.bot:
        return

    # Whenever the bot is tagged, respond with its prefix
    if match := mention.match(message.content):
        if int(match.group("id")) == bot.user.id:
            data = await bot.db.config.find(message.guild.id)
            if not data or "prefix" not in data:
                prefix = bot.DEFAULT_PREFIX
            else:
                prefix = data["prefix"]

            await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)

    # Only run commands in menudocs guild.
    # Alternately run them if its Skelmis or Auxtal
    # await bot.process_commands(message)
