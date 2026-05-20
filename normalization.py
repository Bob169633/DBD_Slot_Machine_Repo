import re

DBD_TERM_REPLACEMENTS = {
  "barbecue": "bbq",
  "chilli": "chili",
  "quick": "vittorios",
  "floods": "flood",
  "franklin's": "franklins",
  "franklins": "franklins",
  "demise": "loss",
  "rancor": "hatred",
  "revealed": "revelated",
  "limits": "confinement",
  "machine": "self",
  "learning": "aware",
  "thanatophobia": "thatanophobia",
  "shattered": "boon",
  "hope": "destroyer",
  "aestri yazar": "troupe",
  "aestri": "troupe",
  "lee yun-jin": "yunjinlee",
  "lee yun jin": "yunjinlee",
  "yun-jin lee": "yunjinlee",
  "yun jin lee": "yunjinlee",
  "the dark lord": "dracula",
  "dark lord": "dracula",
  "the good guy": "yerkes",
  "good guy": "yerkes",
  "phallanx": "phalanx",
  "macmillans": "macmillan",
  "macmillan's": "macmillan",
  "vigos": "vigo",
  "vigo's": "vigo",
  "campingaidkit": "rundownaidkit",
  "camping aid kit": "rundown aid kit",
  "emergencymedkit": "medkit",
  "emergency med kit": "medkit",
  "emergency med-kit": "medkit",
  "rangermedkit": "rangersaidkit",
  "ranger med kit": "rangers aid kit",
  "ranger med-kit": "rangers aid kit",
  "skeletonkey": "key",
  "skeleton key": "key",
  "bloodsensemap": "bloodmap",
  "bloodsense map": "blood map",
  "commodiustoolbox": "toolboxcommodious",
  "commodius toolbox": "toolbox commodious",
  "commodious toolbox": "toolbox commodious",
  "vigosfogvial": "vigos fog vial",
  "vigo's fog vial": "vigos fog vial",
  "vigos fog vial": "vigos fog vial",
  "annotatedmap": "rainbowmap",
  "annotated map": "rainbow map",
  "scribbledmap": "map",
  "scribbled map": "map",
  "sportflashlight": "flashlightsport",
  "sport flashlight": "flashlight sport",
  "utilityflashlight": "flashlightutility",
  "utility flashlight": "flashlight utility",
  "wornouttools": "toolboxwornout",
  "wornout tools": "toolbox worn out",
  "worn-out tools": "toolbox worn out",
  "worn out tools": "toolbox worn out",
  "all hallows' eve lunchbox": "medkit halloween",
  "all hallow's eve lunchbox": "medkit halloween",
  "all hallows eve lunchbox": "medkit halloween",
  "allhallowsevelunchbox": "medkithalloween",
  "mans": "man",
  "man's": "man",
  "dead mans": "dead man",
  "dead man's": "dead man",
  "judgement": "judgment",
  "onryō": "onryo"
}

ICON_SEARCH_ALIASES = {
  "allseeingblood": "bloodkrafabai",
  "allseeingspirit": "spiritallseeing",
  "blindwarriormud": "mudbaikrakaeug",
  "blindwarriorwhite": "whiteblindwarrior",
  "blinkmud": "mudblink",
  "blinkwhite": "whiteblink",
  "disciplinecartersnotes": "diciplinecartersnotes",
  "disciplineclassii": "diciplineclassii",
  "disciplineclassiii": "diciplineclassiii",
  "shadowdanceblood": "bloodshadowdance",
  "shadowdancewhite": "whiteshadowdance",
  "swifthuntblood": "bloodswifthunt",
  "swifthuntmud": "mudswifthunt",
  "swifthuntwhite": "whitekuntintakkho",
  "thebeastsoot": "sootthebeast",
  "theghostsoot": "soottheghost",
  "thehoundsoot": "sootthehound",
  "theserpentsoot": "soottheserpent",
  "windstormblood": "bloodwindstorm",
  "windstormwhite": "whitewindstorm",
  "windstormmud": "mudwindstorm",
  "4coilspringkit": "coilskit4",
  "fourcoilspringkit": "coilskit4",
  "antiexhaustionsyringe": "syringe",
  "airfreshener": "airfreshner",
  "bffs": "colddirt",
  "begrimedchains": "chainsrusted",
  "blacksmithshammer": "blacksmithhammer",
  "blessedapple": "prayerapple",
  "bloodyblackhood": "bloodiedblackhood",
  "bloodyfingernails": "bloodyfingernail",
  "ghostfacecaughtontape": "caughtontape",
  "catatonicboystreasure": "catatonictreasure",
  "chalicegold": "goldchalice",
  "coffeegrounds": "coffeegrinds",
  "defacedsmileypin": "defacedsmileybutton",
  "susiesmixtape": "suziesmixtape",
  "thelegionpin": "thelegionbutton",
  "smileyfacepin": "smileyfacebutton",
  "foxyshook": "foxyhook",
  "foxyhook": "foxyhook",
  "uroborosvirus": "lasplagasvariant",
  "egggold": "goldenegg",
  "fragranttuftofhair": "tuftofhair",
  "maidenmedallion": "maidenmedalliom",
  "muddysportsdaycap": "muddysportcap",
  "ether15vol": "ether15",
  "gauzeroll": "gauseroll",
  "goldcreekwhiskey": "clearcreekwhiskey",
  "videotapecopy": "vhscopy",
  "townwatchstorch": "townwatcttorch",
  "townwatchtorch": "townwatcttorch",
  "tortureapparatus": "medicalapparatus",
  "iridescentvideotape": "iridescentvhstape",
  "iridescentsealofmetatron": "iridescentseal",
  "mistydayremainsofjudgment": "mistyday",
  "supercharge": "overcharge",
  "razorwires": "razerwire",
  "refinedserum": "blightedsyringe",
  "rustedchain": "chainsrusted",
  "vorpalsword": "swordofkass",
  "juniperbonsai": "juniperbonzai",
  "iridescentstone": "diamondstone",
  "stylishsunglasses": "nastyblade",
  "distortedphoto": "disortedphoto",
  "goldtoken": "tokengold",
  "grislychain": "chainsgrisly",
  "oddstamp": "stampodd",
  "hacksaw": "metalsaw",
  "hairsprayandcandle": "flaminghairspray",
  "infraredupgrade": "infaredupgrade",
  "iridescentcrystalshard": "iridiscentcrystalshard",
  "kanekissatchel": "satchel",
  "kanekisatchel": "satchel",
  "lowampfilament": "threadedfilament",
  "matiasbabyshoes": "jacobsbabyshoes",
  "matiassbabyshoes": "jacobsbabyshoes",
  "medicalscissors": "scissors",
  "melodiousmurder": "yumismurder",
  "mysteriouselixir": "iridescentelixir",
  "needleandthread": "needandthread",
  "nightvisionmonocular": "nightvisionmoncular",
  "prototypeclaws": "prototypeclaw",
  "renjirosbloodyglove": "renirosbloodyglove",
  "renjirobloodyglove": "renirosbloodyglove",
  "rubbergloves": "gloves",
  "rulesetno2": "rulessetn2",
  "rulesetn2": "rulessetn2",
  "spatteredhandkerchief": "spottedhandkerchief",
  "thebeastsmarks": "thebeastsmark",
  "thebeastmarks": "thebeastsmark",
  "tillingblade": "tilingblade",
  "uniqueweddingring": "uniquering",
  "unusualstamp": "stampunusual",
  "wirespool": "spoolofwire",
  "yellowwire": "ropeyellow",
  "addongasbomb19aname": "stickysodabottle",
  "addongasbomb20aname": "cheapginbottle",
  "addongasbomb20bname": "sulphuricacidvial",
  "macmillansphalanxbone": "macmilliansphalanxbone",
  "macmillanphalanxbone": "macmilliansphalanxbone",
  "vigojarofsaltylips": "jarofsaltylips",
  "vigosjarofsaltylips": "jarofsaltylips",
  "beartrap": "beartrap",
  "fazbearsfright": "grab",
  "blightedcorruption": "k21",
  "theafterpiecetonic": "gasbomb",
  "afterpiecetonic": "gasbomb",
  "vampiricpower": "k37vampireform",
  "theredeemer": "uk",
  "redeemer": "uk",
  "ritesofjudgment": "walesritesofjudgement",
  "ritesofjudgement": "walesritesofjudgement",
  "testsubject001": "enterupsidedown",
  "nightshroud": "ghostpoweractivated",
  "hideyhomode": "k34",
  "scentofblood": "dashcommandk38",
  "guardiacompagnia": "assassin",
  "unbodiedflesh": "headformk41",
  "dreamdemon": "dreammaster",
  "spencerslastbreath": "breath",
  "spencerlastbreath": "breath",
  "delugeoffear": "delugeoffear2",
  "jigsawsbaptism": "reversebeartrap",
  "jigsawbaptism": "reversebeartrap",
  "eyesinthesky": "drones",
  "wailingbell": "bell"
}

def normalize_dbd_terms(text):
  text = str(text).lower().replace("’", "'").replace('"', "")

  for old, new in DBD_TERM_REPLACEMENTS.items():
    text = text.replace(old, new)

  return text

def normalize_text(text):
  text = normalize_dbd_terms(text).replace("&", "and")
  return re.sub(r"[^a-z0-9]", "", text)

def normalize_icon_search_text(text):
  text = str(text)
  for character in ('"', "“", "”", "'", "’", ",", ".", "(", ")"):
    text = text.replace(character, "")
  text = text.replace("-", " ")

  normalized_text = normalize_text(text)
  return ICON_SEARCH_ALIASES.get(normalized_text, normalized_text)

def get_icon_search_keys(text):
  search_keys = []
  base_key = normalize_icon_search_text(text)

  if base_key:
    search_keys.append(base_key)

  alternate_texts = [
    re.sub(r"\b([A-Za-z0-9]+)['’]s\b", r"\1", str(text)),
    re.sub(r"\b([A-Za-z0-9]+)['’]s\b", r"\1s", str(text))
  ]

  for alternate_text in alternate_texts:
    alternate_key = normalize_icon_search_text(alternate_text)

    if alternate_key and alternate_key not in search_keys:
      search_keys.append(alternate_key)

  return search_keys

def camel_to_words(text):
  return re.sub(r"([a-z])([A-Z])", r"\1 \2", str(text))

def remove_perk_prefix_terms(perk_name):
  perk_name = re.sub(r"\bboon\b:?", "", perk_name, flags=re.IGNORECASE)
  perk_name = re.sub(r"\bhex\b:?", "", perk_name, flags=re.IGNORECASE)
  perk_name = re.sub(r"\bscourge\s+hook\b:?", "", perk_name, flags=re.IGNORECASE)
  return re.sub(r"\s+", " ", perk_name).strip()
