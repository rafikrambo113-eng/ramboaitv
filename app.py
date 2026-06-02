# ═══════════════════════════════════════════════════════════════════════════
#  🔁 التحديثات المطلوب دمجها في صفحة 1 (استبدل الأجزاء دي بالكود الأصلي)
# ═══════════════════════════════════════════════════════════════════════════

# ─── استبدل NILESAT_LIVE_DB الموجودة بالكاملة بالـ dict ده ───

NILESAT_LIVE_DB = {
    # ── Religious - Christian ──
    "AL HAYAT":         {"frequency": 12207, "polarization": "Vertical",   "update_date": "2026-05-10"},
    "AL HAYAT 2":       {"frequency": 12207, "polarization": "Vertical",   "update_date": "2026-05-10"},
    "SAT-7 KIDS":       {"frequency": 11353, "polarization": "Vertical",   "update_date": "2026-04-18"},
    "SAT-7 ARABIC":     {"frequency": 11353, "polarization": "Vertical",   "update_date": "2026-04-18"},
    "SAT-7 PARS":       {"frequency": 11353, "polarization": "Vertical",   "update_date": "2026-04-18"},
    "ALKARMA ME 1":     {"frequency": 11096, "polarization": "Horizontal", "update_date": "2026-02-05"},
    "ALKARMA ME 2":     {"frequency": 11096, "polarization": "Horizontal", "update_date": "2026-02-05"},
    "AGHAPY TV":        {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-03-12"},
    "CTV":              {"frequency": 12022, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "NOURSAT":          {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-10"},
    "MESAT":            {"frequency": 11096, "polarization": "Horizontal", "update_date": "2026-01-10"},
    "MIRACLE CHANNEL":  {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-03-20"},
    # ── Religious - Islamic ──
    "IQRAA":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-01"},
    "MAJD":             {"frequency": 11862, "polarization": "Vertical",   "update_date": "2026-02-14"},
    "RAHMA":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-01"},
    "QURAN KAREEM":     {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-03-05"},
    "MAKKA TV":         {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-03-05"},
    # ── News ──
    "AL JAZEERA":       {"frequency": 10853, "polarization": "Vertical",   "update_date": "2026-05-20"},
    "AL JAZEERA HD":    {"frequency": 10853, "polarization": "Vertical",   "update_date": "2026-05-20"},
    "AL ARABIYA":       {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-15"},
    "AL HADATH":        {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-15"},
    "SKY NEWS ARABIA":  {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-03-30"},
    "CBC":              {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "EXTRA NEWS":       {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "ON E":             {"frequency": 12092, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "CAIRO NEWS":       {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-04-20"},
    "QATAR TV HD":      {"frequency": 10834, "polarization": "Horizontal", "update_date": "2026-05-14"},
    # ── Movies & Entertainment ──
    "MBC 2":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-20"},
    "MBC 4":            {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-20"},
    "MBC MAX":          {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-01-20"},
    "ROTANA CINEMA":    {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-02-01"},
    "ROTANA CLASSIC":   {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-02-01"},
    "ROTANA DRAMA":     {"frequency": 11938, "polarization": "Vertical",   "update_date": "2026-02-01"},
    "FOX MOVIES":       {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-03-10"},
    "AFLAM":            {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-02-28"},
    "AFLAM 2":          {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-02-28"},
    "MELODY AFLAM":     {"frequency": 11862, "polarization": "Vertical",   "update_date": "2026-01-15"},
    # ── Sports ──
    "ON TIME SPORTS 1": {"frequency": 11861, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "ON TIME SPORTS 2": {"frequency": 11861, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "ON TIME SPORTS 3": {"frequency": 11861, "polarization": "Vertical",   "update_date": "2026-05-01"},
    "SSC 1":            {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-04-10"},
    "SSC 2":            {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-04-10"},
    "AD SPORTS":        {"frequency": 11900, "polarization": "Vertical",   "update_date": "2026-03-15"},
    "AD SPORTS 2":      {"frequency": 11900, "polarization": "Vertical",   "update_date": "2026-03-15"},
    "KASS":             {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-02-20"},
    # ── Kids ──
    "SPACE TOON":       {"frequency": 11727, "polarization": "Vertical",   "update_date": "2026-01-05"},
    "MAJID":            {"frequency": 11862, "polarization": "Vertical",   "update_date": "2026-01-05"},
    "TOYOR ALJANNAH":   {"frequency": 11179, "polarization": "Horizontal", "update_date": "2026-02-10"},
    "CARTOON NETWORK":  {"frequency": 11843, "polarization": "Vertical",   "update_date": "2026-03-01"},
}


# ─── استبدل دالة ai_classify الموجودة بالكاملة بالدالة دي ───

def ai_classify(channel_name):
    name = channel_name.upper().strip()

    # ── ⛪ قنوات مسيحية ──
    CHRISTIAN_KW = [
        "CTV", "AGHAPY", "MESAT", "KARMA", "ALKARMA", "NOURSAT",
        "SAT-7", "SAT7", "AL HAYAT", "HAYAT TV", "MIRACLE",
        "COPTIC", "CHRISTIAN", "CHURCH", "CROSS", "GOSPEL",
        "MARYAM", "VIRGIN", "BISHOP", "POPE", "JESUS", "CHRIST",
        "FAITH", "HOPE CHANNEL", "3ABN"
    ]
    if any(w in name for w in CHRISTIAN_KW):
        return ALL_AVAILABLE_CATEGORIES[0]

    # ── 🕌 قنوات إسلامية ──
    ISLAMIC_KW = [
        "QURAN", "RAHMA", "MAJD", "MAKKA", "IQRAA", "IQRA",
        "HUDA", "WESAL", "ISLAM", "SUNNAH", "MADINAH",
        "AL RESALAH", "RESALAH", "SAFWA", "HIDAYA", "HIDAYAT",
        "AHLUL BAYT", "IMAM", "FIQH", "FATWA", "SALAH"
    ]
    if any(w in name for w in ISLAMIC_KW):
        return ALL_AVAILABLE_CATEGORIES[1]

    # ── 🎬 مسلسلات ودراما ──
    DRAMA_KW = [
        "MOSALSALAT", "DRAMA", "SERIES", "KHOLASA", "MASRAWI",
        "ROTANA DRAMA", "CBC DRAMA", "MELODY DRAMA",
        "MBC DRAMA", "SHAHID", "PLUS DRAMA", "AL HAYAT DRAMA"
    ]
    if any(w in name for w in DRAMA_KW):
        return ALL_AVAILABLE_CATEGORIES[2]

    # ── 🍿 أفلام عربية وأجنبية ──
    MOVIE_KW = [
        "CINEMA", "ROTANA", "AFLAM", "MIX", "FOX", "MBC2", "MBC 2",
        "MBC4", "MBC 4", "MBC MAX", "ACTION", "RAMBO", "MISHMISH",
        "MOVIE", "FILM", "AFLAM", "MELODY AFLAM", "OSCAR",
        "COMEDY", "FUN", "STAR MOVIES", "THRILLER", "HORROR",
        "PREMIERE", "PREMIERE HD", "SHOWTIME", "CINE"
    ]
    if any(w in name for w in MOVIE_KW):
        return ALL_AVAILABLE_CATEGORIES[3]

    # ── 👶 أطفال وكرتون ──
    KIDS_KW = [
        "SPACE TOON", "SPACETOON", "CN", "CARTOON", "MAJID",
        "KIDS", "TOM", "TOYOR", "BABY", "JUNIOR", "JUNIOR TV",
        "NICKELODEON", "NICK", "DISNEY", "JUNIOR DISNEY",
        "BOOMERANG", "JIM JAM", "MINIMAX", "LEGO", "MASHA"
    ]
    if any(w in name for w in KIDS_KW):
        return ALL_AVAILABLE_CATEGORIES[4]

    # ── ⚽ رياضة ──
    SPORT_KW = [
        "SPORT", "SPORTS", "ONTIME", "ON TIME", "KASS",
        "AD_SPORTS", "AD SPORTS", "SSC", "BEIN", "MATCH",
        "FOOTBALL", "SOCCER", "GOLF", "NBA", "UFC",
        "EXTREME", "EUROSPORT", "DSF", "FIGHTING", "WWE",
        "OLYMPIC", "VELODROME", "CYCLE", "RACING"
    ]
    if any(w in name for w in SPORT_KW):
        return ALL_AVAILABLE_CATEGORIES[5]

    # ── 📰 أخبار وسياسة ──
    NEWS_KW = [
        "NEWS", "JAZEERA", "ARABIYA", "HADATH", "CAIRO",
        "SKY NEWS", "BBC", "CNN", "FRANCE 24", "RT",
        "EXTRA NEWS", "CBC", "ON E", "SADA", "BALADI",
        "MASR", "MISR", "MASRAWY", "AHRAR", "EL WATAN",
        "ALARABY", "AL GHAD", "MEKAMELEEN", "HIWAR",
        "ALAAN", "ALAAN TV"
    ]
    if any(w in name for w in NEWS_KW):
        return ALL_AVAILABLE_CATEGORIES[6]

    # ── 📺 قنوات عامة ومنوعات (الافتراضي) ──
    return ALL_AVAILABLE_CATEGORIES[7]


# ─── استبدل NILESAT_NEW_CHANNELS الموجودة بالكاملة بالـ list دي ───

NILESAT_NEW_CHANNELS = [
    {"name": "RAMBO ACTION HD",    "frequency": 10834, "polarization": "Horizontal", "launch_date": "2026-01-15", "source": "Nilesat Official"},
    {"name": "MISHMISH CINEMA",    "frequency": 11938, "polarization": "Vertical",   "launch_date": "2026-04-10", "source": "KingOfSat Database"},
    {"name": "ON TIME SPORTS 4 HD","frequency": 11861, "polarization": "Vertical",   "launch_date": "2026-05-01", "source": "FlySat Live"},
    {"name": "AL JAZEERA MUBASHER","frequency": 10853, "polarization": "Vertical",   "launch_date": "2026-03-20", "source": "Nilesat Official"},
    {"name": "SSC EXTRA HD",       "frequency": 11843, "polarization": "Vertical",   "launch_date": "2026-04-25", "source": "FlySat Live"},
    {"name": "TOYOR ALJANNAH 2",   "frequency": 11179, "polarization": "Horizontal", "launch_date": "2026-02-10", "source": "KingOfSat Database"},
    {"name": "CBC DRAMA",          "frequency": 12092, "polarization": "Vertical",   "launch_date": "2026-05-05", "source": "Nilesat Official"},
]
