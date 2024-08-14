import discord
from discord.ext import commands, tasks
from discord import ButtonStyle
from discord.ui import Button, View
from time import strftime

TOKEN = 'TOKEN'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='..!', intents=intents)

class PingMirror(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recchan = {}
        self.role = {}
        self.pinged = []
        self.send = False

    @commands.Cog.listener()
    async def on_ready(self):
        """Cette méthode est appelée lorsque le bot est prêt."""
        print(f"Logged in as {self.bot.user}")
        self.send_mirror_request.start()  # Démarre la tâche après que le bot soit prêt
        print("PingMirror Cog is loaded and ready.")

    @commands.command(name='init')
    async def init(self, ctx, role: discord.Role = None):
        """Enregistre le canal et le rôle pour les messages automatiques."""
        if role is None:
            await ctx.send("Usage: ..!init <role>")
        else:
            self.recchan[ctx.guild.id] = ctx.channel.id
            self.role[ctx.guild.id] = role.id
            await ctx.send(f"Channel and role successfully added! Role: {role.mention}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        """Réagit aux interactions des boutons."""
        if isinstance(interaction, discord.Interaction):
            if interaction.data['custom_id'] == 'ping_button':
                if interaction.guild.id not in self.pinged:
                    self.pinged.append(interaction.guild.id)
                    
                    # Obtiens le rôle enregistré pour le serveur
                    role_id = self.role.get(interaction.guild.id)
                    if role_id:
                        role = interaction.guild.get_role(role_id)
                        if role:
                            # Envoie un message en mentionnant le rôle
                            await interaction.response.send_message(f"Well played {interaction.user.mention}. {role.mention}")
                        else:
                            # Envoie un message si le rôle n'est pas trouvé
                            await interaction.response.send_message(f"Well played {interaction.user.mention}. Le rôle mentionné est introuvable.")
                    else:
                        await interaction.response.send_message(f"Well played {interaction.user.mention}. Aucun rôle enregistré pour ce serveur.")

    @tasks.loop(seconds=1)
    async def send_mirror_request(self):
        """Envoie des messages avec un bouton dans les canaux enregistrés."""
        if strftime("%H") != strftime("%M"):
            if self.send:
                self.send = False
                self.pinged = []
            return
        print("Sending msg!")
        if not self.send:
            self.send = True
            for guild_id, channel_id in self.recchan.items():
                guild = self.bot.get_guild(guild_id)
                if guild:
                    channel = guild.get_channel(channel_id)
                    if channel and channel.permissions_for(guild.me).send_messages:
                        print("Sending!")
                        # Création du bouton Ping
                        button = Button(label="Ping mirror time", style=ButtonStyle.primary, custom_id='ping_button')
                        
                        # Créer une vue et ajouter le bouton
                        view = View()
                        view.add_item(button)
                        
                        # Envoyer le message avec le bouton
                        await channel.send('Hello, it’s mirror time!', view=view)

async def main():
    # Ajouter la classe comme un Cog au bot
    await bot.add_cog(PingMirror(bot))

    # Démarrer le bot
    await bot.start(TOKEN)

# Démarrer le bot en appelant la fonction main
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
