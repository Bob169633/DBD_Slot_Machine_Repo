import random


SURVIVOR_ADEPT_PERKS = {
  "Dwight Fairfield": ["Bond", "Prove Thyself", "Leader"],
  "Meg Thomas": ["Sprint Burst", "Adrenaline", "Quick and Quiet"],
  "Claudette Morel": ["Self-Care", "Botany Knowledge", "Empathy"],
  "Jake Park": ["Saboteur", "Calm Spirit", "Iron Will"],
  "Nea Karlsson": ["Balanced Landing", "Streetwise", "Urban Evasion"],
  "William B. Overbeck": ["Left Behind", "Unbreakable", "Borrowed Time"],
  "Laurie Strode": ["Decisive Strike", "Object of Obsession", "Sole Survivor"],
  "Ace Visconti": ["Ace in the Hole", "Open Handed", "Up the Ante"],
  "Feng Min": ["Lithe", "Technician", "Alert"],
  "David King": ["Dead Hard", "No Mither", "We're Gonna Live Forever"],
  "Quentin Smith": ["Pharmacy", "Wake Up!", "Vigil"],
  "Detective Tapp": ["Stake Out", "Tenacity", "Detective's Hunch"],
  "Kate Denson": ["Dance With Me", "Boil Over", "Windows of Opportunity"],
  "Adam Francis": ["Distraction", "Deliverance", "Autodidact"],
  "Jeff Johansen": ["Distortion", "Breakdown", "Aftercare"],
  "Jane Romero": ["Head On", "Poised", "Solidarity"],
  "Ashley J. Williams": ["Mettle of Man", "Buckle Up", "Flip-Flop"],
  "Nancy Wheeler": ["Inner Strength", "Fixated", "Better Together"],
  "Steve Harrington": ["Babysitter", "Second Wind", "Camaraderie"],
  "Yui Kimura": ["Breakout", "Any Means Necessary", "Lucky Break"],
  "Zarina Kassir": ["For The People", "Red Herring", "Off The Record"],
  "Cheryl Mason": ["Soul Guard", "Repressed Alliance", "Blood Pact"],
  "Felix Richter": ["Built To Last", "Desperate Measures", "Visionary"],
  "Elodie Rakoto": ["Deception", "Power Struggle", "Appraisal"],
  "Lee Yun-Jin": ["Smash Hit", "Self Preservation", "Fast Track"],
  "Jill Valentine": ["Blast Mine", "Counterforce", "Resurgence"],
  "Leon S. Kennedy": ["Rookie Spirit", "Flashbang", "Bite The Bullet"],
  "Mikaela Reid": ["Boon: Circle of Healing", "Boon: Shadow Step", "Clairvoyance"],
  "Jonah Vasquez": ["Corrective Action", "Overcome", "Boon: Exponential"],
  "Yoichi Asakawa": ["Parental Guidance", "Boon: Dark Theory", "Empathic Connection"],
  "Haddie Kaur": ["Residual Manifest", "Overzealous", "Inner Focus"],
  "Ada Wong": ["Low Profile", "Wiretap", "Reactive Healing"],
  "Rebecca Chambers": ["Hyperfocus", "Reassurance", "Better Than New"],
  "Vittorio Toscano": ["Fogwise", "Quick Gambit", "Potential Energy"],
  "Thalita Lyra": ["Cut Loose", "Teamwork: Power of Two", "Friendly Competition"],
  "Renato Lyra": ["Blood Rush", "Background Player", "Teamwork: Collective Stealth"],
  "Gabriel Soma": ["Made For This", "Troubleshooter", "Scavenger"],
  "Nicolas Cage": ["Dramaturgy", "Plot Twist", "Scene Partner"],
  "Ellen Ripley": ["Lucky Star", "Chemical Trap", "Light-footed"],
  "Alan Wake": ["Boon: Illumination", "Champion of Light", "Deadline"],
  "Sable Ward": ["Invocation: Weaving Spiders", "Strength In Shadows", "Wicked"],
  "Aestri Yazar": ["Bardic Inspiration", "Mirrored Illusion", "Still Sight"],
  "Lara Croft": ["Hardened", "Finesse", "Specialist"],
  "Trevor Belmont": ["Exultation", "Moment of Glory", "Eyes of Belmont"],
  "Taurie Cain": ["Shoulder The Burden", "Invocation: Weaving Spiders", "Clean Break"],
  "Orela Rose": ["Do No Harm", "Rapid Response", "Duty of Care"],
  "Rick Grimes": ["Apocalyptic Ingenuity", "Teamwork: Toughen Up", "Come and Get Me!"],
  "Michonne Grimes": ["Last Stand", "Teamwork: Throwdown", "Conviction"],
  "Vee Boonyasak": ["ONE-TWO-THREE-FOUR!", "Road Life", "Ghost Notes"],
  "Dustin Henderson": ["Bada Bada Boom", "Change of Plan", "Teamwork: Full Circuit"],
  "Eleven": ["Extrasensory Perception", "We See You", "Teamwork: Soft-Spoken"],
  "Kwon Tae-Young": ["Five Moves Ahead", "Flow State", "A Place For Us"],
}


KILLER_ADEPT_PERKS = {
  "The Trapper": ["Brutal Strength", "Unnerving Presence", "Agitation"],
  "The Wraith": ["Bloodhound", "Predator", "Shadowborn"],
  "The Hillbilly": ["Lightborn", "Tinkerer", "Enduring"],
  "The Nurse": ["A Nurse's Calling", "Thanatophobia", "Stridor"],
  "The Shape": ["Dying Light", "Save the Best For Last", "Play With Your Food"],
  "The Hag": ["Hex: Devour Hope", "Hex: Third Seal", "Hex: Ruin"],
  "The Doctor": ["Overwhelming Presence", "Monitor and Abuse", "Overcharge"],
  "The Cannibal": ["Barbecue and Chili", "Knockout", "Franklin's Demise"],
  "The Huntress": ["Hex: Lullaby", "Beast of Prey", "Territorial Imperative"],
  "The Nightmare": ["Blood Warden", "Remember Me", "Fire Up"],
  "The Pig": ["Make Your Choice", "Surveillance", "Scourge Hook: Hangman's Trick"],
  "The Clown": ["Bamboozle", "Pop Goes the Weasel", "Coulrophobia"],
  "The Spirit": ["Spirit Fury", "Hex: Haunted Ground", "Rancor"],
  "The Legion": ["Iron Maiden", "Discordance", "Mad Grit"],
  "The Plague": ["Dark Devotion", "Corrupt Intervention", "Infectious Fright"],
  "The Ghostface": ["Furtive Chase", "I'm All Ears", "Thrilling Tremors"],
  "The Demogorgon": ["Surge", "Mindbreaker", "Cruel Limits"],
  "The Oni": ["Blood Echo", "Nemesis", "Zanshin Tactics"],
  "The Deathslinger": ["Gearhead", "Dead Man's Switch", "Hex: Retribution"],
  "The Executioner": ["Trail of Torment", "Forced Penance", "Deathbound"],
  "The Blight": ["Dragon's Grip", "Hex: Blood Favor", "Hex: Undying"],
  "The Twins": ["Coup de Grace", "Hoarder", "Oppression"],
  "The Trickster": ["Starstruck", "Hex: Crowd Control", "No Way Out"],
  "The Nemesis": ["Lethal Pursuer", "Eruption", "Hysteria"],
  "The Cenobite": ["Scourge Hook: Gift of Pain", "Deadlock", "Hex: Plaything"],
  "The Artist": ["Grim Embrace", "Scourge Hook: Pain Resonance", "Hex: Pentimento"],
  "The Onryo": ["Call of Brine", "Scourge Hook: Floods of Rage", "Merciless Storm"],
  "The Dredge": ["Dissolution", "Darkness Revealed", "Septic Touch"],
  "The Mastermind": ["Awakened Awareness", "Superior Anatomy", "Terminus"],
  "The Knight": ["Hex: Face the Darkness", "Hubris", "Nowhere to Hide"],
  "The Skull Merchant": ["TWHACK!", "Leverage", "Game Afoot"],
  "The Singularity": ["Genetic Limits", "Forced Hesitation", "Machine Learning"],
  "The Xenomorph": ["Ultimate Weapon", "Rapid Brutality", "Alien Instinct"],
  "The Good Guy": ["Friends 'til the End", "Batteries Included", "Hex: Two Can Play"],
  "The Unknown": ["Undone", "Unforeseen", "Unbound"],
  "The Lich": ["Weave Attunement", "Dark Arrogance", "Languid Touch"],
  "The Dark Lord": ["Dominance", "Human Greed", "Hex: Wretched Fate"],
  "The Houndmaster": ["Scourge Hook: Jagged Compass", "All-Shaking Thunder", "No Quarter"],
  "The Ghoul": ["Forever Entwined", "Hex: Nothing But Misery", "None Are Free"],
  "The Animatronic": ["Phantom Fear", "Haywire", "Help Wanted"],
  "The Krasue": ["Hex: Overture of Doom", "Ravenous", "Wandering Eye"],
  "The First": ["Turn Back The Clock", "Secret Project", "Hex: Hive Mind"],
  "The Slasher": ["Hex: Scared to Death", "Silent Shadow", "Rampage"],
}


def initialize_adept_perk_dictionaries(survivor_characters, killer_characters):
  for survivor in survivor_characters:
    SURVIVOR_ADEPT_PERKS.setdefault(survivor["name"], [])

  for killer in killer_characters:
    KILLER_ADEPT_PERKS.setdefault(killer["name"], [])


def get_adept_dictionary(role):
  if role == "Killer":
    return KILLER_ADEPT_PERKS

  return SURVIVOR_ADEPT_PERKS


def get_adept_perk_names(role, character_name):
  adept_dictionary = get_adept_dictionary(role)
  return list(adept_dictionary.get(character_name, []))


def choose_adept_loadout_source_character(role, selected_character, characters):
  selected_name = selected_character["name"]

  possible_source_characters = [
    character
    for character in characters
    if character["name"] != selected_name
  ]

  if not possible_source_characters:
    return selected_character

  return random.choice(possible_source_characters)