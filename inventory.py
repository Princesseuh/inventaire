import discord
import asyncio
import aiosqlite
import random
import difflib

from discord.ext import commands

class Inventory:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return

        def check(reaction, user):
            return user == message.author

        def check2(msg):
            return msg.author == message.author and msg.content.strip() != ""

        salutations = ["bonjour", "hello", "hi", "salut", "hey", "je t'aime"]
        content = message.content.lower()
        if any(mot in content for mot in salutations):
            await message.channel.trigger_typing()
            await asyncio.sleep(2)

            users = await self.get_users()
            user_list = [user[0] for user in users]

            if message.author.id in user_list:
                inventory = await self.get_inventory()
                e = discord.Embed(description=inventory)
                e.set_author(name="Contenu de l'inventaire")

                print("Showing inventory for {}".format(message.author.display_name))

                await message.channel.send("Oh! Bonjour! Tu m'as déjà grandement aidé, je n'ai pas besoin d'aide supplémentaire. Merci beaucoup! Voici le contenu de l'inventaire de Princesseuh : ", embed=e)
                return

            intro_message = await message.channel.send("Oh! Bonjour! Je suis Inventaire. Habituellement, je m'occupe de gérer l'inventaire de Princesseuh mais.. J'ai eu un petit problème et j'aurais bien besoin de ton aide!\n\nC'est un peu gênant mais.. j'ai perdu tous ses objets! Enfin pas tous.. J'ai réussi à récupérer quelques trucs mais impossible de trouver le reste! Est-ce que tu voudrais bien m'aider?")
            await intro_message.add_reaction("🇴")
            await intro_message.add_reaction("🇳")

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send("Ah.. Je présume que ça veut dire non. Dommage.")
                return
            else:
                if str(reaction.emoji) == "🇴":
                    await message.channel.trigger_typing()
                    await asyncio.sleep(2)
                    inventory = await self.get_inventory()
                    e = discord.Embed(description=inventory)
                    e.set_author(name="Contenu de l'inventaire")

                    await message.channel.send("Ohh! Merci beaucoup! Je ne sais pas ce que j'aurais fait sans toi! Connaissant Princesseuh, elle aurait été furieuse si son inventaire avait été perdu (et elle m'aurait sûrement tapée!)\nVoici ce qu'il y a dans l'inventaire pour le moment :", embed=e)

                    await message.channel.trigger_typing()
                    await asyncio.sleep(4)
                    await message.channel.send(".. Oh?! Tu as déjà trouvé quelque chose? Chouette! Ajoutons ça à l'inventaire!\n\n(Tape le nom de l'objet à ajouter)")

                    too_big = True
                    while (too_big):
                        try:
                            msg = await self.bot.wait_for("message", timeout=90.0, check=check2)
                        except asyncio.TimeoutError:
                            await message.channel.send("Hmm.. Désolée mais.. Je n'ai pas toute la journée! Je dois retrouver ses objets. Reviens quand tu seras sûr de ce que tu as trouvé.")
                            return
                        else:
                            await message.channel.trigger_typing()
                            await asyncio.sleep(2)

                            if (len(msg.content.strip()) > 100):
                                await message.channel.send("Hmm.. C'est un peu trop gros pour l'inventaire.. Est-ce que tu pourrais trouver quelque chose d'autre? (Tape le nom d'un objet de moins de 100 caractères)")
                            else:
                                break

                    possible_messages = [
                        "`{}`?! Je ne suis pas sûre qu'elle avait ça dans son inventaire mais bon.. Autant l'ajouter, elle sera contente! J'ajoute ça à l'inventaire!",
                        "Wow! `{}`! La plupart des gens l'auraient gardé pour eux-mêmes. Merci beaucoup! Elle sera contente! Ajoutons cet objet à l'inventaire..",
                        "Hmm.. Je ne suis pas sûre comment je vais faire pour faire rentrer ça dans l'inventaire mais si tu pense qu'elle avait ça.. Je vais l'ajouter à l'inventaire!"
                    ]

                    rnumber = random.randint(0, len(possible_messages)-1)
                    await message.channel.send(possible_messages[rnumber].format(msg.content.strip()))
                    too_big = False

                    await message.channel.trigger_typing()

                    async with aiosqlite.connect("database.db") as db:
                        await db.execute("INSERT INTO items VALUES(NULL, ?, ?)", (msg.content.strip(), msg.author.id))
                        await db.execute("INSERT INTO users VALUES(NULL, ?)", [msg.author.id])
                        await db.commit()

                    print("{} added to inventory by {}".format(msg.content.strip(), message.author.display_name))

                    await asyncio.sleep(3)
                    offer = await message.channel.send("Et voilà! C'est fait!\n\nJ'aimerais te remercier avec quelque chose d'un peu plus conséquent qu'un simple merci.. Eeeet siiii.. Je te laissais prendre un des objets de Princesseuh en échange de celui que tu viens de me donner? Ça te dirait? Je suis sûre qu'elle ne sera pas trop fâchée!")
                    await offer.add_reaction("🇴")
                    await offer.add_reaction("🇳")

                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await message.channel.send("Ha! Je vais prendre ça pour un non :stuck_out_tongue: Ton honnêteté est honorable :) Merci beaucoup pour ton aide! Reparle moi si tu veux voir le contenu de l'inventaire de Princesseuh!")
                        return
                    else:
                        if str(reaction.emoji) == "🇴":
                            await message.channel.trigger_typing()
                            await asyncio.sleep(2)

                            inventory = await self.get_inventory()
                            e = discord.Embed(description=inventory)
                            e.set_author(name="Contenu de l'inventaire")

                            await message.channel.send("Ooh! Qu'est-ce que tu souhaiterais prendre? Pour rappel, voici ce qu'il y a dans son inventaire actuellement (Tape le nom de l'objet que vous souhaitez prendre) : ", embed=e)

                            no_object = True
                            msg3 = ""
                            while (no_object):
                                try:
                                    msg2 = await self.bot.wait_for("message", timeout=120.0, check=check2)
                                except asyncio.TimeoutError:
                                    await message.channel.send("Désolée! Je n'ai pas toute la journée! J'espère qu'un merci suffit! Reparle moi si tu veux voir le contenu de l'inventaire de Princesseuh!")
                                    return
                                else:
                                    item_to_get = msg2.content.strip()
                                    inventory = await self.get_inventory(False)
                                    item_list = [item[0] for item in inventory]

                                    if item_to_get in item_list:
                                        no_object = False
                                        msg3 = item_to_get
                                        break
                                    else:
                                        match = difflib.get_close_matches(item_to_get, item_list)
                                        matches = " Peut-être voulais-tu dire {}?".format(", ".join("`{}`".format(result) for result in match))

                                        await message.channel.send("Hmm.. Désolée mais je ne trouve pas de `{}` dans l'inventaire! Réessayons!{}".format(item_to_get, matches if match else ""))

                            await message.channel.trigger_typing()

                            async with aiosqlite.connect("database.db") as db:
                                await db.execute("DELETE FROM items where id in (SELECT id FROM items WHERE item == (?) LIMIT 1)", [msg3])
                                await db.commit()

                            print("{} removed from inventory by {}".format(msg3, message.author.display_name))

                            await asyncio.sleep(2)
                            await message.channel.send("Ha! Bon choix, je suis sûre qu'elle n'a pas besoin de ce `{}`! C'est à toi maintenant :)\nMerci beaucoup de ton aide! Si tu veux voir ce qu'il y a dans l'inventaire, suffit de revenir me dire bonjour! :)".format(msg3))
                            return
                        elif str(reaction.emoji) == "🇳":
                            await message.channel.trigger_typing()
                            await asyncio.sleep(2)
                            await message.channel.send("Ha! Je ne sais pas si Princesseuh a vraiment besoin de tout ce qu'elle a dans son sac mais je suis sûre qu'elle apprécie ton honnêteté! :) Merci beaucoup de ton aide! Si tu veux voir ce qu'il y a dans l'inventaire, suffit de revenir me dire bonjour!")
                            return

                elif str(reaction.emoji) == "🇳":
                    await message.channel.trigger_typing()
                    await asyncio.sleep(1)
                    await message.channel.send("Ah.. Dommage.. Si tu change d'idée, revient me parler, j'ai toujours besoin d'une aide comme la tienne!")
                    return

    @commands.command(aliases=["d"])
    async def debug(self, ctx):
        items = await self.get_inventory()
        users = await self.get_users()
        print(items)
        print(users)

    async def get_users(self):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.execute("SELECT discord_id FROM users")
            rows = await cursor.fetchall()
            await cursor.close()

        return rows

    async def get_inventory(self, as_string=True):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.execute('SELECT item, COUNT(item) FROM items GROUP BY item ORDER BY count(item) DESC')
            rows = await cursor.fetchall()
            await cursor.close()

        if as_string:
            result = "\n".join("x{} {}".format(item[1], item[0]) for item in rows)
            return result
        else:
            return rows


def setup(bot):
    bot.add_cog(Inventory(bot))
