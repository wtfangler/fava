"""Generates the extra optional TEMPERED quests (source of truth for 42 era quests + the Epilog branch).

  python tools/gen_more_quests.py [--registries <dir with reports262 / reports263 out/reports>]

Writes into src/tempered:
  data/tempered/advancement/bonus/<era>/<id>.json   (+3 per era, on top of the original 21 by Codex)
  data/tempered/advancement/bonus/epilog/*.json     (hidden root unlocked by killing the dragon + the Epilog quests)
  assets/tempered/lang/{pl_pl,en_us}.json           (keys appended, existing ones untouched)
  data/tempered/function/core/reset_bonus.mcfunction (revoke lines for every optional quest)
Schema is the verified 26.2 one; tools/build_tempered.py converts it for 26.3.
Every item/block/entity/potion/effect id is checked against the official registries of both versions.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "tempered"
ADV = SRC / "data" / "tempered" / "advancement" / "bonus"
LANG = SRC / "assets" / "tempered" / "lang"
RESET = SRC / "data" / "tempered" / "function" / "core" / "reset_bonus.mcfunction"
OPT_PL, OPT_EN = "(Opcjonalne, osobiste) ", "(Optional, personal) "
EPILOG = "tempered:bonus/epilog/root"


# ------------------------------------------------------------------ criteria builders (26.2 schema)
def gate(adv):
    return [{"condition": "minecraft:entity_properties", "entity": "this",
             "predicate": {"minecraft:type_specific/player": {"advancements": {adv: True}}}}]


def entity(ent):
    return [{"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"minecraft:entity_type": ent}}]


class C:
    """One criterion: (name, trigger, conditions, ids-to-validate)."""

    def __init__(self, name, trigger, cond, check=()):
        self.name, self.trigger, self.cond, self.check = name, trigger, cond, check


def placed(block):
    return C("placed_" + block, "minecraft:placed_block",
             {"location": [{"condition": "minecraft:location_check", "predicate": {"block": {"blocks": "minecraft:" + block}}}]},
             [("block", block)])


def have(item, count=None):
    spec = {"items": "minecraft:" + item}
    if count:
        spec["count"] = {"min": count}
    return C("has_" + item, "minecraft:inventory_changed", {"items": [spec]}, [("item", item)])


def eat(item):
    return C("ate_" + item, "minecraft:consume_item", {"item": {"items": "minecraft:" + item}}, [("item", item)])


def killed(ent):
    return C("killed_" + ent, "minecraft:player_killed_entity", {"entity": entity("minecraft:" + ent)}, [("entity", ent)])


def bred(ent):
    return C("bred_" + ent, "minecraft:bred_animals", {"child": entity("minecraft:" + ent)}, [("entity", ent)])


def tamed(ent):
    return C("tamed_" + ent, "minecraft:tame_animal", {"entity": entity("minecraft:" + ent)}, [("entity", ent)])


def summoned(ent):
    return C("summoned_" + ent, "minecraft:summoned_entity", {"entity": entity("minecraft:" + ent)}, [("entity", ent)])


def brewed(potion):
    return C("brewed_" + potion, "minecraft:brewed_potion", {"potion": "minecraft:" + potion}, [("potion", potion)])


def bucket(item):
    return C("bucket_" + item, "minecraft:filled_bucket", {"item": {"items": "minecraft:" + item}}, [("item", item)])


def structure(sid):
    return C("visited_" + sid, "minecraft:location",
             {"player": None, "_loc": sid}, [("structure", sid)])


PLAIN = {
    "crossbow": C("shot_crossbow", "minecraft:shot_crossbow", {}),
    "trade": C("traded", "minecraft:villager_trade", {}),
    "cure": C("cured_villager", "minecraft:cured_zombie_villager", {}),
    "totem": C("used_totem", "minecraft:used_totem", {"item": {"items": "minecraft:totem_of_undying"}}),
    "lightning": C("channeled", "minecraft:channeled_lightning", {}),
    "sculk": C("near_catalyst", "minecraft:kill_mob_near_sculk_catalyst", {}),
    "hero": C("hero", "minecraft:hero_of_the_village", {}),
    "beacon4": C("full_beacon", "minecraft:construct_beacon", {"level": 4}),
    "enchant15": C("enchanted", "minecraft:enchanted_item", {"levels": {"min": 15}}, []),
    "enchant30": C("enchanted30", "minecraft:enchanted_item", {"levels": {"min": 30}}, []),
    "end_ship_loot": C("loot", "minecraft:player_generates_container_loot", {"loot_table": "minecraft:chests/end_city_treasure"}),
    "cocktail": C("effects", "minecraft:effects_changed",
                  {"effects": {"minecraft:speed": {}, "minecraft:strength": {}, "minecraft:regeneration": {}}}, []),
}
EFFECTS_USED = ["speed", "strength", "regeneration"]

# ------------------------------------------------------------------ quest catalogue
# (era, id, icon, frame, xp, criteria | [[alternatives]], (title_pl, desc_pl), (title_en, desc_en))
# `any` groups: a tuple of criteria in a list is an OR group; plain items are AND.
Q = []


def quest(era, qid, icon, xp, crit, pl, en, frame="task"):
    Q.append(dict(era=era, id=qid, icon=icon, xp=xp, crit=crit, pl=pl, en=en, frame=frame))


# --- era 1 :: wood
quest(1, "loyal_companion", "bone", 10, [[tamed("wolf"), tamed("cat")]],
      ("Wierny towarzysz", "Oswój wilka albo kota. Towarzysz przyda się w drodze i w domu."),
      ("A loyal companion", "Tame a wolf or a cat. A friend for the road and for home."))
quest(1, "supply_chests", "barrel", 10, [placed("chest"), placed("barrel")],
      ("Spiżarnia na zapasy", "Ustaw skrzynię i beczkę. Porządek w zapasach to połowa przetrwania."),
      ("Pantry for supplies", "Place a chest and a barrel. Tidy supplies are half of survival."))
quest(1, "forest_dessert", "sweet_berries", 10, [eat("apple"), eat("sweet_berries")],
      ("Leśny deser", "Zjedz jabłko i słodkie jagody. Natura potrafi poczęstować."),
      ("Forest dessert", "Eat an apple and sweet berries. Nature can be generous."))
# --- era 2 :: stone
quest(2, "smoke_chimney", "smoker", 15, [placed("furnace"), placed("smoker")],
      ("Dym z komina", "Ustaw piec i wędzarnię. Kuchnia domu zaczyna pachnieć."),
      ("Smoke from the chimney", "Place a furnace and a smoker. Home starts to smell like a kitchen."))
quest(2, "window_on_world", "glass_pane", 15, [placed("glass"), placed("glass_pane")],
      ("Okno na świat", "Ustaw blok szkła i szybkę. Dom zyskuje widok."),
      ("A window on the world", "Place a glass block and a glass pane. Your home gets a view."))
quest(2, "compost_corner", "composter", 15, [placed("composter"), placed("flower_pot")],
      ("Zielony zakątek", "Ustaw kompostownik i doniczkę. Mały ogród przy domu."),
      ("Green corner", "Place a composter and a flower pot. A small garden by the house."))
# --- era 3 :: iron
quest(3, "blacksmith", "anvil", 20, [placed("anvil"), placed("smithing_table")],
      ("Kowal z powołania", "Ustaw kowadło i stół kowalski. Warsztat na lata."),
      ("A born blacksmith", "Place an anvil and a smithing table. A workshop for years."))
quest(3, "barter_day", "emerald", 20, [PLAIN["trade"]],
      ("Dzień targowy", "Dobij targu z wieśniakiem. Handel to początek przyjaźni."),
      ("Market day", "Make a trade with a villager. Trade is the start of friendship."))
quest(3, "iron_guardian", "iron_block", 25, [summoned("iron_golem")],
      ("Żelazny strażnik", "Zbuduj żelaznego golema. Dom pod ochroną."),
      ("Iron guardian", "Build an iron golem. Your home under guard."))
# --- era 4 :: diamond
quest(4, "enchanter_apprentice", "enchanting_table", 25, [PLAIN["enchant15"]],
      ("Uczeń zaklinacza", "Zaklnij przedmiot za co najmniej 15 poziomów. Pierwszy poważny krok w magii."),
      ("Enchanter's apprentice", "Enchant an item at level 15 or higher. A first serious step into magic."))
quest(4, "swift_potion", "potion", 25, [brewed("strong_swiftness")],
      ("Szybki jak wiatr", "Uwarz miksturę silnej szybkości. Każda sekunda na wyprawie się liczy."),
      ("Swift as the wind", "Brew a potion of strong swiftness. Every second counts on an expedition."))
quest(4, "village_doctor", "golden_apple", 25, [PLAIN["cure"]],
      ("Lekarz wsi", "Wylecz zombie-wieśniaka. Wioska to zapamięta."),
      ("Village doctor", "Cure a zombie villager. The village will remember."))
# --- era 5 :: nether
quest(5, "nether_garden", "nether_wart", 25, [placed("nether_wart")],
      ("Piekielny ogród", "Zasadź nasiona nether wartu. Warzelnia mikstur potrzebuje własnych zbiorów."),
      ("Infernal garden", "Plant nether wart. A brewing stand needs its own harvest."))
quest(5, "blaze_hunter", "blaze_rod", 25, [killed("blaze")],
      ("Łowca płomyków", "Pokonaj płomyka. Pręty przydadzą się w warzelni."),
      ("Blaze hunter", "Defeat a blaze. The rods will serve the brewing stand."))
quest(5, "ghost_tears", "ghast_tear", 25, [have("ghast_tear")],
      ("Łzy ducha", "Zdobądź łzę ghasta. Z niej powstają kryształy i mikstury."),
      ("Ghost tears", "Obtain a ghast tear. It makes crystals and potions."))
# --- era 6 :: end
quest(6, "shulker_hunter", "shulker_shell", 30, [killed("shulker")],
      ("Łowca szulkerów", "Pokonaj szulkera. Skorupy przydadzą się w bazie."),
      ("Shulker hunter", "Defeat a shulker. The shells will serve your base."))
quest(6, "dragon_bottle", "dragon_breath", 30, [have("dragon_breath")],
      ("Smoczy oddech w butelce", "Zbierz oddech smoka do butelki. Przyda się do mikstur."),
      ("Dragon's breath in a bottle", "Collect dragon's breath in a bottle. Useful for potions."))
quest(6, "pearl_stock", "ender_pearl", 20, [have("ender_pearl", 16)],
      ("Zapas pereł", "Miej jednocześnie 16 pereł Endu. Szybkie przeprawy na każdą wyprawę."),
      ("Pearl stock", "Carry 16 ender pearls at once. Quick crossings on every expedition."))
# --- era 7 :: post-end
quest(7, "full_beacon", "beacon", 30, [PLAIN["beacon4"]],
      ("Pełna latarnia", "Zbuduj w pełni zasilany beacon (cztery poziomy piramidy). Światło widać z daleka."),
      ("Full beacon", "Build a fully powered beacon (four pyramid levels). The light shows from afar."))
quest(7, "second_life", "totem_of_undying", 25, [PLAIN["totem"]],
      ("Drugie życie", "Uratuj się totemem nieśmiertelności. Dobrze mieć zapas."),
      ("A second life", "Save yourself with a totem of undying. Always carry a spare."))
quest(7, "storm_caller", "trident", 30, [PLAIN["lightning"]],
      ("Władca burzy", "Przywołaj piorun trójzębem z urokiem przywołania. Wymaga burzy."),
      ("Storm caller", "Channel lightning with a trident. Needs a thunderstorm."))

# --- epilog (after the Ender Dragon): optional quests
E = "epilog"
quest(E, "rocket_stock", "firework_rocket", 30, [have("firework_rocket", 64)],
      ("Zapas rakiet", "Miej w ekwipunku pełny stos rakiet: 64 sztuki. Daleki lot nie lubi niespodzianek."),
      ("Rocket stock", "Carry a full stack of 64 rockets. Long flights hate surprises."))
quest(E, "sky_ship", "purpur_block", 60, [PLAIN["end_ship_loot"]],
      ("Okręt na niebie", "Otwórz skrzynię ze skarbem w statku z End City."),
      ("A ship in the sky", "Open the treasure chest on an End City ship."), "goal")
quest(E, "wings", "elytra", 50, [have("elytra")],
      ("Skrzydła", "Zdobądź elytrę. Świat widziany z góry wygląda inaczej."),
      ("Wings", "Obtain an elytra. The world looks different from above."), "goal")
quest(E, "navigator_kit", "recovery_compass", 30, [have("compass"), have("clock"), have("recovery_compass")],
      ("Zestaw nawigatora", "Zdobądź kompas, zegarek i kompas odzyskiwania. Nie zgubisz drogi ani czasu."),
      ("Navigator's kit", "Obtain a compass, a clock and a recovery compass. Lose neither way nor time."))
quest(E, "warden_down", "sculk_shrieker", 200, [killed("warden")],
      ("Koniec ciszy", "Pokonaj strażnika (Warden). Najgroźniejszy mieszkaniec głębin."),
      ("The silence ends", "Defeat a Warden. The deadliest dweller of the deep."), "challenge")
quest(E, "elder_down", "prismarine_shard", 120, [killed("elder_guardian")],
      ("Starszy strażnik", "Pokonaj starszego strażnika z monumentu oceanicznego."),
      ("Elder guardian", "Defeat an elder guardian from an ocean monument."), "challenge")
quest(E, "creaking_down", "creaking_heart", 60, [killed("creaking")],
      ("Cichy ruch", "Pokonaj skrzypiącego. Nie patrz, a nie ruszy."),
      ("Quiet movement", "Defeat a creaking. Do not look and it will not move."), "goal")
quest(E, "breeze_down", "wind_charge", 50, [killed("breeze")],
      ("Wiatr ucichł", "Pokonaj wichra w komnatach prób."),
      ("The wind calms", "Defeat a breeze in the trial chambers."), "goal")
quest(E, "catalyst_kill", "sculk_catalyst", 50, [PLAIN["sculk"]],
      ("Sculk się syci", "Zabij moba przy katalizatorze sculku."),
      ("Sculk feeds", "Kill a mob near a sculk catalyst."), "goal")
quest(E, "brute_down", "golden_axe", 50, [killed("piglin_brute")],
      ("Brutalna brama", "Pokonaj brutala piglinów w bastionie."),
      ("Brutal gate", "Defeat a piglin brute in a bastion."), "goal")
quest(E, "village_hero", "white_banner", 80, [PLAIN["hero"]],
      ("Bohater wsi", "Obroń wioskę przed najazdem i zostań jej bohaterem."),
      ("Hero of the village", "Defend a village from a raid and become its hero."), "goal")
quest(E, "cat_friends", "cod", 25, [tamed("cat")],
      ("Kocia ferajna", "Oswój kota. Dom bez kota jest pusty."),
      ("Cat friends", "Tame a cat. A home without a cat is empty."))
quest(E, "wolf_pack", "bone", 25, [tamed("wolf")],
      ("Wilcza wataha", "Oswój wilka. Wierny towarzysz na wyprawy."),
      ("Wolf pack", "Tame a wolf. A faithful companion for expeditions."))
quest(E, "parrot_shoulder", "feather", 25, [tamed("parrot")],
      ("Papuga na ramieniu", "Oswój papugę. Żegluga bez papugi to nie żegluga."),
      ("Parrot on the shoulder", "Tame a parrot. Sailing without one is no sailing."))
quest(E, "stable_family", "saddle", 30, [bred("horse")],
      ("Rodzinna stajnia", "Doprowadź do narodzin źrebaka."),
      ("A family stable", "Breed a foal."))
quest(E, "apiary_dynasty", "honeycomb", 30, [bred("bee")],
      ("Pszczela dynastia", "Rozmnóż pszczoły."),
      ("Bee dynasty", "Breed bees."))
quest(E, "armadillo_burrow", "armadillo_scute", 30, [bred("armadillo")],
      ("Pancerna rodzina", "Rozmnóż pancernik."),
      ("Armored family", "Breed armadillos."))
quest(E, "pond_family", "frogspawn", 30, [bred("frog")],
      ("Rodzina znad stawu", "Rozmnóż żaby."),
      ("Family from the pond", "Breed frogs."))
quest(E, "sniffer_pair", "torchflower_seeds", 60, [bred("sniffer")],
      ("Para węszycieli", "Rozmnóż węszyciela. Prastare rośliny wracają do świata."),
      ("A pair of sniffers", "Breed sniffers. Ancient plants return to the world."), "goal")
quest(E, "treasury", "netherite_block", 60, [placed(b) for b in (
      "iron_block", "gold_block", "diamond_block", "emerald_block", "netherite_block", "copper_block", "lapis_block", "redstone_block")],
      ("Skarbiec", "Ustaw bloki żelaza, złota, diamentu, szmaragdu, netherytu, miedzi, lapis lazuli i redstone. Pokaż, co zdobyłeś."),
      ("The treasury", "Place blocks of iron, gold, diamond, emerald, netherite, copper, lapis lazuli and redstone. Show what you earned."), "goal")
quest(E, "winter_garden", "flowering_azalea", 40, [placed(b) for b in ("flowering_azalea", "glow_lichen", "spore_blossom", "big_dripleaf")],
      ("Ogród zimowy", "Ustaw kwitnącą azalię, świetlisty porost, kwiat zarodników i duży liść kroplówki."),
      ("Winter garden", "Place a flowering azalea, glow lichen, a spore blossom and a big dripleaf."))
quest(E, "beacon_lights", "sea_lantern", 40, [placed(b) for b in ("sea_lantern", "shroomlight", "glowstone", "soul_lantern", "end_rod")],
      ("Latarnie dla zagubionych", "Ustaw morską latarnię, grzybnię świetlną, glowstone, duszną latarnię i pręt Endu."),
      ("Lights for the lost", "Place a sea lantern, shroomlight, glowstone, soul lantern and end rod."))
quest(E, "great_library", "chiseled_bookshelf", 30, [placed(b) for b in ("chiseled_bookshelf", "lectern", "bookshelf", "enchanting_table")],
      ("Wielka biblioteka", "Ustaw rzeźbioną biblioteczkę, pulpit, regał i stół zaklęć."),
      ("The great library", "Place a chiseled bookshelf, a lectern, a bookshelf and an enchanting table."))
quest(E, "world_hub", "lodestone", 50, [placed(b) for b in ("conduit", "lodestone", "respawn_anchor")],
      ("Węzeł światów", "Ustaw przewód, magnetyt i kotwicę odrodzenia. Punkt powrotu z każdego wymiaru."),
      ("World hub", "Place a conduit, a lodestone and a respawn anchor. A return point from every dimension."), "goal")
quest(E, "auto_works", "crafter", 40, [placed(b) for b in ("crafter", "hopper", "piston", "observer")],
      ("Automatyczna wytwórnia", "Ustaw wytwornicę, lej, tłok i obserwatora. Zacznij budować maszynę."),
      ("Automatic works", "Place a crafter, a hopper, a piston and an observer. Start building a machine."))
quest(E, "mechanic", "comparator", 30, [placed(b) for b in ("repeater", "comparator", "daylight_detector", "target")],
      ("Mechanik", "Ustaw przekaźnik, komparator, czujnik światła dziennego i tarczę."),
      ("The mechanic", "Place a repeater, a comparator, a daylight detector and a target block."))
quest(E, "apothecary", "brewing_stand", 50, [brewed("strength"), brewed("swiftness"), brewed("regeneration")],
      ("Apteka na wyprawę", "Uwarz mikstury siły, szybkości i regeneracji."),
      ("Expedition apothecary", "Brew potions of strength, swiftness and regeneration."), "goal")
quest(E, "grand_enchanter", "experience_bottle", 50, [PLAIN["enchant30"]],
      ("Wielki zaklinacz", "Zaklnij przedmiot na maksymalnym poziomie (30)."),
      ("Grand enchanter", "Enchant an item at the maximum level (30)."), "goal")
quest(E, "power_cocktail", "glowstone_dust", 60, [PLAIN["cocktail"]],
      ("Wielki koktajl", "Miej jednocześnie aktywne efekty szybkości, siły i regeneracji."),
      ("Power cocktail", "Have speed, strength and regeneration active at the same time."), "goal")
quest(E, "grand_explorer", "map", 100, [structure(s) for s in (
      "ancient_city", "trial_chambers", "bastion_remnant", "fortress", "end_city", "monument", "mansion")],
      ("Wielki odkrywca", "Odwiedź prastare miasto, komnaty prób, bastion, twierdzę Netheru, End City, monument oceaniczny i leśną rezydencję."),
      ("Grand explorer", "Visit an ancient city, trial chambers, a bastion, a nether fortress, an End City, an ocean monument and a woodland mansion."), "challenge")
quest(E, "jukebox_collector", "jukebox", 40, [have(d) for d in ("music_disc_13", "music_disc_cat", "music_disc_blocks", "music_disc_chirp")],
      ("Płyty z lochów", "Zdobądź płyty 13, cat, blocks i chirp."),
      ("Records from the dungeons", "Obtain the records 13, cat, blocks and chirp."))
quest(E, "skull_collection", "wither_skeleton_skull", 50, [have(h) for h in (
      "skeleton_skull", "zombie_head", "creeper_head", "piglin_head", "wither_skeleton_skull")],
      ("Kolekcja głów", "Zdobądź czaszkę szkieleta, głowę zombie, creepera, piglina i czaszkę wither szkieleta."),
      ("Head collection", "Obtain a skeleton skull and zombie, creeper and piglin heads plus a wither skeleton skull."), "goal")
quest(E, "dragon_egg", "dragon_egg", 100, [have("dragon_egg")],
      ("Smocze jajo", "Zdobądź jajo smoka. Trofeum, którego nie ma nikt, kto nie pokonał smoka."),
      ("Dragon egg", "Obtain the dragon egg. A trophy only dragon slayers own."), "challenge")
quest(E, "netherite_vault", "netherite_ingot", 80, [have("netherite_ingot", 9)],
      ("Skarbiec netherytu", "Miej jednocześnie dziewięć sztabek netherytu. Wystarczą na blok."),
      ("Netherite vault", "Carry nine netherite ingots at once. Enough for a block."), "challenge")
quest(E, "sea_lord", "trident", 60, [have("trident"), have("heart_of_the_sea")],
      ("Władca mórz", "Zdobądź trójząb i serce morza."),
      ("Lord of the seas", "Obtain a trident and a heart of the sea."), "goal")



# --- batch 2: three more quests per era and twenty more in the Epilog
# era 1 :: wood
quest(1, "roof_fence", "oak_fence", 10, [placed(b) for b in ("oak_stairs", "oak_slab", "oak_fence")],
      ("Dach i płot", "Ustaw drewniane schody, półblok i płot. Dom zaczyna wyglądać jak dom."),
      ("Roof and fence", "Place wooden stairs, a slab and a fence. A house starts to look like a house."))
quest(1, "sapling_garden", "oak_sapling", 10, [placed(b) for b in ("oak_sapling", "birch_sapling", "spruce_sapling")],
      ("Szkółka leśna", "Zasadź sadzonkę dębu, brzozy i świerku. Zadbaj o drewno na później."),
      ("Forest nursery", "Plant an oak, a birch and a spruce sapling. Look after your future timber."))
quest(1, "roast_meat", "cooked_chicken", 10, [eat("cooked_chicken"), eat("cooked_mutton")],
      ("Pieczone mięso", "Zjedz pieczonego kurczaka i pieczoną baraninę. Upiecz mięso w piecu lub na ognisku."),
      ("Roast meat", "Eat cooked chicken and cooked mutton. Use a furnace or a campfire."))
# era 2 :: stone
quest(2, "stone_wall", "cobblestone_wall", 15, [placed(b) for b in ("cobblestone_wall", "stone_brick_stairs", "stone_slab")],
      ("Kamienny mur", "Ustaw mur z bruku, schody z kamiennych cegieł i kamienny półblok."),
      ("Stone wall", "Place a cobblestone wall, stone brick stairs and a stone slab."))
quest(2, "first_ores", "raw_copper", 15, [have("coal"), have("raw_copper")],
      ("Pierwsze rudy", "Zdobądź węgiel i surową miedź. Pod ziemią czeka coś więcej niż kamień."),
      ("First ores", "Obtain coal and raw copper. There is more underground than stone."))
quest(2, "stone_workshop", "stonecutter", 15, [placed("stonecutter"), placed("grindstone")],
      ("Kamieniarnia", "Ustaw przecinarkę do kamienia i szlifierkę. Wygodniejsza obróbka materiałów."),
      ("Stone workshop", "Place a stonecutter and a grindstone. Easier crafting of materials."))
# era 3 :: iron
quest(3, "ironclad", "iron_chestplate", 25, [have(a) for a in ("iron_helmet", "iron_chestplate", "iron_leggings", "iron_boots")],
      ("W żelaznej zbroi", "Zdobądź hełm, napierśnik, nogawice i buty z żelaza."),
      ("Ironclad", "Obtain an iron helmet, chestplate, leggings and boots."))
quest(3, "sorting_room", "hopper", 20, [placed(b) for b in ("hopper", "dropper", "dispenser")],
      ("Sortownia", "Ustaw lej, podajnik i dozownik. Pierwsza automatyka w bazie."),
      ("Sorting room", "Place a hopper, a dropper and a dispenser. The first automation in your base."))
quest(3, "aquarium", "cod_bucket", 20, [bucket("cod_bucket"), bucket("salmon_bucket")],
      ("Akwarium", "Złap dorsza i łososia do wiadra. Ryby w domu."),
      ("Aquarium", "Catch a cod and a salmon in a bucket. Fish at home."))
# era 4 :: diamond
quest(4, "master_tools", "diamond_pickaxe", 25, [have(t) for t in ("diamond_pickaxe", "diamond_axe", "diamond_shovel")],
      ("Narzędzia mistrza", "Zdobądź diamentowy kilof, siekierę i łopatę."),
      ("Master's tools", "Obtain a diamond pickaxe, axe and shovel."))
quest(4, "crossbow_shot", "crossbow", 25, [PLAIN["crossbow"]],
      ("Strzał z kuszy", "Wystrzel z kuszy. Naładuj ją i trafiaj z daleka."),
      ("Crossbow shot", "Fire a crossbow. Load it and strike from afar."))
quest(4, "golden_snack", "golden_apple", 25, [eat("golden_apple")],
      ("Złota przekąska", "Zjedz złote jabłko. Warto mieć je na czarną godzinę."),
      ("Golden snack", "Eat a golden apple. Worth having for a rainy day."))
# era 5 :: nether
quest(5, "nether_bricks", "nether_bricks", 25, [placed(b) for b in ("nether_bricks", "nether_brick_fence", "red_nether_bricks")],
      ("Cegła z Netheru", "Ustaw cegły Netheru, płot z cegieł i czerwone cegły Netheru."),
      ("Nether brick", "Place nether bricks, a nether brick fence and red nether bricks."))
quest(5, "quartz_palace", "quartz_block", 25, [placed(b) for b in ("quartz_block", "quartz_pillar", "chiseled_quartz_block")],
      ("Kwarcowy pałac", "Ustaw blok kwarcu, filar i rzeźbiony blok kwarcu."),
      ("Quartz palace", "Place a quartz block, a quartz pillar and a chiseled quartz block."))
quest(5, "lava_bucket", "lava_bucket", 25, [bucket("lava_bucket")],
      ("Odwaga nad lawą", "Nabierz lawę do wiadra. Ostrożnie, ogień nie wybacza."),
      ("Courage above lava", "Fill a bucket with lava. Careful, fire does not forgive."))
# era 6 :: end
quest(6, "purpur_tower", "purpur_pillar", 30, [placed(b) for b in ("purpur_pillar", "purpur_stairs", "purpur_slab")],
      ("Purpurowa wieża", "Ustaw filar z purpuru, schody i półblok. Wieża godna Endu."),
      ("Purpur tower", "Place a purpur pillar, stairs and a slab. A tower worthy of the End."))
quest(6, "crystal_maker", "end_crystal", 30, [have("end_crystal")],
      ("Kryształy Endu", "Wytwórz kryształ Endu. Pamiętaj, że wybucha."),
      ("End crystals", "Craft an end crystal. Remember that it explodes."))
quest(6, "enderman_hunter", "ender_eye", 25, [killed("enderman")],
      ("Łowca endermanów", "Pokonaj endermana. Nie patrz mu w oczy."),
      ("Enderman hunter", "Defeat an enderman. Do not look it in the eyes."))
# era 7 :: post-end
quest(7, "music_hall", "jukebox", 25, [placed(b) for b in ("jukebox", "note_block", "bell")],
      ("Sala koncertowa", "Ustaw szafę grającą, blok dźwiękowy i dzwon. Zagraj coś w bazie."),
      ("Concert hall", "Place a jukebox, a note block and a bell. Play something at home."))
quest(7, "netherite_smith", "netherite_pickaxe", 30, [have("netherite_pickaxe")],
      ("Netherytowy kilof", "Wykuj netherytowy kilof na kowalskim stole."),
      ("Netherite pickaxe", "Forge a netherite pickaxe at a smithing table."))
quest(7, "rare_garden", "pitcher_plant", 25, [placed(b) for b in ("torchflower", "pitcher_plant", "wither_rose")],
      ("Ogród rzadkości", "Zasadź pochodnik, dzbanecznik i różę Withera. Najrzadsze rośliny w jednym miejscu."),
      ("Garden of rarities", "Plant a torchflower, a pitcher plant and a wither rose. The rarest plants in one place."))

# epilog: more goals
quest(E, "full_netherite", "netherite_chestplate", 100, [have(a) for a in ("netherite_helmet", "netherite_chestplate", "netherite_leggings", "netherite_boots")],
      ("Pełny netheryt", "Zdobądź hełm, napierśnik, nogawice i buty z netherytu."),
      ("Full netherite", "Obtain a netherite helmet, chestplate, leggings and boots."), "challenge")
quest(E, "trial_keys", "trial_key", 50, [have("trial_key"), have("ominous_trial_key")],
      ("Klucze prób", "Zdobądź zwykły i złowrogi klucz prób."),
      ("Trial keys", "Obtain a trial key and an ominous trial key."), "goal")
quest(E, "raid_breaker", "crossbow", 60, [killed(m) for m in ("pillager", "vindicator", "evoker", "ravager")],
      ("Pogromca najazdów", "Pokonaj rabusia, obrońcę, przywoływacza i dewastatora."),
      ("Raid breaker", "Defeat a pillager, a vindicator, an evoker and a ravager."), "goal")
quest(E, "axolotl_pond", "axolotl_bucket", 35, [bred("axolotl")],
      ("Staw aksolotli", "Rozmnóż aksolotle."),
      ("Axolotl pond", "Breed axolotls."))
quest(E, "panda_grove", "bamboo", 35, [bred("panda")],
      ("Bambusowy gaj", "Rozmnóż pandy."),
      ("Bamboo grove", "Breed pandas."))
quest(E, "turtle_beach", "turtle_egg", 35, [bred("turtle")],
      ("Żółwia plaża", "Rozmnóż żółwie."),
      ("Turtle beach", "Breed turtles."))
quest(E, "camel_caravan", "sand", 35, [bred("camel")],
      ("Karawana", "Rozmnóż wielbłądy."),
      ("Caravan", "Breed camels."))
quest(E, "goat_herd", "goat_horn", 30, [bred("goat")],
      ("Stado kóz", "Rozmnóż kozy."),
      ("Goat herd", "Breed goats."))
quest(E, "goat_music", "goat_horn", 30, [have("goat_horn")],
      ("Róg z gór", "Zdobądź róg kozła. Zagraj coś głośnego."),
      ("Horn from the mountains", "Obtain a goat horn. Play something loud."))
quest(E, "template_collector", "netherite_upgrade_smithing_template", 60,
      [have(t) for t in ("netherite_upgrade_smithing_template", "sentry_armor_trim_smithing_template", "eye_armor_trim_smithing_template")],
      ("Kolekcjoner szablonów", "Zdobądź szablon ulepszenia netherytu oraz szablony wzorów wartownika i oka."),
      ("Template collector", "Obtain a netherite upgrade template and the sentry and eye armor trim templates."), "goal")
quest(E, "sherd_collection", "angler_pottery_sherd", 50,
      [have(t) for t in ("angler_pottery_sherd", "archer_pottery_sherd", "arms_up_pottery_sherd", "blade_pottery_sherd")],
      ("Skorupy archeologa", "Zdobądź skorupy wędkarza, łucznika, uniesionych rąk i ostrza."),
      ("Archaeologist's sherds", "Obtain the angler, archer, arms up and blade pottery sherds."))
quest(E, "ominous_bottle", "ominous_bottle", 40, [have("ominous_bottle")],
      ("Złowroga butelka", "Zdobądź złowrogą butelkę. Zwiastuje coś niedobrego."),
      ("Ominous bottle", "Obtain an ominous bottle. It foretells trouble."))
quest(E, "heavy_core", "heavy_core", 80, [have("heavy_core")],
      ("Ciężki rdzeń", "Zdobądź ciężki rdzeń ze złowrogiego skarbca."),
      ("Heavy core", "Obtain a heavy core from an ominous vault."), "challenge")
quest(E, "mace_wielder", "mace", 80, [have("mace")],
      ("Władca maczugi", "Zdobądź maczugę. Zrzucaj się z wysokości z klasą."),
      ("Mace wielder", "Obtain a mace. Fall from heights with style."), "challenge")
quest(E, "wind_stock", "wind_charge", 30, [have("wind_charge", 64)],
      ("Zapas wichru", "Miej jednocześnie 64 ładunki wichru."),
      ("Wind stock", "Carry 64 wind charges at once."))
quest(E, "crystal_lab", "amethyst_block", 40, [placed(b) for b in ("amethyst_block", "tinted_glass", "calibrated_sculk_sensor")],
      ("Kryształowa pracownia", "Ustaw blok ametystu, przyciemnione szkło i skalibrowany czujnik sculku."),
      ("Crystal lab", "Place an amethyst block, tinted glass and a calibrated sculk sensor."))
quest(E, "sculk_garden", "sculk_sensor", 50, [placed(b) for b in ("sculk_sensor", "sculk_shrieker", "sculk_catalyst")],
      ("Ogród sculku", "Ustaw czujnik, wrzaskacz i katalizator sculku."),
      ("Sculk garden", "Place a sculk sensor, a shrieker and a catalyst."), "goal")
quest(E, "copper_power", "lightning_rod", 35, [placed(b) for b in ("lightning_rod", "copper_bulb", "copper_grate")],
      ("Miedziana elektrownia", "Ustaw piorunochron, miedzianą żarówkę i miedzianą kratę."),
      ("Copper power station", "Place a lightning rod, a copper bulb and a copper grate."))
quest(E, "last_bite", "enchanted_golden_apple", 60, [eat("enchanted_golden_apple")],
      ("Ostatni kęs", "Zjedz zaklęte złote jabłko. Rzadki przysmak z łupów."),
      ("The last bite", "Eat an enchanted golden apple. A rare treat from loot."), "goal")
quest(E, "diamond_hoard", "diamond", 60, [have("diamond", 64)],
      ("Sakwa diamentów", "Miej jednocześnie pełny stos 64 diamentów."),
      ("Diamond hoard", "Carry a full stack of 64 diamonds at once."), "goal")


# ------------------------------------------------------------------ registry validation
def load_registries(base):
    out = {}
    for tag in ("262", "263"):
        path = Path(base) / f"reports{tag}" / "out" / "reports" / "registries.json"
        data = json.loads(path.read_text(encoding="utf8"))
        out[tag] = {k: set(v["entries"]) for k, v in data.items() if "entries" in v}
    return out


KIND = {"block": "minecraft:block", "item": "minecraft:item", "entity": "minecraft:entity_type", "potion": "minecraft:potion",
        "structure": "minecraft:worldgen/structure"}


def validate(registries):
    problems = []
    for q in Q:
        for group in q["crit"]:
            for crit in (group if isinstance(group, list) else [group]):
                for kind, value in crit.check:
                    for version, regs in registries.items():
                        pool = regs.get(KIND[kind])
                        if pool is not None and "minecraft:" + value not in pool:
                            problems.append(f"{q['id']}: unknown {kind} minecraft:{value} in 26.{version[-1]}")
    for effect in EFFECTS_USED:
        for version, regs in registries.items():
            if "minecraft:" + effect not in regs["minecraft:mob_effect"]:
                problems.append(f"unknown effect {effect} in {version}")
    return problems


# ------------------------------------------------------------------ writers
def build_advancement(q):
    era = q["era"]
    parent = EPILOG if era == "epilog" else f"tempered:age/{era}"
    gate_id = EPILOG if era == "epilog" else f"tempered:age/{era}"
    criteria, requirements = {}, []
    for group in q["crit"]:
        members = group if isinstance(group, list) else [group]
        names = []
        for crit in members:
            cond = json.loads(json.dumps(crit.cond))
            if cond.get("_loc"):
                cond = {"player": [{"condition": "minecraft:entity_properties", "entity": "this",
                                    "predicate": {"minecraft:location": {"structures": "minecraft:" + cond["_loc"]}}},
                                   gate(gate_id)[0]]}
            else:
                cond["player"] = gate(gate_id)
            criteria[crit.name] = {"trigger": crit.trigger, "conditions": cond}
            names.append(crit.name)
        requirements.append(names)
    key = f"tempered.bonus.{era}.{q['id']}"
    return {
        "parent": parent,
        "display": {"icon": {"id": "minecraft:" + q["icon"]},
                    "title": {"translate": key + ".title"},
                    "description": {"translate": key + ".desc", "color": "gray"},
                    "frame": q["frame"], "show_toast": True, "announce_to_chat": False},
        "criteria": criteria, "requirements": requirements, "rewards": {"experience": q["xp"]},
    }


def epilog_root():
    return {
        "display": {"icon": {"id": "minecraft:dragon_head"},
                    "title": {"translate": "tempered.bonus.epilog.root.title", "color": "light_purple", "bold": True},
                    "description": {"translate": "tempered.bonus.epilog.root.desc", "color": "gray"},
                    "background": "minecraft:gui/advancements/backgrounds/end",
                    "frame": "goal", "show_toast": True, "announce_to_chat": False, "hidden": True},
        "criteria": {
            "killed_dragon": {"trigger": "minecraft:player_killed_entity",
                              "conditions": {"entity": entity("minecraft:ender_dragon")}},
            "already_defeated": {"trigger": "minecraft:tick",
                                 "conditions": {"player": gate("minecraft:end/kill_dragon")}}},
        "requirements": [["killed_dragon", "already_defeated"]],
    }


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registries", default=r"C:/Users/Admin/AppData/Local/Temp/claude/H--Claude-Code-New-MC/05a75c53-4143-4582-8287-1f744ddf4dbb/scratchpad")
    parser.add_argument("--no-validate", action="store_true")
    args = parser.parse_args()
    if not args.no_validate:
        problems = validate(load_registries(args.registries))
        if problems:
            raise SystemExit("Unknown ids:\n  " + "\n  ".join(problems))
        print(f"Validated {len(Q)} quests against the official 26.2 and 26.3 registries")
    ids = [(q["era"], q["id"]) for q in Q]
    assert len(ids) == len(set(ids)), "duplicate quest id"
    for q in Q:
        write_json(ADV / str(q["era"]) / f"{q['id']}.json", build_advancement(q))
    write_json(ADV / "epilog" / "root.json", epilog_root())

    lang = {}
    for tag, idx, prefix in (("pl_pl", "pl", OPT_PL), ("en_us", "en", OPT_EN)):
        path = LANG / f"{tag}.json"
        data = json.loads(path.read_text(encoding="utf8"))
        for q in Q:
            key = f"tempered.bonus.{q['era']}.{q['id']}"
            data[key + ".title"] = q[idx][0]
            data[key + ".desc"] = prefix + q[idx][1]
        data["tempered.bonus.epilog.root.title"] = "Epilog" if tag == "pl_pl" else "Epilogue"
        n_epilog = sum(1 for q in Q if q["era"] == "epilog")
        data["tempered.bonus.epilog.root.desc"] = (f"Smok pokonany. Świat czeka dalej: {n_epilog} celów na długie wieczory."
                                                   if tag == "pl_pl" else f"The dragon is down. The world goes on: {n_epilog} goals for long evenings.")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
        lang[tag] = len(data)

    # reset_bonus: keep Codex's header/lines, add every quest we generate (idempotent)
    lines = RESET.read_text(encoding="utf8").splitlines()
    revoke = [l for l in lines if l.startswith("advancement revoke")]
    tail = [l for l in lines if not l.startswith("advancement revoke") and not l.startswith("#")]
    header = [l for l in lines if l.startswith("#")]
    known = set(revoke)
    for q in Q:
        line = f"advancement revoke @s only tempered:bonus/{q['era']}/{q['id']}"
        if line not in known:
            revoke.append(line)
            known.add(line)
    RESET.write_text("\n".join(header + revoke + tail) + "\n", encoding="utf8")
    print(f"Wrote {len(Q)} quests ({sum(1 for q in Q if q['era'] == 'epilog')} epilog), lang keys: {lang}, reset lines: {len(revoke)}")


if __name__ == "__main__":
    main()
