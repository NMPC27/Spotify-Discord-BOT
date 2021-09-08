########################################################################
#																		 #
#	This work is copyright protected do not use/modify or distribute	 #
#	without the consent of the author									 #
#																		 #
#	copyright - Please if you want to distribute this product ask for	#
#	premission of the author											 #
#																		 #
#	Author: NMPC27 - https://github.com/NMPC27/Spotify-Discord-BOT		 #
#																		 #
#	Project based on: 													 #
#	https://github.com/stuyy/Lavalink-Discordpy-Example					 #
#																		 #
########################################################################

import os
import discord
from discord import utils
from discord import Embed
from discord.ext import tasks, commands
import time
import lavalink
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


with open('config.txt') as f:
	data = f.read()
  
js = json.loads(data)

os.environ["SPOTIPY_CLIENT_ID"] = js["SPOTIPY_CLIENT_ID"]	
os.environ["SPOTIPY_CLIENT_SECRET"] = js["SPOTIPY_CLIENT_SECRET"]
os.environ["SPOTIPY_REDIRECT_URI"] = js["SPOTIPY_REDIRECT_URI"]	

scope = "user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

os.system('start "START Lavalink" cmd /k "java -jar Lavalink.jar"')

bot = commands.Bot(command_prefix=".")
bot.remove_command('help')

########################################################################


@bot.event
async def on_ready():
	print(f'{bot.user} has logged in.')
	bot.add_cog(MusicCog(bot))
	
class MusicCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.music = lavalink.Client(self.bot.user.id)
		self.bot.music.add_node('localhost', 7000, 'youshallnotpass', 'na', 'music-node')
		self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
		self.bot.music.add_event_hook(self.track_hook)
		self.musica_disc=""
		self.play_disc=False
		self.spotify.start()

	
	@commands.command(name='help')
	async def help(self, ctx):
		await ctx.channel.send("```List of commands: \n .help -> it shows a list of usefull commands \n .play XXX -> it will play the name of the song or Youtube link put in XXX \n .pause -> pauses the current song \n .stop -> stop the current song ```")


	@commands.command(name='join')
	async def join(self, ctx):
		print('join command worked')
		global ctx_g
		ctx_g=ctx
		member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
		if member is not None and member.voice is not None:
			vc = member.voice.channel
			player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
			if not player.is_connected:
				player.store('channel', ctx.channel.id)
				await self.connect_to(ctx.guild.id, str(vc.id))
							 
	@commands.command(name='pause')
	async def pause(self, ctx):
		print("PAUSE")
		player = self.bot.music.player_manager.get(ctx.guild.id)
		if not player.paused:
			await player.set_pause(True)
		
	@commands.command(name='resume')
	async def resume(self, ctx):
		print("PLAY")
		player = self.bot.music.player_manager.get(ctx.guild.id)
		if player.paused:
			await player.set_pause(False)
			
	@commands.command(name='stop')
	async def stop(self, ctx):
		print("STOP")
		player = self.bot.music.player_manager.get(ctx.guild.id)
		await player.stop()

	@commands.command(name='play')
	async def play(self, ctx, *, query):
		try:
			player = self.bot.music.player_manager.get(ctx.guild.id)
			query = f'ytsearch:{query}'
			results = await player.node.get_tracks(query)
			track = results['tracks'][0]

			print("playing "+track["info"]["title"]+" in Discord | YOUTUBE SONG")
			
			await player.stop()
			
			await ctx.channel.send(track["info"]["title"]+" - "+track["info"]["uri"])

			player.add(requester=ctx.author.id, track=track)
			if not player.is_playing:
				await player.play()

		except Exception as error:
			print(error)
	
	async def track_hook(self, event):
		x=0
			
	async def connect_to(self, guild_id: int, channel_id: str):
		ws = self.bot._connection._get_websocket(guild_id)
		await ws.voice_state(str(guild_id), channel_id)
		
	@tasks.loop(seconds=1.0)
	async def spotify(self):
		dick=sp.current_user_playing_track()
			
		try:
			if(ctx_g==0):
				x=0		 	
			if dick==None:
				print("SPOTIFY IS OFF")			
			else:
				try:
					if(dick["item"]["is_local"]):#local song
						if(self.musica_disc==dick["item"]["name"]):
							if(dick["is_playing"]):										
								if(self.play_disc!=dick["is_playing"]):						
									print("PLAY")		
									player = self.bot.music.player_manager.get(ctx_g.guild.id)
									if player.paused:
										await player.set_pause(False)		
							else:														
								if(self.play_disc!=dick["is_playing"]):
									print("PAUSE")
									player = self.bot.music.player_manager.get(ctx_g.guild.id)
									if not player.paused:
										await player.set_pause(True)
							
						else:
							musica=dick["item"]["name"]
							print("playing "+musica+" in Discord ## LOCAL SONG")
							
							player = self.bot.music.player_manager.get(ctx_g.guild.id)
							await player.stop()
							
							try:
								player = self.bot.music.player_manager.get(ctx_g.guild.id)
								query = f'ytsearch:{musica}'
								results = await player.node.get_tracks(query)
								track = results['tracks'][0]
				
								await ctx_g.channel.send(track["info"]["title"]+" - "+track["info"]["uri"])

								player.add(requester=ctx_g.author.id, track=track)
								if not player.is_playing:
									await player.play()

							except Exception as error:
								print(error)
						
						self.musica_disc=dick["item"]["name"]
						self.play_disc=dick["is_playing"]
					else:#online song
						if(self.musica_disc==dick["item"]["external_urls"]["spotify"]):
							if(dick["is_playing"]):										
								if(self.play_disc!=dick["is_playing"]):						
									print("PLAY")		
									player = self.bot.music.player_manager.get(ctx_g.guild.id)
									if player.paused:
										await player.set_pause(False)		
							else:														
								if(self.play_disc!=dick["is_playing"]):
									print("PAUSE")
									player = self.bot.music.player_manager.get(ctx_g.guild.id)
									if not player.paused:
										await player.set_pause(True)
							
						else:
							musica=dick["item"]["name"]
							print("playing "+musica+" in Discord ## ONLINE SONG")

							for i in range(len(dick["item"]["artists"])):
								musica=musica+" "+dick["item"]["artists"][i]["name"]
							
							player = self.bot.music.player_manager.get(ctx_g.guild.id)
							await player.stop()
							
							try:
								player = self.bot.music.player_manager.get(ctx_g.guild.id)
								query = f'ytsearch:{musica}'
								results = await player.node.get_tracks(query)
								track = results['tracks'][0]
				
								await ctx_g.channel.send(track["info"]["title"]+" - "+track["info"]["uri"])

								player.add(requester=ctx_g.author.id, track=track)
								if not player.is_playing:
									await player.play()

							except Exception as error:
								print(error)
						
						self.musica_disc=dick["item"]["external_urls"]["spotify"]
						self.play_disc=dick["is_playing"]
												
				except:
					print("playing AD")
		except:
			print("Use .join command")


bot.run(js["TOKEN"])
