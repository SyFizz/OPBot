from random import choices
from unicodedata import category
from disnake import Guild
import interactions
import sys
import json
import os


def loadConfigs():
    with open ('config.json', encoding="UTF8") as f:
        global config
        config = json.load(f)

    with open ('lang.json', encoding="UTF8") as f:
        global lang 
        lang = json.load(f)

async def noPermission(ctx):
    embed = interactions.Embed(
            title=lang['error'],
            description=lang['no_permission'].replace('{user}', ctx.author.name),
            footer=EMBED_FOOTER,
            color=int(config['embeds']['colors']['error'], base=16)
        )
    await ctx.send(embeds=embed, ephemeral=True)
    
async def success(ctx, message):
    embed = interactions.Embed(
            title=lang['success'],
            description=message,
            footer=EMBED_FOOTER,
            color=int(config['embeds']['colors']['success'], base=16)
        )
    await ctx.send(embeds=embed, ephemeral=True)

async def failure(ctx, message):
    embed = interactions.Embed(
            title=lang['error'],
            description=message,
            footer=EMBED_FOOTER,
            color=int(config['embeds']['colors']['error'], base=16)
        )
    await ctx.send(embeds=embed, ephemeral=True)
    
loadConfigs()

def save_config():
    with open('config.json', 'w') as json_file:
        json.dump(config, json_file)

# Declare variables
BOT_TOKEN = config['BOT_TOKEN']
DEFAULT_GUILD_ID = int(config['DEFAULT_GUILD_ID'])
EMBED_FOOTER = interactions.EmbedFooter(text=config['embeds']['footer'], icon_url=config['embeds']['thumbnail'])

bot=interactions.Client(
    token=BOT_TOKEN,
    default_scope=DEFAULT_GUILD_ID
    )



# Reload config command
@bot.command(default_member_permissions=interactions.Permissions.MANAGE_GUILD)
async def reload(ctx: interactions.CommandContext):
    """Commande permettant de recharger les fichiers JSON"""
    if(ctx.author.id in config['whitelist']):
        loadConfigs()
        await success(ctx,lang['reload']['success'])
    else:
        await noPermission(ctx)

@bot.command(default_member_permissions=interactions.Permissions.MANAGE_GUILD)
async def stop(ctx: interactions.CommandContext):
    """Commande permettant de stopper le processus du bot"""
    if(ctx.author.id in config['whitelist']):
        await success(ctx,lang['stop']['success'])
        sys.exit(0)
    else:
        await noPermission(ctx)
             
             
             
@bot.command(default_member_permissions=interactions.Permissions.MANAGE_ROLES)
async def whitelist(ctx: interactions.CommandContext):
    """Commande de base pour la gestion des administrateurs"""
    pass

@whitelist.subcommand()
@interactions.option(interactions.OptionType.USER, name='utilisateur', description=lang['whitelist']['add']['description'], required=True)
async def add(ctx: interactions.CommandContext, utilisateur: interactions.Member):
    """Ajoute un utilisateur à la liste des administrateurs"""
    if(ctx.author.id in config['whitelist']):
        if(utilisateur.id in config['whitelist']):
            await failure(ctx, lang['whitelist']['add']['exists'].replace('{user}', utilisateur.mention))
        else:
            try:
                config['whitelist'].append(int(utilisateur.id))
                save_config()
                await success(ctx,lang['whitelist']['add']['success'].replace('{user}', utilisateur.mention))
            except Exception as e:
                await failure(ctx,lang['whitelist']['add']['failure'].replace('{user}', utilisateur.mention).replace('{error}', str(e)))
    else:
        await noPermission(ctx)
              
@whitelist.subcommand()
@interactions.option(interactions.OptionType.USER, name='utilisateur', description=lang['whitelist']['remove']['description'], required=True)
async def remove(ctx: interactions.CommandContext, utilisateur: interactions.Member):
    """Supprime un utilisateur de la liste blanche"""
    if(ctx.author.id in config['whitelist']):
        if(utilisateur.id in config['whitelist']):
            try:
                config['whitelist'].remove(int(utilisateur.id))
                save_config()
                await success(ctx,lang['whitelist']['remove']['success'].replace('{user}', utilisateur.mention))
            except Exception as e:
                await failure(ctx, lang['whitelist']['remove']['failure'].replace('{user}', utilisateur.mention).replace('{error}', str(e)))
        else:
            await failure(ctx, lang['whitelist']['remove']['not_found'].replace('{user}', utilisateur.mention))
    else:
        await noPermission(ctx)
    
@whitelist.subcommand()
async def list(ctx: interactions.CommandContext):
    """Donne une liste des utilisateurs dans la liste blanche"""
    if(ctx.author.id in config['whitelist']):
        userList = ""
        for user in config['whitelist']:
            userList += "<@" + str(user) + ">\n"
        embed = interactions.Embed(
            title=lang['whitelist']['title'],
            description="Voici la liste blanche :\n" + userList,
            footer=EMBED_FOOTER,
            color=int(config['embeds']['colors']['success'], base=16)
        )
        await ctx.send(embeds=embed, ephemeral=True)
    else:
        await noPermission(ctx)


ticketOptions = []
for category in lang['tickets']['panel']['categories']:
    option = interactions.SelectOption(
            label=lang['tickets']['panel']['categories'][category]['title'],
            value=lang['tickets']['panel']['categories'][category]['value'],
            description=lang['tickets']['panel']['categories'][category]['description']
        )
    ticketOptions.append(option)
ticketChoice = interactions.SelectMenu(
    custom_id='ticketChoice',
    placeholder=lang['tickets']['panel']['choicePlaceholder'],
    min_values=1,
    max_values=1,
    disabled=False,
    options=ticketOptions
)



    
@bot.component("ticketChoice")
async def select_response(ctx: interactions.ComponentContext):
    await ctx.send(ctx.value)
    


@bot.command(default_member_permissions=interactions.Permissions.MANAGE_GUILD)
@interactions.option(interactions.OptionType.STRING, name='type', description=lang['settings']['menu']['description'], required=True, choices=[interactions.Choice(name="Statut des serveurs",value="status"), interactions.Choice(name="Choix des notifications",value="roles"), interactions.Choice(name="Création de ticket",value="ticket")])
async def init_message(ctx: interactions.CommandContext, type: str):
    """Commande permettant d'initialiser les embeds d'interaction"""
    if(ctx.author.id in config['whitelist']):
        if(type == 'status'):
            #Do something
            pass
        elif(type == 'roles'):
            #Do something
            pass
        elif(type == 'ticket'):
            try:
                embed = interactions.Embed(
                    title=lang['tickets']['panel']['title'],
                    description="\n".join(lang['tickets']['panel']['description']),
                    footer=EMBED_FOOTER,
                    color=int(config['embeds']['colors']['primary'], base=16)
                )
                embed.set_thumbnail(url=config['embeds']['thumbnail'])
                panelID = await ctx.channel.send(embeds=embed, components=ticketChoice)
                config['tickets']['panel_id'] = int(panelID.id)
                config['tickets']['panel_channel_id'] = int(ctx.channel.id)
                save_config()
                await success(ctx,lang['tickets']['published'])
            except Exception as e:
                await failure(ctx, lang['tickets']['error'].replace('{error}', str(e)))               
        else:
            #Display error
            pass
    else:
        await noPermission(ctx)
        

bot.start()