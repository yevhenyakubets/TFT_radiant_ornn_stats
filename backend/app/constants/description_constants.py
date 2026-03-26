keyword_map = {
    "{{TFT_Keyword_Sunder}}": "Sunder: Reduce Armor",
    "{{TFT_Keyword_Shred}}": "Shred: Reduce Magic Resist",
    "{{TFT_Keyword_Chill}}": "Chill: Reduce Attack Speed",
    "{{TFT_Keyword_Wound}}": "Wound: Reduce healing received by 33%",
    "{{TFT_Keyword_Burn}}": "Burn: Deal a percent of the target's max Health as true damage every second",
}

CHAMP_BASE_STATS = {
    "ashe": {"hp": None, "ad": 58},
    "dr. mundo": {"hp": 900, "ad": None},
    "jinx": {"hp": None, "ad": 50},
    "nasus": {"hp": 1500, "ad": None},
    "nautilus": {"hp": 900, "ad": None},
    "rift herald": {"hp": 1100, "ad": None},
    "ryze": {"hp": 1000, "ad": None},
    "sion": {"hp": 650, "ad": None},
    "swain": {"hp": 1200, "ad": None},
    "volibear": {"hp": 1200, "ad": None},
    "wukong": {"hp": 1050, "ad": None},
    "yasuo": {"hp": None, "ad": 45},
    "yorick": {"hp": 850, "ad": None},
}

SPECIFIC_EXCEPTIONS = {
    "aatrox": {
        "firstcastmodifieddamage": (["addamage", "apdamage"], None),
        "secondcastmodifieddamage": (
            ["addamage", "apdamage"],
            "secondcastpercentdamage",
        ),
        "thirdcastmodifieddamage": (["addamage", "apdamage"], "thirdcastpercentdamage"),
    },
    "annie": {
        "modifieddamage": (["damage"], None),
        "modifiedsecondarydamage": (["singletargetdamage"], None),
    },
    "ashe": {"smallarrowdamagefinal": (["smallarrowdamage*base_ad"], None)},
    "azir": {"modifiedsecondarydamage": (["maxsummonsdamage"], None)},
    "baron nashor": {
        "modifiedaciddamage": (["addamage", "apdamage"], "acidpercentdamage"),
    },
    "bel'veth": {
        "modifiedattackspeed": (["attackspeedontransform*100"], None),
    },
    "braum": {
        "modifieddurability": (["damagereduction"], None),
        "modifieddamage": (["apdamage", "armordamage*60"], None),
    },
    "briar": {
        "modifiedattackspeed": (["decayingattackspeed*100"], None),
    },
    "blitzcrank": {
        "modifieddamage": (["mrdamageratio*40"], None),
    },
    "darius": {
        "modifiedsecondarydamage": (["physicaldamagepersecond"], None),
    },
    "dr. mundo": {
        "totalhealing": (
            ["percenthealthhealingpersecond*base_hp", "aphealpersecond"],
            None,
        ),
        "totaldamage": (["percentmaximumhealthdamage*base_hp", "addamage"], None),
    },
    "fizz": {
        "modifiedattackdamage": (["damageonhit"], None),
    },
    "galio": {
        "bonuspassivedamage": (["passivemrratio*65"], None),
        "modifiedactivedamage": (["activeardamage*65", "activemrdamage*65"], None),
    },
    "gwen": {
        "modifiedcastsniptimes": (["snipcount"], None),
        "modifieddamage": (["damage"], None),
        "modifiedsecondarydamage": (["secondarymagicdamage"], None),
    },
    "jarvan iv": {
        "modifiedattackspeed": (["attackspeed*100"], None),
    },
    "kalista": {
        "totalnumberofspears": (["basespears"], None),
    },
    "leona": {
        "modifieddamagereduction": (["flatdr"], None),
    },
    "lux": {
        "modifieddamage_q": (["qdamage"], None),
    },
    "mel": {
        "modifiedsecondarydamage": (["targetdamage"], None),
        "tftunitproperty.:tft16_mel_manaspent": (["0"], None),
    },
    "milio": {
        "modifiedaoedamage": (["magicdamageaoe"], None),
    },
    "miss fortune": {
        "modifiedsecondarydamage": (
            ["addamage", "apdamage"],
            "percentdamageofsecondarywaves",
        ),
    },
    "nautilus": {
        "modifieddamage": (["mrdamageratio*50"], None),
        "modifiedshield": (["apshield", "percenthealthshield*base_hp"], None),
    },
    "nasus": {
        "modifieddamagepersecond": (["percenthealthdamagepersecond*base_hp"], None),
    },
    "orianna": {
        "modifiedsecondarydamage": (["targetdamage"], None),
    },
    "rek'sai": {
        "modifiedsecondarydamage": (["spellattackdamage"], None),
    },
    "renekton": {
        "modifieddashdamage": (["dashaddamage"], None),
        "modifiedslashdamage": (["slashaddamage", "slashapdamage"], None),
    },
    "rift herald": {
        "modifieddurability": (["bonusdurability*100"], None),
        "modifieddamage": (["apdamage", "percenthealthdamage*base_hp"], None),
    },
    "rumble": {
        "modifiedshield": (["apshield"], None),
        "totaldamage": (["percentarmordamage*40"], None),
    },
    "ryze": {
        "modifiedshadowislesbonusdamage": (["shadowislesbasepercentage*100"], None),
        "modifieddemaciaexecutethreshold": (["demaciaexecutethreshold*100"], None),
        "modifiedfreljordtruedamage": (
            ["freljordtruedamagepercenthealth*base_hp"],
            None,
        ),
    },
    "sett": {
        "modifiedpercentoftargetmaxhealth": (["percentoftargetmaxhealth*100"], None),
    },
    "shyvana": {
        "modifieddivebombdamage": (["divebombaddamage"], None),
        "modifiedfiredamagepersecond": (
            ["firedamagetaddamagepersecond", "firedamageappersecond"],
            None,
        ),
    },
    "singed": {
        "modifiedmanapersec": (["manapercentas*0.7"], None),
    },
    "sion": {
        "modifiedshield": (["apshield", "percenthealthshield*base_hp"], None),
        "modifieddamage": (["damagepercenthealth*base_hp"], None),
    },
    "skarner": {
        "modifieddamage": (["damagepercentarmor*70"], None),
    },
    "swain": {
        "modifiedhanddamage": (["activedamage"], None),
        "totalhealing": (["aphealing", "percentmaximumhealthhealing*base_hp"], None),
    },
    "t-hex": {
        "modifiedlaserdamagepersecond": (["apdamage", "addamage"], None),
        "modifiedmissiledamage": (["apdamage", "addamage"], "missiledamagemult"),
    },
    "thresh": {
        "modifiedhealthdrain": (["appassivedamage"], None),
    },
    "tryndamere": {
        "modifieddurability": (["dr*100"], None),
    },
    "vi": {
        "modifiedsecondarydamage": (["secondaryaddamage"], None),
    },
    "viego": {
        "modifiedattackspeed": (["baseattackspeed"], None),
    },
    "volibear": {
        "modifiedbitedamage": (["bitedamagebase", "bitedamagehealth*base_hp"], None),
        "modifiedslamdamage": (
            ["bitedamagebase", "bitedamagehealth*base_hp"],
            "slamdamagemultiplier",
        ),
        "modifiedboltdamage": (
            ["stormbringerboltbase", "stormbringerbolthealth*base_hp"],
            None,
        ),
    },
    "warwick": {
        "modifiedtakedownattackspeed": (["allyattackspeed*100"], None),
    },
    "wukong": {
        "modifieddefenses": (["resists"], None),
        "modifiedclonehealth": (["summonmaxhealthpercent*base_hp"], None),
    },
    "yasuo": {
        "yasuoadpercent*100": (["base_ad"], None),
    },
    "yone": {
        "modifiedpertargetdamage": (["pertargetaddamage", "pertargetapdamage"], None),
        "modifiedstrikedamage": (["strikeaddamage", "strikeapdamage"], None),
    },
    "yunara": {
        "modifiedattackspeed": (["attackspeed*100"], None),
    },
    "yorick": {
        "modifiedheal": (["apheal"], None),
        "modifieddamage": (["flatdamage", "percenthealthdamage*base_hp"], None),
    },
    "zaahen": {
        "modifiedbigaoedamage": (["apdamage", "addamage"], "bigaoedamagemultiplier"),
        "modifieddamage": (["apdamage", "addamage"], "aoedamagemultiplier"),
    },
    "ziggs": {
        "modifiedbasicattackdamage": (["bapercentap"], None),
        "modifiedmindamage": (["minaoedamage"], None),
        "modifiedmaxdamage": (["maxaoedamage"], None),
    },
    "zilean": {
        "modifieddamage": (["magicdamage"], None),
        "modifiedsecondarydamage": (["explosiondamage"], None),
    },
}

GLOBAL_EXCEPTIONS = {
    "totaldamage": (["addamage", "apdamage"], None),
}

DECREASING_STATS = ["attacks", "mana", "requirement", "cooldown"]