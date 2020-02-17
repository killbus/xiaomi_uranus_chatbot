""" admin messages generator """


async def stats_message(stats):
    """ Generate telegram message of stats command """
    message = f"**Bot current statistics:**\n\n" \
              f"Bot is currently used by **{stats['usage']['users']}** users " \
              f"and **{stats['usage']['channels']}** channels, " \
              f"and available in **{stats['usage']['groups']}** groups.\n\n" \
              f"There are **{stats['subscriptions']['firmware']}** firmware subscriptions, " \
              f"**{stats['subscriptions']['miui']}** miui subscriptions, and " \
              f"**{stats['subscriptions']['vendor']}** vendor subscriptions."
    return message
