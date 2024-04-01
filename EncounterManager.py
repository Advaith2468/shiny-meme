import threading
import time
import math
import discord
import re
from discord import Webhook, AsyncWebhookAdapter, Embed, EmbedField, EmbedAuthor, Color
from discord.ext import tasks
from aiohttp import ClientSession
from datetime import datetime, timedelta
from typing import List, Dict
from POGOProtos.Rpc import EncounterOutProto, PokemonProto
from PolygonStats.Configuration import ConfigurationManager
from PolygonStats.MySQLConnectionManager import MySQLConnectionManager
from PolygonStats.MySQLContext import MySQLContext
from PolygonStats.HoloPokemonId import HoloPokemonId

class EncounterManager:
    def __init__(self):
        self.clean_timer = None
        self.consumer_thread = None
        self.connection_manager = MySQLConnectionManager()
        self.blocking_encounter_queue = []
        self.already_send_encounters = {}
        self.lock_obj = threading.Lock()

        if not ConfigurationManager.Shared.Config.Encounter.Enabled:
            return

        self.clean_timer = threading.Timer(0, self.do_clean_timer)
        self.clean_timer.start()

        self.consumer_thread = threading.Thread(target=self.encounter_consumer)
        self.consumer_thread.start()

    def __del__(self):
        if self.clean_timer:
            self.clean_timer.cancel()
        if self.consumer_thread:
            self.consumer_thread.join()

    def do_clean_timer(self):
        with self.lock_obj:
            delete_encounters = [key for key, value in self.already_send_encounters.items() if value < datetime.now() - timedelta(minutes=20)]
            for id in delete_encounters:
                del self.already_send_encounters[id]

        if ConfigurationManager.Shared.Config.MySql.Enabled and ConfigurationManager.Shared.Config.Encounter.SaveToDatabase:
            with self.connection_manager.get_context() as context:
                context.execute("DELETE FROM `Encounter` WHERE `timestamp` < DATE_SUB( CURRENT_TIME(), INTERVAL 20 MINUTE)")

    def add_encounter(self, encounter):
        if not ConfigurationManager.Shared.Config.Encounter.Enabled:
            return
        self.blocking_encounter_queue.append(encounter)

    def encounter_consumer(self):
        while True:
            encounter_list = []
            if ConfigurationManager.Shared.Config.MySql.Enabled and ConfigurationManager.Shared.Config.Encounter.SaveToDatabase:
                with MySQLContext() as context:
                    while len(self.blocking_encounter_queue) > 0:
                        encounter = self.blocking_encounter_queue.pop(0)
                        if encounter.Pokemon.EncounterId in self.already_send_encounters:
                            continue
                        with self.lock_obj:
                            self.already_send_encounters[encounter.Pokemon.EncounterId] = datetime.now()
                        encounter_list.append(encounter)
                        self.connection_manager.add_encounter_to_database(encounter, context)
                    context.save_changes()
            else:
                while len(self.blocking_encounter_queue) > 0:
                    encounter = self.blocking_encounter_queue.pop(0)
                    if encounter.Pokemon.EncounterId in self.already_send_encounters:
                        continue
                    with self.lock_obj:
                        self.already_send_encounters[encounter.Pokemon.EncounterId] = datetime.now()
                    encounter_list.append(encounter)

            if len(encounter_list) > 0:
                for hook in ConfigurationManager.Shared.Config.Encounter.DiscordWebhooks:
                    self.send_discord_webhooks(hook, encounter_list)
                time.sleep(3)
            time.sleep(1)

    async def send_discord_webhooks(self, webhook, encounter_list):
        embeds = []
        for encounter in encounter_list:
            pokemon = encounter.Pokemon.Pokemon
            if webhook.FilterByIV:
                if webhook.OnlyEqual:
                    if pokemon.IndividualAttack != webhook.MinAttackIV:
                        continue
                    if pokemon.IndividualDefense != webhook.MinDefenseIV:
                        continue
                    if pokemon.IndividualStamina != webhook.MinStaminaIV:
                        continue
                else:
                    if pokemon.IndividualAttack < webhook.MinAttackIV:
                        continue
                    if pokemon.IndividualDefense < webhook.MinDefenseIV:
                        continue
                    if pokemon.IndividualStamina < webhook.MinStaminaIV:
                        continue
            if webhook.FilterByLocation:
                if self.distance_to(webhook.Latitude, webhook.Longitude, encounter.Pokemon.Latitude, encounter.Pokemon.Longitude) > webhook.DistanceInKm:
                    continue
            if webhook.FilterByShiny:
                if pokemon.PokemonDisplay.Shiny != webhook.IsShiny:
                    continue
            custom_link = ""
            if webhook.CustomLink:
                custom_link = f"[{webhook.CustomLink.Title}]({self.get_replaced_custom_link(webhook.CustomLink.Link, encounter)})"
            eb = Embed(
                title=f"Level {self.get_pokemon_level(pokemon.CpMultiplier)} {pokemon.PokemonId.name} (#{int(pokemon.PokemonId)})",
                author=EmbedAuthor(
                    name=f"{round(encounter.Pokemon.Latitude, 5)}, {round(encounter.Pokemon.Longitude, 5)}"
                ),
                thumbnail=self.get_pokemon_image_url(pokemon.PokemonId),
                fields=[
                    EmbedField(
                        name="Stats",
                        value=f"CP: {pokemon.Cp}\nIVs:{pokemon.IndividualAttack}/{pokemon.IndividualDefense}/{pokemon.IndividualStamina} | {self.get_iv(pokemon.IndividualAttack, pokemon.IndividualDefense, pokemon.IndividualStamina)}%"
                    ),
                    EmbedField(
                        name="Moves",
                        value=f"Fast: {self.format_move(pokemon.Move1.name)}\nCharge: {self.format_move(pokemon.Move2.name)}"
                    ),
                    EmbedField(
                        name="Links",
                        value=f"[Google Maps](https://maps.google.com/maps?q={round(encounter.Pokemon.Latitude, 5)},{round(encounter.Pokemon.Longitude, 5)}) [Apple Maps](http://maps.apple.com/?daddr={round(encounter.Pokemon.Latitude, 5)},{round(encounter.Pokemon.Longitude, 5)}) {custom_link}"
                    )
                ],
                color=Color.blue()
            )
            embeds.append(eb)

        if len(embeds) <= 0:
            return

        errors = 0
        was_sent = False
        while not was_sent and errors <= 5:
            try:
                async with ClientSession() as session:
                    webhook = Webhook.from_url(webhook.WebhookUrl, adapter=AsyncWebhookAdapter(session))
                    await webhook.send(embeds=embeds)
                    was_sent = True
            except Exception:
                errors += 1

    def get_replaced_custom_link(self, custom_link, encounter):
        link = custom_link.replace("{latitude}", str(round(encounter.Pokemon.Latitude, 5)))
        link = link.replace("{longitude}", str(round(encounter.Pokemon.Longitude, 5)))
        link = link.replace("{encounterId}", str(encounter.Pokemon.EncounterId))
        return link

    def get_pokemon_image_url(self, pokemon):
        if pokemon == HoloPokemonId.MrRime:
            return "https://img.pokemondb.net/sprites/go/normal/mr-rime.png"
        elif pokemon == HoloPokemonId.MrMime:
            return "https://img.pokemondb.net/sprites/bank/normal/mr-mime.png"
        elif pokemon == HoloPokemonId.MimeJr:
            return "https://img.pokemondb.net/sprites/bank/normal/mime-jr.png"
        else:
            return f"https://img.pokemondb.net/sprites/bank/normal/{pokemon.name.lower().replace('female', '-f').replace('male', '-m')}.png"

    def get_pokemon_level(self, cp_multiplier):
        if cp_multiplier < 0.734:
            pokemon_level = 58.35178527 * cp_multiplier * cp_multiplier - 2.838007664 * cp_multiplier + 0.8539209906
        else:
            pokemon_level = 171.0112688 * cp_multiplier - 95.20425243
        pokemon_level = (round(pokemon_level) * 2) / 2
        return pokemon_level

    def get_iv(self, atk, def_, sta):
        iv = ((atk + def_ + sta) / 45) * 100
        return round(iv, 1)

    def split_uppercase(self, input_):
        return re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])|(?<=[^A-Z])(?=[A-Z])', ' ', input_)

    def format_move(self, move):
        move = move.replace("Fast", "")
        return self.split_uppercase(move)

    def distance_to(self, lat1, lon1, lat2, lon2, unit='K'):
        rlat1 = math.pi * lat1 / 180
        rlat2 = math.pi * lat2 / 180
        theta = lon1 - lon2
        rtheta = math.pi * theta / 180
        dist = math.sin(rlat1) * math.sin(rlat2) + math.cos(rlat1) * math.cos(rlat2) * math.cos(rtheta)
        dist = math.acos(dist)
        dist = dist * 180 / math.pi
        dist = dist * 60 * 1.1515
        if unit == 'K':
            return dist * 1.609344
        elif unit == 'N':
            return dist * 0.8684
        elif unit == 'M':
            return dist
        return dist

    def dispose(self):
        if self.clean_timer:
            self.clean_timer.cancel()
        if self.consumer_thread:
            self.consumer_thread.join()
