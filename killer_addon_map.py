from normalization import normalize_icon_search_text

KILLER_ADDON_NAMES = {
  "Trapper": [
    "bloody coil", "iridescent stone", "honing stone", "oily coil", "tension spring",
    "trapper sack", "fastening tools", "rusted jaws", "secondary coil", "tar bottle",
    "trapper bag", "4-coil spring kit", "coffee grounds", "lengthened jaws", "serrated jaws",
    "wax brick", "bear oil", "makeshift wrap", "padded jaws", "trapper gloves",
  ],
  "Wraith": [
    '"All Seeing" - Spirit', "coxcombed clapper", '"All Seeing" - Blood',
    '"Shadow Dance" - Blood', '"Swift Hunt" - Blood', '"Windstorm" - Blood',
    '"Blind Warrior" - White', '"Blink" - White', '"Shadow Dance" - White',
    '"Swift Hunt" - White', '"Windstorm" - White', '"Blind Warrior" - Mud',
    '"Blink" - Mud', '"Swift Hunt" - Mud', '"Windstorm" - Mud', "Bone Clapper",
    '"The Beast" - Soot', '"The Ghost" - Soot', '"The Hound" - Soot', '"The Serpent" - Soot',
  ],
  "Hillbilly": [
    "iridescent engravings", "tuned carburetor", "apex muffler", "filthy slippers",
    "lo pro chains", "spiked boots", "begrimed chains", "dad's boots", "low kickback chains",
    "ragged engine", "the thompsons' mix", "clogged intake", "greased throttle",
    "high-speed idler screw", "off-brand motor oil", "thermal casing", "counterweight",
    "cracked primer bulb", "discarded air filter", "steel toe boots",
  ],
  "Nurse": [
    "matchbox", "torn bookmark", '"Bad Man\'s" Last Breath', "campbell's last breath",
    "jenner's last breath", "kavanagh's last breath", "anxious gasp", "ataxic respiration",
    "fragile wheeze", "heavy panting", "spasmodic breath", "bad man keepsake",
    "catatonic boy's treasure", "dark cincture", "dull bracelet", "pocket watch", "metal spoon",
    "plaid flannel", "white nit comb", "wooden horse",
  ],
  "Shape": [
    "judith's tombstone", "scratched mirror", "lock of hair", "reflective fragment", "tombstone piece",
    "vanity mirror", "hair bow", "j.myers memorial", "jewelry box", "judith's journal",
    "mirror shard", "dead rabbit", "fragrant tuft of hair", "glass fragment", "hair brush",
    "jewelry", "blonde hair", "boyfriend's memo", "memorial flower", "tacky earrings",
  ],
  "Hag": [
    "mint rag", "waterlogged shoe", "disfigured ear", "grandma's heart", "rusty shackles",
    "scarred hand", "bloodied mud", "cracked turtle egg", "dried cicada", "swamp orchid necklet",
    "willow wreath", "bloodied water", "cypress necklet", "dragonfly wings", "half eggshell",
    "pussy willow catkins", "bog water", "dead fly mud", "powdered eggshell", "rope necklet",
  ],
  "Doctor": [
    "iridescent king", "iridescent queen", '"Calm" - Carter\'s Notes',
    '"Discipline" - Carter\'s Notes', '"Order" - Carter\'s Notes',
    '"Restraint" - Carter\'s Notes', '"Discipline" - Class III', '"Restraint" - Class III',
    "high stimulus electrode", "interview tape", "scrapped tape", '"Calm" - Class II',
    '"Discipline" - Class II', '"Order" - Class II', '"Restraint" - Class II',
    "polished electrode", '"Calm" - Class I', '"Order" - Class I', "maple knight", "moldy electrode",
  ],
  "Cannibal": [
    "iridescent flesh", "carburetor tuning guide", "award-winning chili", "depth gauge rake",
    "light chassis", "rusted chain", "begrimed chains", "grisly chain", "shop lubricant",
    "the beast's marks", "the grease", "chili", "homemade muffler", "knife scratches",
    "long guide bar", "primer bulb", "chainsaw file", "spark plug", "speed limiter", "vegetable oil",
  ],
  "Huntress": [
    "iridescent head", "soldier's puttee", "begrimed head", "glowing concoction", "infantry belt",
    "wooden fox", "deerskin gloves", "flower babushka", "rose root", "rusty head",
    "venomous concoction", "leather loop", "manna grass braid", "oak haft", "shiny pin",
    "weighted head", "amanita toxin", "bandaged haft", "coarse stone", "yellowed cloth",
  ],
  "Nightmare": [
    "black box", "red paint brush", '"Z" Block', "class photo", "pill bottle", "swing chains",
    "blue dress", "jump rope", "nancy's masterpiece", "paint thinner", "unicorn block", "cat block",
    "green dress", "nancy's sketch", "outdoor rope", "prototype claws", "garden rake",
    "kid's drawing", "sheep block", "wool shirt",
  ],
  "Pig": [
    "amanda's letter", "video tape", "amanda's secret", "crate of gears", "jigsaw's sketch",
    "tampered timer", "bag of gears", "jigsaw's annotated plan", "rule set no.2",
    "rusty attachments", "slow-release toxin", "face mask", "last will", "razor wires",
    "utility blades", "workshop grease", "combat straps", "interlocking razor",
    "john's medical file", "shattered syringe",
  ],
  "Clown": [
    "redhead's pinky finger", "tattoo's middle finger", "cigar box", "ether 15 vol%",
    "garish makeup kit", "bottle of chloroform", "flask of bleach", "smelly inner soles",
    "spirit of hartshorn", "sulfuric acid vial", "kerosene can", "solvent jug",
    "starling feather", "sticky soda bottle", "thick cork stopper", "fingerless parade gloves",
    "party bottle", "robin feather", "vhs porn", "cheap gin bottle",
  ],
  "Spirit": [
    "kintsugi teacup", "mother-daughter ring", "dried cherry blossom", "furin", "wakizashi saya",
    "yakuyoke amulet", "katana tsuba", "mother's glasses", "rusty flute", "senko hanabi",
    "uchiwa", "juniper bonsai", "kaiun talisman", "muddy sports day cap", "rin's broken watch",
    "white hair ribbon", "gifted bamboo comb", "origami crane", "shiawase amulet", "zōri",
  ],
  "Legion": [
    "fuming mix tape", "iridescent button", "bffs", "filthy blade", "frank's mix tape",
    "stab wounds study", "joey's mix tape", "stolen sketch book", "stylish sunglasses",
    "susie's mix tape", "the legion pin", "defaced smiley pin", "etched ruler",
    "julie's mix tape", "mural sketch", "never-sleep pills", "friendship bracelet",
    "mischief list", "scratched ruler", "smiley face pin",
  ],
  "Plague": [
    "black incense", "iridescent seal", "devotee's amulet", "severed toe", "vile emetic",
    "worship tablet", "ashen apple", "exorcism amulet", "incensed ointment", "infected emetic",
    "rubbing oil", "blessed apple", "emetic poison", "hematite seal", "potent tincture",
    "prophylactic amulet", "healing salve", "limestone seal", "olibanum incense", "prayer tablet fragment",
  ],
  "Ghost Face": [
    "outdoor security camera", '"ghost face caught on tape"', "driver's license", "drop-leg knife sheath",
    "night vision monocular", "victim's detailed routine", "chewed pen", "knife belt clip",
    "lasting perfume", "leather knife sheath", "olsen's wallet", "cinch straps", "marked map",
    "olsen's address book", "olsen's journal", "telephoto lens", "cheap cologne",
    "headline cutouts", "walleye's matchbook", '"philly"',
  ],
  "Demogorgon": [
    "leprose lichen", "red moss", "lifeguard whistle", "unknown egg", "upside down resin",
    "vermillion webcap", "brass case lighter", "deer lung", "eleven's soda", "thorny vines",
    "violet waxcap", "barb's glasses", "mew's guts", "rotten green tape", "sticky lining",
    "viscous webbing", "black heart", "rat liver", "rat tail", "rotten pumpkin",
  ],
  "Oni": [
    "iridescent family crest", "renjiro's bloody glove", "akito's crutch", "lion fang",
    "splintered hull", "tear soaked tenugui", "kanai-anzen talisman", "scalped topknot",
    "shattered wakizashi", "wooden oni mask", "yamaoka sashimono", "bloody sash",
    "child's wooden sword", "chipped saihai", "ink lion", "polished maedate",
    "blackened toenail", "cracked sakazuki", "paper lantern", "rotting rope",
  ],
  "Deathslinger": [
    "hellshire iron", "iridescent coin", "barbed wire", "bayshore's cigar", "gold creek whiskey",
    "prison chain", "bayshore's gold tooth", "honey locust thorns", "tin oil can", "wanted poster",
    "warden's keys", "chewing tobacco", "jaw smasher", "marshal's badge", "poison oak leaves",
    "rusted spike", "modified ammo belt", "rickety chain", "snake oil", "spit polish rag",
  ],
  "Executioner": [
    "iridescent seal of metatron", "obsidian goblet", "crimson ceremony book", "lost memories book",
    "rust-colored egg", "scarlet egg", "burning man painting", "mannequin foot",
    "misty day, remains of judgement", "tablet of the oppressor", "valtiel sect photograph",
    "cinderella music box", "forgotten videotape", "leopard-print fabric", "spearhead",
    "wax doll", "black strap", "copper ring", "dead butterfly", "lead ring",
  ],
  "Blight": [
    "compound thirty-three", "iridescent blight tag", "alchemist's ring", "soul chemical",
    "summoning stone", "vigo's journal", "adrenaline vial", "blighted crow", "compound twenty-one",
    "rose tonic", "umbra salts", "blighted rat", "canker thorn", "plague bile", "pustula dust",
    "shredded notes", "chipped monocle", "compound seven", "foxglove", "placebo tablet",
  ],
  "Twins": [
    "iridescent pendant", "silencing cloth", "drop of perfume", "forest stew", "spinning top",
    "victor's soldier", "madeleine's scarf", "rusted needle", "sewer sludge", "stale biscuit",
    "weighty rattle", "baby teeth", "bloody black hood", "cat's eye", "ceremonial candelabrum",
    "madeleine's glove", "cat figurine", "soured milk", "tiny fingernail", "toy sword",
  ],
  "Trickster": [
    "death throes compilation", "iridescent photocard", "cut thru u single", "diamond cufflinks",
    "edge of revival album", "trick blades", "fizz-spin soda", "melodious murder", "on target single",
    "ripper brace", "waiting for you watch", "bloody boa", "caged heart shoes", "ji-woon's autograph",
    "lucky blade", "tequila moonrock", "inferno wires", "killing part chords", "memento blades", "trick pouch",
  ],
  "Nemesis": [
    "iridescent umbrella badge", "shattered S.T.A.R.S. badge", "broken recovery coin", "depleted ink ribbon",
    "jill's sandwich", "ne-a parasite", "licker tongue", "plant 43 vines", "serotonin injector",
    "t-virus sample", "tyrant gore", "admin wristband", "adrenaline injector", "marvin's blood",
    "mikhail's eye", "zombie heart", "brian's intestine", "damaged syringe",
    "S.T.A.R.S. field combat manual", "visitor wristband",
  ],
  "Cenobite": [
    "engineer's fang", "iridescent lament configuration", "chatterer's tooth", "greasy black lens",
    "impaling wire", "original pain", "frank's heart", "larry's blood", "larry's remains",
    "slice of frank", "torture pillar", "flickering television", "liquified gore", "skewered rat",
    "spoiled meal", "wriggling maggots", "bent nail", "burning candle", "leather strip", "lively crickets",
  ],
  "Artist": [
    "garden of rot", "iridescent feather", "ink egg", "matias' baby shoes", "severed hands",
    "severed tongue", "charcoal stick", "darkest ink", "o grief, o lover", "silver bell",
    "thorny nest", "automatic drawing", "festering carrion", "still life crow", "untitled agony",
    "velvet fabric", "choclo corn", "oil paints", "thick tar", "vibrant obituary",
  ],
  "Onryō": [
    "iridescent videotape", "remote control", "distorted photo", "tape editing deck", "telephone",
    "vcr", "bloody fingernails", "mother's comb", "rickety pinwheel", "ring drawing",
    "well water", "clump of hair", "reiko's watch", "sea-soaked cloth", "well stone",
    "yoichi's fishing net", "cabin sign", "mother's mirror", "old newspaper", "videotape copy",
  ],
  "Dredge": [
    "iridescent wooden plank", "sacrificial knife", "boat key", "field recorder", "lavalier microphone",
    "tilling blade", "broken doll", "destroyed pillow", "ottomarian writing", "war helmet",
    "worry stone", "air freshener", "burnt letters", "fallen shingle", "haddie's calendar",
    "malthinker's skull", "caffeine tablets", "follower's cowl", "mortar and pestle", "wooden plank",
  ],
  "Mastermind": [
    "iridescent uroboros vial", "lab photo", "dark sunglasses", "green herb", "helicopter stick",
    "uroboros virus", "egg (gold)", "maiden medallion", "portable safe", "red herb",
    "video conference device", "bullhorn", "chalice (gold)", "leather gloves", "lion medallion",
    "loose crank", "jewel beetle", "r.p.d. shoulder walkie", "unicorn medallion", "uroboros tendril",
  ],
  "Knight": [
    "iridescent company banner", "knight's contract", "blacksmith's hammer", "flint and steel",
    "healing poultice", "jailer's chimes", "broken hilt", "grim iron mask", "ironworker's tongs",
    "sharpened mount", "town watch's torch", "battleaxe head", "call to arms", "cold steel manacles",
    "dried horsemeat", "treated blade", "gritty lump", "map of the realm", "pillaged mead", "tattered tabard",
  ],
  "Skull Merchant": [
    "expired batteries", "iridescent unpublished manuscript", "advanced movement prediction", "geographical readout",
    "prototype rotor", "randomized strobes", "brown noise generator", "infrared upgrade", "loose screw",
    "powdered glass", "vital targeting processor", "adaptive lighting", "low-power mode", "shotgun speakers",
    "stereo remote mic", "supercharge", "adi valente #1", "high current upgrade", "high-power floodlight", "ultrasonic speaker",
  ],
  "Singularity": [
    "denied requisition form", "iridescent crystal shard", "crew manifest", "diagnostic tool (construction)",
    "foreign plant fibers", "soma family photo", "hologram generator", "hyperawareness spray",
    "live wires", "nanomachine gel", "spent oxygen tank", "android arm", "cremated remains",
    "cryo gel", "kid's ball glove", "ultrasonic sensor", "broken security key", "diagnostic tool (repair)",
    "heavy water", "nutritional slurry",
  ],
  "Xenomorph": [
    "acidic blood", "improvised cattle prod", "cat carrier", "harpoon gun", "self-destruct bolt",
    "semiotic keyboard", "emergency helmet", "kane's helmet", "moted skin", "multipurpose hatchet",
    "parker's headband", "ash's innards", "brett's cap", "crew headset", "lambert's star map",
    "light wand", "cereal rations", "drinking bird", "ovomorph", "ripley's watch",
  ],
  "Good Guy": [
    "hard hat", "iridescent amulet", "mirror shards", "pile of nails", "plastic bag", "straight razor",
    "portable TV", "rat poison", "running shoes", "silk pillow", "yardstick", "automatic screwdriver",
    "electric carving knife", "hair spray & candle", "jump rope", "power drill", "doll eyes",
    "good guy box", "strobing light", "tiny scalpel",
  ],
  "Unknown": [
    "captured by the dark", "iridescent oss report", "discarded milk carton", "homemade mask",
    "obscure game cartridge", "serum vial", "b-movie poster", "footprint cast", "front-page article",
    "hypnotist's watch", "vanishing box", "device of undisclosed origin", "last known recording",
    "notebook of theories", "slashed backpack", "victim's map", "blurry photo", "punctured eyeball",
    "rabbit's foot", "sketch attempt",
  ],
  "Lich": [
    "iridescent book of vile darkness", "vorpal sword", "bag of holding", "cloak of invisibility",
    "dragontooth dagger", "robe of eyes", "boots of speed", "cloak of elvenkind", "ornate horn",
    "pearl of power", "staff of withering", "glass eye", "lantern of revealing", "potion of speed",
    "ring of spell strong", "ring of telekinesis", "crystal ball", "raven's feather",
    "tattered headband", "trickster's glove",
  ],
  "Dark Lord": [
    "alucard's shield", "iridescent ring of vlad", "cube of zoe", "lapis lazuli", "medusa's hair",
    "warg's fang", "force of echo", "killer doll", "pocket watch", "sunglasses", "sylph feather",
    "blood-filled goblet", "magical ticket", "moonstone necklace", "white wolf medallion",
    "winged boots", "cerberus talon", "clock tower gear", "ruby circlet", "traveler's hat",
  ],
  "Houndmaster": [
    "iridescent wheel handle", "torn novel", "gunpowder tin", "leather harness", "marlinspike",
    "ship figurehead", "fatty meat", "spiked collar", "training bell", "unfinished map", "waterskin",
    "barley meal", "belaying pins", "knotted rope", "smoked snapper", "spyglass", "creature's bone",
    "sticky patch", "trainer's book", "young coconut",
  ],
  "Ghoul": [
    "iridescent eye patch", "yamori's mask", "ccg id card", "fresh coffee", "red-headed centipede",
    "torture apparatus", "amon's necktie", "aogiri tree robe", "mado's glove", "red spider lily",
    "rize's glasses", "blood-stained handkerchief", "broken chain", "hide's headphones",
    "hinami's umbrella", "kaneki's satchel", "anteiku apron", "kaneki's wallet", "taiyaki",
    "the black goat's egg",
  ],
  "Animatronic": [
    "faz-coin", "iridescent remnant", "access panel", "celebrate! poster", "endo cpu", "loot bag",
    "bonnie's guitar strings", "chica's bib", "foxy's hook", "freddy's hat", "purple guy drawing",
    "office phone", "party hat", "ripped curtain", "security guard's badge", "streamers",
    "greasy paper plate", "help wanted ad", "restaurant menu", "rotten pizza",
  ],
  "Krasue": [
    "chicken head", "shredded gown", "lorenza's remains", "mysterious elixir", "queen's scepter",
    "rotten swine", "dulled knife", "framed newspaper", "janjira's hand", "spattered handkerchief",
    "theater binoculars", "chunk of malai", "crumpled sheet music", "defective metronome",
    "pig's eye", "wriggling parasite", "broken tiara", "first libretto", "luckless mouse", "sticky lozenge",
  ],
  "First": [
    "chess piece", "iridescent soteria chip", "black widow spider", "broken skateboard",
    "electroshock collar", "rabbit remains", "electrode cap", "forged death certificate",
    "neck tendril", "pizza goggles", "victor's razor blade", "bloody roller skate", "clock hands",
    "gutted supercom", "shattered wrist rocket", "smashed cassette deck", "bead maze",
    "mid-century radio", "orderly ID", "stained glass mural",
  ],
  "Slasher": [
    "dirty money", "iridescent boat motor", "bloody magazine", "burnt fuse", "deputy's badge",
    "missing corkscrew", "eye goop", "imprinted aluminum", "mirror shards", "sauna rock", "two nails",
    "bloody smile", "coroner's coffee", "party noisemaker", "sleeping bag", "toxic waste",
    "bent wheel", "garden claw", "knitting needle", "orderly's shoe",
  ],
}

KILLER_KEY_BY_ALIAS = {}
for killer_name in KILLER_ADDON_NAMES:
  normalized_killer_name = normalize_icon_search_text(killer_name)
  KILLER_KEY_BY_ALIAS[normalized_killer_name] = killer_name

  the_killer_name = f"The {killer_name}"
  KILLER_KEY_BY_ALIAS[normalize_icon_search_text(the_killer_name)] = killer_name

NORMALIZED_ADDON_NAMES_BY_KILLER = {
  killer_name: {normalize_icon_search_text(addon_name) for addon_name in addon_names}
  for killer_name, addon_names in KILLER_ADDON_NAMES.items()
}

def get_manual_killer_key(owner_terms):
  for owner_term in owner_terms:
    normalized_term = normalize_icon_search_text(owner_term)
    if normalized_term in KILLER_KEY_BY_ALIAS:
      return KILLER_KEY_BY_ALIAS[normalized_term]
  return None

def get_manual_killer_addons(addons, owner_terms):
  killer_key = get_manual_killer_key(owner_terms)
  if killer_key is None:
    return None

  allowed_names = NORMALIZED_ADDON_NAMES_BY_KILLER.get(killer_key, set())
  return [
    addon for addon in addons
    if normalize_icon_search_text(addon.get("name", "")) in allowed_names
  ]
