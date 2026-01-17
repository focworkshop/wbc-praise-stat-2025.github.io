#!/usr/bin/env python3
"""
Worship Journey 2025 - Data Processing and HTML Generation
Analyzes worship service data and generates a comprehensive statistics report.
"""

import csv
import re
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple, Optional

# ============================================================================
# SONG NAME MAPPINGS
# ============================================================================

# Canonical mappings for song name variants
SONG_NAME_MAPPINGS = {
    # Cornerstone variations
    "房角石頭（Cornerstone）": "Cornerstone 房角基石",
    "Cornerstone": "Cornerstone 房角基石",
    "房角基石": "Cornerstone 房角基石",

    # In Christ Alone
    "唯獨在基督裡 (In Christ Alone)": "唯獨在基督裡",

    # Amazing Grace variations
    "奇異恩典 Amazing Grace (My Chains are Gone)": "奇異恩典（除掉困鎖）",
    "奇異恩典(除掉困鎖)": "奇異恩典（除掉困鎖）",

    # Shout to the Lord
    "獻上頌讚": "獻上頌讚 (Shout To The Lord)",
    "獻上頌讚 Shout to The Lord": "獻上頌讚 (Shout To The Lord)",
    "獻上頌讚 Shout to the Lord": "獻上頌讚 (Shout To The Lord)",
    "Shout to The Lord 獻上頌讚": "獻上頌讚 (Shout To The Lord)",

    # King of Kings
    "King of Kings 萬代君主": "萬代君主",

    # Contrite spirit
    "憂傷痛悔的靈": "憂愁痛悔的靈",

    # Peace be with you
    "願您平安": "願你平安",

    # Ocean Will Part
    "海會分開（Ocean Will Part）": "Ocean Will Part",
    "海會分開": "Ocean Will Part",

    # Most beautiful sound
    "世界最美的聲音 (奇異恩典)": "世界最美的聲音",

    # Broaden life
    "讓生命寛宏": "讓生命寬宏",

    # Still
    "安靜 (Still)": "安靜 Still",

    # All because of Christ
    "全因基督": "全因基督",

    # Renew me again
    "再次讓我更新": "再次將我更新",

    # Jehovah Jireh
    "耶和華以勒 (同心圓)": "耶和華以勒",

    # Lord's Prayer
    "主禱文 (請教導我們禱告)": "主禱文（請教導我們禱告）",

    # New song name groupings
    "至愛的回嚮": "至愛的迴響",
    "新的異象，新的方向": "新的異象 新的方向",
    "坐在寶坐上聖潔羔羊": "坐在寶座上聖潔羔羊",
    "神真正心意 (The heart of worship)": "神真正心意 (The Heart of Worship)",

    # Day By Day
    "每一天 (Day By Day)": "每一天",

    # Amazing Grace variations
    "Amazing Grace (My Chains Are Gone) 奇異恩典": "奇異恩典（除掉困鎖）",
}

# ============================================================================
# PUBLISHER MAPPINGS
# ============================================================================

# Publisher consolidation mappings - maps variants to canonical name
PUBLISHER_MAPPINGS = {
    # 余子麟 group
    "Alan Yu": "余子麟",
    "林四": "余子麟",

    # Tsz-Lam Mak group
    "Tsz-Lam Mak": "麥子霖",

    # Stream of Praise group
    "Stream Of Praise Music": "Stream of Praise Music",
    "Stream of Praise": "Stream of Praise Music",
    "Steam of Praise": "Stream of Praise Music",
    "Stream of Praise Musice": "Stream of Praise Music",

    # Hong Kong Christian Music group
    "香港基督徒音樂協會": "香港基督徒音樂事工協會",
    "香港基督徒音事工協會": "香港基督徒音樂事工協會",
    "香港基督徒音樂事工協會(HKACM)": "香港基督徒音樂事工協會",

    # Salty Egg Music group
    "鹹蛋⾳樂事⼯": "鹹蛋音樂事工",
    "鹹蛋音樂事": "鹹蛋音樂事工",

    # Milk & Honey Worship group
    "©️Milk&Honey Worship": "Milk & Honey Worship",
    "Milk&Honey Worship": "Milk & Honey Worship",

    # Herald Crusades group
    "角聲佈道團": "角聲使團",

    # One Circle group
    "One Circle Limited": "One Circle Ltd",
    "同心圓敬拜福音平台": "One Circle Ltd",

    # Flow Church group
    "Flow Music, Flow Church": "Flow Church",
    "Flow Music": "Flow Church",

    # Gsus Music Ministry group
    "Gsus Music Ministry": "Gsus Music Ministry Ltd",

    # Esther Chow group
    "周敏曦": "Esther Chow",

    # AFC Vancouver group
    "AFC": "AFC Vancouver",
    "加拿大基督使者協會": "AFC Vancouver",

    # Ruth Chen group
    "Ruth Chen Music": "曾路得",
    "Ruth Chen": "曾路得",

    # Worship Nations group
    "Worship Nations / 玻璃海樂團": "Worship Nations",
    "Worship Nations X 玻璃海樂團": "Worship Nations",
    "Worship Nation": "Worship Nations",
    "© 2019 Worship Nations": "Worship Nations",
    "玻璃海樂團": "Worship Nations",

    # Grace Melodia group
    "頌恩旋律": "Grace Melodia",
    "Kyrios Culture Association": "Grace Melodia",

    # CantonHymn group
    "Cantonhymn": "CantonHymn",

    # Son Music group
    "Public Domain, Son Music Worship Ministry": "Son Music",
}

# Publisher display name mappings - for changing how publishers are displayed in UI
# Maps canonical publisher name to preferred display name
PUBLISHER_DISPLAY_NAMES = {
    "余子麟": "林四",
    "Grace Melodia": "頌恩旋律",
    "麥子霖": "Tsz-Lam Mak",
    "Worship Nations": "Worship Nations/玻璃海樂團",
}

# ============================================================================
# STATIC SONG COPYRIGHT MAPPINGS
# ============================================================================

# Static mappings for specific songs to their copyright owners
# These override the fuzzy matching logic
STATIC_SONG_COPYRIGHT_MAPPINGS = {
    "小小的雙手": "玻璃海樂團",
    "是為祢預備": "Milk & Honey Worship",
    "仍然敬拜": "Flow Church",
    "最美好的仗": "香港基督徒音樂事工協會",
    "主超過我在面對的紅海": "RedSea Music",
    "讚頌未停": "頌恩旋律",
    "坐在寶座上聖潔羔羊": "Stream of Praise Music",
    "我屬祢": "鹹蛋音樂事工",
    # Additional mappings from photo - ONLY those with red text visible
    "到那日": "Gsus Music Ministry Ltd",
    "天父...": "Esther Chow",
    "天父⋯": "Esther Chow",  # Alternative ellipsis character
    "Great Is Thy Faithfulness 主恩何信實": "香港基督徒音樂事工協會",
    "遇於祢": "Worship Nations",
    "連於祢": "Worship Nations",
    "賜我自由": "Stream of Praise Music",
    "𧶽我自由": "Stream of Praise Music",  # Character encoding variant
    "垂絲柳樹下": "Worship Nations",
}

# Songs that should explicitly have NO publisher (medleys, compilations, etc.)
# Map to None to force them to be unmatched
SONGS_WITHOUT_PUBLISHER = {
    "Christmas2025（信眾齊到主前, 祢是彌賽亞, 祢配得, 君尊義僕, 好信息, 神同在, 榮美屬祢）",
}

# ============================================================================
# DATA LOADING AND PARSING
# ============================================================================

def load_csv_data(filepath: str) -> List[Dict]:
    """
    Load and parse CSV data with proper encoding and multi-line handling.

    Returns list of service records with normalized data.
    """
    services = []

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        rows = list(reader)
        consolidated_rows = consolidate_multiline_rows(rows)

        for row in consolidated_rows:
            if len(row) < 16:  # Skip incomplete rows
                continue

            date_str = row[0].strip() if row[0] else None
            if not date_str:  # Skip empty date rows
                continue

            # Parse date
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                continue

            # Extract praise leader
            praise_leader = normalize_leader_name(row[1])
            if not praise_leader:
                continue

            # Extract songs from columns
            praise1_songs = extract_songs_from_columns(row, [3, 5, 7])
            praise2_songs = extract_songs_from_columns(row, [9, 11, 13])
            peace_songs = extract_songs_from_columns(row, [15])

            service = {
                'date': date,
                'year': date.year,
                'month': date.month,
                'weekday': date.weekday(),  # 5 = Saturday, 6 = Sunday
                'praise_leader': praise_leader,
                'theme': row[2].strip() if len(row) > 2 else '',
                'praise1': praise1_songs,
                'praise2': praise2_songs,
                'peace': peace_songs,
                'all_songs': praise1_songs + praise2_songs + peace_songs
            }

            services.append(service)

    return services


def consolidate_multiline_rows(rows: List[List[str]]) -> List[List[str]]:
    """
    Merge rows where the date column is empty (continuation of previous row).
    """
    consolidated = []
    current_row = None

    for row in rows:
        # Ensure row has enough columns
        while len(row) < 17:
            row.append('')

        if row[0] and row[0].strip():  # Has date - new record
            if current_row:
                consolidated.append(current_row)
            current_row = row.copy()
        else:  # Continuation of previous row
            if current_row:
                # Merge non-empty cells
                for i in range(1, len(row)):
                    if row[i] and row[i].strip():
                        if current_row[i]:
                            current_row[i] += ' ' + row[i].strip()
                        else:
                            current_row[i] = row[i].strip()

    if current_row:
        consolidated.append(current_row)

    return consolidated


def load_copyright_metadata() -> Dict[str, str]:
    """
    Load copyright metadata from songindex CSV file.
    Returns a dictionary mapping song names to copyright owners.
    """
    metadata = {}

    try:
        with open('songindex_20260116.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                # Skip header rows and empty rows
                if len(row) < 5:
                    continue
                if row[0].strip() in ['', 'Number', 'Last Updated:']:
                    continue

                # Extract song name (column 1) and copyright (column 4)
                song_name = row[1].strip()
                copyright_owner = row[4].strip()

                # Skip if song name or copyright is empty
                if not song_name or not copyright_owner:
                    continue

                metadata[song_name] = copyright_owner

    except FileNotFoundError:
        print("Warning: songindex_20260116.csv not found. Copyright data will be unavailable.")

    return metadata


def normalize_for_comparison(s: str) -> str:
    """
    Normalize a song name for comparison purposes.
    - Case-insensitive
    - Whitespace removed
    - Full-width/half-width punctuation normalized
    - Character variants (你/袮 → 祢) normalized

    Args:
        s: The song name to normalize

    Returns:
        Normalized string for comparison
    """
    if not s:
        return ''
    # Replace character variants with 祢
    s = s.replace('你', '祢').replace('袮', '祢')
    # Normalize full-width/half-width punctuation
    s = s.replace('（', '(').replace('）', ')').replace('，', ',')
    s = s.replace('。', '.').replace('：', ':').replace('！', '!').replace('？', '?')
    # Remove whitespace and convert to lowercase for comparison
    s = ''.join(s.split()).lower()
    return s


def load_historical_songs(csv_path: str = 'uniquesong_until2024.csv') -> Set[str]:
    """
    Load the list of songs that existed before 2025 from uniquesong_until2024.csv.

    A "new song" is defined as a song that exists in 2025 but not in this file.

    Args:
        csv_path: Path to the uniquesong_until2024.csv file

    Returns:
        Set of normalized song names (for comparison) from before 2025
    """
    historical_songs = set()
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                song = line.strip()
                if song:
                    # Split by '+' or '/' if present (e.g., "Song1 + Song2" or "Song1 / Song2")
                    if '+' in song or '/' in song:
                        song_parts = [part.strip() for part in re.split(r'\s*[+/]\s*', song)]
                    else:
                        song_parts = [song]

                    # Apply comparison normalization for each part
                    for part in song_parts:
                        cleaned = clean_song_name(part)
                        if cleaned:
                            # Use comparison normalization for set membership
                            historical_songs.add(normalize_for_comparison(cleaned))
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found. New song detection will be unavailable.")
    return historical_songs


def consolidate_publisher_name(publisher: str) -> str:
    """
    Consolidate publisher names according to PUBLISHER_MAPPINGS.

    Args:
        publisher: Original publisher name from metadata

    Returns:
        Canonical publisher name
    """
    if publisher in PUBLISHER_MAPPINGS:
        return PUBLISHER_MAPPINGS[publisher]
    return publisher


def get_publisher_display_name(publisher: str) -> str:
    """
    Get the display name for a publisher.

    Args:
        publisher: Canonical publisher name

    Returns:
        Display name if mapping exists, otherwise the original name
    """
    if publisher in PUBLISHER_DISPLAY_NAMES:
        return PUBLISHER_DISPLAY_NAMES[publisher]
    return publisher


def map_song_to_copyright(song_name: str, copyright_metadata: Dict[str, str]) -> Optional[str]:
    """
    Map a cleaned song name to its copyright owner using fuzzy matching.

    Args:
        song_name: The cleaned song name from praisehistory
        copyright_metadata: Dictionary mapping metadata song names to copyright owners

    Returns:
        Copyright owner name or None if no match found
    """
    if not copyright_metadata:
        return None

    # Use the shared normalize_for_comparison function
    normalize = normalize_for_comparison

    normalized_song = normalize(song_name)

    # Strategy -1: Check exclusion list first (songs that should have NO publisher)
    for excluded_song in SONGS_WITHOUT_PUBLISHER:
        if normalize(excluded_song) == normalized_song:
            return None

    # Strategy 0: Check static mappings first (highest priority)
    for static_song, static_publisher in STATIC_SONG_COPYRIGHT_MAPPINGS.items():
        if normalize(static_song) == normalized_song:
            return consolidate_publisher_name(static_publisher)

    # Strategy 1: Try exact match
    for metadata_song, copyright in copyright_metadata.items():
        normalized_metadata = normalize(metadata_song)
        if normalized_song == normalized_metadata:
            return consolidate_publisher_name(copyright)

    # Strategy 2: Check if cleaned song contains metadata song (substring)
    for metadata_song, copyright in copyright_metadata.items():
        normalized_metadata = normalize(metadata_song)
        if normalized_metadata and normalized_metadata in normalized_song:
            return consolidate_publisher_name(copyright)

    # Strategy 3: Check if metadata song contains cleaned song (reverse substring)
    for metadata_song, copyright in copyright_metadata.items():
        normalized_metadata = normalize(metadata_song)
        if normalized_song and normalized_song in normalized_metadata:
            return consolidate_publisher_name(copyright)

    # Strategy 4: Try matching against canonical song names from SONG_NAME_MAPPINGS
    # Check if the song_name appears in the mappings dictionary values
    for original_variant, canonical_name in SONG_NAME_MAPPINGS.items():
        if normalize(canonical_name) == normalized_song:
            # Try to match the original variant with metadata
            for metadata_song, copyright in copyright_metadata.items():
                normalized_metadata = normalize(metadata_song)
                normalized_variant = normalize(original_variant)
                if normalized_metadata in normalized_variant or normalized_variant in normalized_metadata:
                    return consolidate_publisher_name(copyright)

    return None


def get_all_publishers_from_metadata(copyright_metadata: Dict[str, str]) -> List[str]:
    """
    Extract unique publisher names from copyright metadata.

    Args:
        copyright_metadata: Dictionary mapping song names to copyright owners

    Returns:
        Sorted list of unique publisher names (consolidated)
    """
    publishers = set()
    for publisher in copyright_metadata.values():
        publishers.add(consolidate_publisher_name(publisher))
    return sorted(publishers)


def extract_songs_from_columns(row: List[str], indices: List[int]) -> List[str]:
    """
    Extract and clean songs from specified column indices.
    Handles combined songs and empty cells.
    """
    songs = []

    for idx in indices:
        if idx >= len(row):
            continue

        cell = row[idx].strip() if row[idx] else ''
        if not cell:
            continue

        # Split combined songs
        song_parts = split_combined_songs(cell)

        for song in song_parts:
            cleaned = clean_song_name(song)
            if cleaned:
                songs.append(cleaned)

    return songs


def split_combined_songs(song_text: str) -> List[str]:
    """
    Handle patterns like:
    - "Song1 + Song2"
    - "Song1 / Song2"
    - "Song1 + Communion"
    - "Song1 V1 V2 + Song2"
    """
    if not song_text:
        return []

    # Handle Communion markers specially
    song_text = re.sub(r'\s*\+\s*Communion\s*', '', song_text)

    # Split by common delimiters
    parts = re.split(r'\s*\+\s*|\s*/\s*', song_text)

    # Further filter out pure V1 V2, C1 C2 patterns
    filtered = []
    for part in parts:
        part = part.strip()
        # Skip pure verse/chorus markers
        if re.match(r'^[VC]\d+(\s+[VC]\d+)*$', part):
            continue
        # Remove trailing verse markers
        part = re.sub(r'\s+V\d+(\s+V\d+)*\s*$', '', part)
        part = re.sub(r'\s+C\d+(\s+C\d+)*\s*$', '', part)
        part = re.sub(r'\s+B\s*$', '', part)
        if part:
            filtered.append(part)

    return filtered if filtered else []


def clean_song_name(song: str) -> str:
    """
    Normalize song names:
    - Normalize character variants (你 → 祢)
    - Normalize full-width/half-width punctuation
    - Remove suffixes/annotations
    - Apply canonical name mappings
    - Normalize whitespace and punctuation
    - Preserve Chinese/English characters
    """
    if not song:
        return None

    # Character normalization: normalize 你/祢/袮 to 祢 for consistency
    # This makes "願祢國度彰顯" = "願你國度彰顯" = "願袮國度彰顯"
    song = song.replace('你', '祢')
    song = song.replace('袮', '祢')

    # Normalize full-width/half-width punctuation (full-width → half-width)
    song = song.replace('（', '(')
    song = song.replace('）', ')')
    song = song.replace('，', ',')
    song = song.replace('。', '.')
    song = song.replace('：', ':')
    song = song.replace('！', '!')
    song = song.replace('？', '?')

    # Remove specific suffixes and annotations (case-insensitive where needed)
    # Remove artist attribution patterns like "by Esther Chow"
    song = re.sub(r'\s+by\s+[A-Za-z\s]+$', '', song, flags=re.IGNORECASE)

    # Remove medley/chorus indicators
    song = re.sub(r'\s*\bMedl?ey\b\s*', '', song, flags=re.IGNORECASE)
    song = re.sub(r'\s*\bChorus\s+Only\b\s*', '', song, flags=re.IGNORECASE)

    # Remove language/version annotations
    song = re.sub(r'\s*\(Canto\)\s*', '', song, flags=re.IGNORECASE)
    song = re.sub(r'\s*\(Mando\)\s*', '', song, flags=re.IGNORECASE)
    song = re.sub(r'\s*\(skip\s+verse\)\s*', '', song, flags=re.IGNORECASE)

    # Remove chorus/verse indicators like "C1 C2"
    song = re.sub(r'\s+[CV]\d+(\s+[CV]\d+)*\s*$', '', song)

    # Normalize whitespace
    song = ' '.join(song.split())

    # Remove trailing punctuation
    song = song.rstrip(',.;:')

    # Normalize quotes
    song = song.replace('"', '"').replace('"', '"')
    song = song.replace(''', "'").replace(''', "'")

    song = song.strip()

    # Check if song is just a non-song marker (Communion, Baptism, etc.)
    # These should be filtered out completely
    if song.lower() in ['communion', 'holy communion', 'baptism']:
        return None

    if not song:
        return None

    # Apply canonical name mappings
    if song in SONG_NAME_MAPPINGS:
        song = SONG_NAME_MAPPINGS[song]

    return song if song else None


def normalize_leader_name(leader: str) -> str:
    """
    Normalize praise leader names:
    - Remove annotations like "(HC)", "(AGW)"
    - Handle prefixes like "P1:", "P2:", "A:", "B:", "C:"
    - Trim whitespace
    """
    if not leader:
        return None

    # Remove annotations in parentheses
    leader = re.sub(r'\s*\([^)]*\)', '', leader)

    # Remove prefixes like "P1:", "P2:", "A:", "B:", "C:", etc.
    # Pattern: single letter, optional digits, colon, optional whitespace
    leader = re.sub(r'^[A-Z]\d*:\s*', '', leader)

    # Handle joint worship - take first leader
    if '/' in leader or '&' in leader:
        leader = re.split(r'[/&]', leader)[0]

    leader = leader.strip()

    return leader if leader else None


# ============================================================================
# STATISTICS CALCULATION - SECTION A (PER LEADER)
# ============================================================================

def calculate_leader_stats(services: List[Dict], historical_songs_set: Set[str], year: int = 2025) -> Dict[str, Dict]:
    """
    Calculate statistics for each praise leader in the specified year.

    Args:
        services: List of service records
        historical_songs_set: Set of songs from uniquesong_until2024.csv for new song detection
        year: The year to calculate statistics for
    """
    # Filter services by year
    year_services = [s for s in services if s['year'] == year]

    # Load copyright metadata for publisher calculations
    copyright_metadata = load_copyright_metadata()

    # Group services by leader
    leader_services = defaultdict(list)
    for service in year_services:
        leader_services[service['praise_leader']].append(service)

    # Calculate stats for each leader
    stats = {}

    for leader, leader_svc_list in leader_services.items():
        # Count services
        total_services = len(leader_svc_list)

        # Count songs by category
        praise1_counter = Counter()
        praise2_counter = Counter()
        peace_counter = Counter()
        all_songs_counter = Counter()
        all_songs_set = set()

        for svc in leader_svc_list:
            praise1_counter.update(svc['praise1'])
            praise2_counter.update(svc['praise2'])
            peace_counter.update(svc['peace'])
            all_songs_counter.update(svc['all_songs'])
            all_songs_set.update(svc['all_songs'])

        # Total songs count
        total_songs = sum(all_songs_counter.values())

        # Top 20 lists - filter out songs with only 1 occurrence
        praise1_top20 = [(song, count) for song, count in praise1_counter.most_common(20) if count > 1]
        praise2_top20 = [(song, count) for song, count in praise2_counter.most_common(20) if count > 1]
        peace_top20 = [(song, count) for song, count in peace_counter.most_common(20) if count > 1]
        combined_top20 = [(song, count) for song, count in all_songs_counter.most_common(20) if count > 1]

        # New songs in 2025 (not in uniquesong_until2024.csv)
        # Compare using normalized form (case-insensitive, whitespace removed)
        new_songs_2025 = sorted([
            song for song in all_songs_set
            if normalize_for_comparison(song) not in historical_songs_set
        ])

        # Calculate overlap with other leaders
        other_leaders_songs = set()
        for other_leader, other_svc_list in leader_services.items():
            if other_leader != leader:
                for svc in other_svc_list:
                    other_leaders_songs.update(svc['all_songs'])

        common_songs_count = len(all_songs_set & other_leaders_songs)

        # Find top 2 leaders with most common songs
        leader_overlap_counts = []
        for other_leader, other_svc_list in leader_services.items():
            if other_leader != leader:
                other_songs = set()
                for svc in other_svc_list:
                    other_songs.update(svc['all_songs'])
                overlap_count = len(all_songs_set & other_songs)
                if overlap_count > 0:
                    leader_overlap_counts.append((other_leader, overlap_count))

        leader_overlap_counts.sort(key=lambda x: x[1], reverse=True)
        top2_leaders_overlap = leader_overlap_counts[:2]

        # Calculate publisher statistics for this leader (excluding peace songs)
        publisher_counter = Counter()
        praise_only_counter = Counter()  # Count of praise1 + praise2 songs (excluding peace)
        unmatched_count = 0  # Track unmatched songs

        for svc in leader_svc_list:
            praise_only_counter.update(svc['praise1'] + svc['praise2'])

        # Map each praise song to its publisher
        for song, count in praise_only_counter.items():
            copyright_owner = map_song_to_copyright(song, copyright_metadata)
            if copyright_owner is not None:
                publisher_counter[copyright_owner] += count
            else:
                unmatched_count += count

        # Calculate total songs (excluding peace)
        total_praise_songs = sum(praise_only_counter.values())

        # Calculate percentages for each publisher
        publisher_percentages = []
        for publisher, count in publisher_counter.most_common():
            percentage = (count / total_praise_songs * 100) if total_praise_songs > 0 else 0
            publisher_percentages.append((publisher, percentage, count))

        # Add unmatched songs row if there are any
        if unmatched_count > 0:
            unmatched_percentage = (unmatched_count / total_praise_songs * 100) if total_praise_songs > 0 else 0
            publisher_percentages.append(("__UNMATCHED__", unmatched_percentage, unmatched_count))

        stats[leader] = {
            'name': leader,
            'total_services': total_services,
            'total_songs': total_songs,
            'praise1_top20': praise1_top20,
            'praise2_top20': praise2_top20,
            'peace_top20': peace_top20,
            'combined_top20': combined_top20,
            'new_songs_2025': new_songs_2025,
            'common_songs_count': common_songs_count,
            'top2_leaders_overlap': top2_leaders_overlap,
            'publisher_percentages': publisher_percentages
        }

    return stats


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_unique_songs_2025(services: List[Dict]) -> List[str]:
    """
    Get a sorted list of all unique song names from 2025.

    Args:
        services: List of all service records

    Returns:
        Sorted list of unique song names from 2025
    """
    year_services = [s for s in services if s['year'] == 2025]
    all_songs = set()

    for service in year_services:
        all_songs.update(service['all_songs'])

    return sorted(all_songs)


def calculate_publisher_stats(services: List[Dict], year: int = 2025) -> Dict:
    """
    Calculate publisher/copyright statistics for all songs in the specified year.

    Args:
        services: List of all service records
        year: Year to calculate statistics for

    Returns:
        Dictionary containing top20_publishers (excluding peace),
        top20_praise1, top20_praise2, top20_peace, unmatched_songs, and all_publishers
    """
    # Filter services by year
    year_services = [s for s in services if s['year'] == year]

    # Load copyright metadata
    copyright_metadata = load_copyright_metadata()
    all_publishers = get_all_publishers_from_metadata(copyright_metadata)

    # Count songs - separated by category
    all_songs_counter = Counter()
    praise1_counter = Counter()
    praise2_counter = Counter()
    peace_counter = Counter()
    praise_only_counter = Counter()  # Praise1 + Praise2 (excluding peace)

    # Publisher counters for different categories
    copyright_counter = Counter()  # Praise only (excluding peace)
    copyright_to_songs = defaultdict(list)  # Praise only

    copyright_praise1_counter = Counter()
    copyright_praise1_to_songs = defaultdict(list)

    copyright_praise2_counter = Counter()
    copyright_praise2_to_songs = defaultdict(list)

    copyright_peace_counter = Counter()
    copyright_peace_to_songs = defaultdict(list)

    unmatched_songs = []  # Songs with no publisher match

    for svc in year_services:
        all_songs_counter.update(svc['all_songs'])
        praise1_counter.update(svc['praise1'])
        praise2_counter.update(svc['praise2'])
        peace_counter.update(svc['peace'])
        praise_only_counter.update(svc['praise1'] + svc['praise2'])

    # Map praise1 songs to publishers
    for song, count in praise1_counter.items():
        copyright_owner = map_song_to_copyright(song, copyright_metadata)
        if copyright_owner is not None:
            copyright_praise1_counter[copyright_owner] += count
            copyright_praise1_to_songs[copyright_owner].append((song, count))

    # Map praise2 songs to publishers
    for song, count in praise2_counter.items():
        copyright_owner = map_song_to_copyright(song, copyright_metadata)
        if copyright_owner is not None:
            copyright_praise2_counter[copyright_owner] += count
            copyright_praise2_to_songs[copyright_owner].append((song, count))

    # Map peace songs to publishers
    for song, count in peace_counter.items():
        copyright_owner = map_song_to_copyright(song, copyright_metadata)
        if copyright_owner is not None:
            copyright_peace_counter[copyright_owner] += count
            copyright_peace_to_songs[copyright_owner].append((song, count))

    # Map praise-only songs to publishers (excluding peace)
    for song, count in praise_only_counter.items():
        copyright_owner = map_song_to_copyright(song, copyright_metadata)
        if copyright_owner is None:
            unmatched_songs.append((song, count))
        else:
            copyright_counter[copyright_owner] += count
            copyright_to_songs[copyright_owner].append((song, count))

    # Generate subsection 1: Top 20 publishers (praise only, excluding peace)
    top20_publishers = []
    for publisher, total_count in copyright_counter.most_common(20):
        songs_list = sorted(copyright_to_songs[publisher], key=lambda x: x[1], reverse=True)
        top10_songs = songs_list[:10]  # Limit to top 10 songs
        top20_publishers.append((publisher, total_count, top10_songs))

    # Generate subsection 1a: Top 20 publishers for Praise1
    top20_praise1 = []
    for publisher, total_count in copyright_praise1_counter.most_common(20):
        songs_list = sorted(copyright_praise1_to_songs[publisher], key=lambda x: x[1], reverse=True)
        top10_songs = songs_list[:10]  # Limit to top 10 songs
        top20_praise1.append((publisher, total_count, top10_songs))

    # Generate subsection 1b: Top 20 publishers for Praise2
    top20_praise2 = []
    for publisher, total_count in copyright_praise2_counter.most_common(20):
        songs_list = sorted(copyright_praise2_to_songs[publisher], key=lambda x: x[1], reverse=True)
        top10_songs = songs_list[:10]  # Limit to top 10 songs
        top20_praise2.append((publisher, total_count, top10_songs))

    # Generate subsection 1c: Top 20 publishers for Peace
    top20_peace = []
    for publisher, total_count in copyright_peace_counter.most_common(20):
        songs_list = sorted(copyright_peace_to_songs[publisher], key=lambda x: x[1], reverse=True)
        top10_songs = songs_list[:10]  # Limit to top 10 songs
        top20_peace.append((publisher, total_count, top10_songs))

    # Generate subsection 2: Unmatched songs (sorted by count descending)
    unmatched_songs_sorted = sorted(unmatched_songs, key=lambda x: x[1], reverse=True)

    # Generate subsection 3: All publishers
    all_publishers_list = []
    for publisher in all_publishers:
        count = copyright_counter.get(publisher, 0)
        songs = sorted(copyright_to_songs.get(publisher, []), key=lambda x: x[1], reverse=True)
        all_publishers_list.append((publisher, count, songs))

    # Sort by count descending, then by publisher name
    all_publishers_list.sort(key=lambda x: (-x[1], x[0]))

    return {
        'top20_publishers': top20_publishers,
        'top20_praise1': top20_praise1,
        'top20_praise2': top20_praise2,
        'top20_peace': top20_peace,
        'unmatched_songs': unmatched_songs_sorted,
        'all_publishers': all_publishers_list,
    }


# ============================================================================
# STATISTICS CALCULATION - SECTION B (GLOBAL)
# ============================================================================

def calculate_global_stats(services: List[Dict], historical_songs_set: Set[str], year: int = 2025) -> Dict:
    """
    Calculate global statistics for all services in the specified year.

    Args:
        services: List of service records
        historical_songs_set: Set of songs from uniquesong_until2024.csv for new song detection
        year: The year to calculate statistics for
    """
    # Filter services by year
    year_services = [s for s in services if s['year'] == year]
    previous_year_services = [s for s in services if s['year'] == year - 1]

    # Count songs by category
    praise1_counter = Counter()
    praise2_counter = Counter()
    praise1_praise2_combined_counter = Counter()
    peace_counter = Counter()
    all_songs_counter = Counter()
    all_songs_set = set()

    # Track which leaders chose which songs (for multi-leader analysis)
    song_to_leaders = defaultdict(set)

    for svc in year_services:
        praise1_counter.update(svc['praise1'])
        praise2_counter.update(svc['praise2'])
        praise1_praise2_combined_counter.update(svc['praise1'] + svc['praise2'])
        peace_counter.update(svc['peace'])
        all_songs_counter.update(svc['all_songs'])
        all_songs_set.update(svc['all_songs'])

        # Track leaders for praise1 and praise2 songs (excluding peace)
        for song in svc['praise1'] + svc['praise2']:
            song_to_leaders[song].add(svc['praise_leader'])

    # Total unique songs
    total_unique_songs = len(all_songs_set)

    # Top 20 lists
    praise1_top20 = praise1_counter.most_common(20)
    praise2_top20 = praise2_counter.most_common(20)
    combined_top20 = praise1_praise2_combined_counter.most_common(20)

    # Top 10 songs chosen by at least 3 leaders (excluding peace)
    multi_leader_songs = []
    for song, leaders in song_to_leaders.items():
        if len(leaders) >= 3:
            count = praise1_praise2_combined_counter[song]
            multi_leader_songs.append((song, len(leaders), sorted(leaders), count))

    # Sort by number of leaders (desc), then by occurrence count (desc)
    multi_leader_songs.sort(key=lambda x: (x[1], x[3]), reverse=True)
    top10_multi_leader = multi_leader_songs[:10]

    # Top 3 peace songs
    peace_top3 = peace_counter.most_common(3)

    # New songs in 2025 (not in uniquesong_until2024.csv)
    # Compare using normalized form (case-insensitive, whitespace removed)
    new_songs_2025 = sorted([
        song for song in all_songs_set
        if normalize_for_comparison(song) not in historical_songs_set
    ])

    # All unique songs in 2025 (alphabetically sorted)
    unique_songs_2025 = sorted(all_songs_set)

    return {
        'total_unique_songs': total_unique_songs,
        'praise1_top20': praise1_top20,
        'praise2_top20': praise2_top20,
        'combined_top20': combined_top20,
        'top10_multi_leader': top10_multi_leader,
        'peace_top3': peace_top3,
        'new_songs_2025': new_songs_2025,
        'unique_songs_2025': unique_songs_2025
    }


def calculate_new_song_usage_stats(services: List[Dict], historical_songs_set: Set[str], year: int = 2025) -> Dict:
    """
    Calculate new song usage statistics for worship services.

    For each category (combined, saturday, sunday), counts:
    - Total number of worship services
    - Number of services where a new song appeared for the first time (in that category)
    - Percentage of services with new song introductions

    The "first occurrence" rule means if a new song appears multiple times,
    only the first service in that category counts.

    Args:
        services: List of service records
        historical_songs_set: Set of normalized song names from before 2025
        year: The year to calculate statistics for

    Returns:
        Dictionary with stats for 'combined', 'saturday', and 'sunday'
    """
    # Filter services by year and sort by date
    year_services = sorted(
        [s for s in services if s['year'] == year],
        key=lambda x: x['date']
    )

    # Separate by day of week
    saturday_services = [s for s in year_services if s['weekday'] == 5]
    sunday_services = [s for s in year_services if s['weekday'] == 6]

    def count_worships_with_new_songs(service_list: List[Dict]) -> Tuple[int, List[str]]:
        """Count worships that introduce a new song (first occurrence only).

        Returns:
            Tuple of (count, list of date strings with song names e.g. "2025-1-18(song1,song2)")
        """
        seen_new_songs = set()
        worships_with_new = 0
        dates_with_new = []

        for svc in service_list:
            new_songs_in_service = []
            for song in svc['all_songs']:
                normalized = normalize_for_comparison(song)
                # Check if this is a new song (not in historical set)
                if normalized not in historical_songs_set:
                    # Check if this is the first time we see it in this category
                    if normalized not in seen_new_songs:
                        new_songs_in_service.append(song)
                        seen_new_songs.add(normalized)

            if new_songs_in_service:
                worships_with_new += 1
                # Format date without leading zeros (Windows compatible)
                date_str = f"{svc['date'].year}-{svc['date'].month}-{svc['date'].day}"
                songs_str = ','.join(new_songs_in_service)
                dates_with_new.append(f"{date_str}({songs_str})")

        return worships_with_new, dates_with_new

    # Calculate for each category
    combined_total = len(year_services)
    combined_with_new, combined_dates = count_worships_with_new_songs(year_services)
    combined_pct = (combined_with_new / combined_total * 100) if combined_total > 0 else 0

    saturday_total = len(saturday_services)
    saturday_with_new, saturday_dates = count_worships_with_new_songs(saturday_services)
    saturday_pct = (saturday_with_new / saturday_total * 100) if saturday_total > 0 else 0

    sunday_total = len(sunday_services)
    sunday_with_new, sunday_dates = count_worships_with_new_songs(sunday_services)
    sunday_pct = (sunday_with_new / sunday_total * 100) if sunday_total > 0 else 0

    return {
        'combined': {
            'total_worships': combined_total,
            'worships_with_new_songs': combined_with_new,
            'percentage': combined_pct
        },
        'saturday': {
            'total_worships': saturday_total,
            'worships_with_new_songs': saturday_with_new,
            'percentage': saturday_pct,
            'dates': saturday_dates
        },
        'sunday': {
            'total_worships': sunday_total,
            'worships_with_new_songs': sunday_with_new,
            'percentage': sunday_pct,
            'dates': sunday_dates
        }
    }


# ============================================================================
# HTML GENERATION
# ============================================================================

# Global variable to store new songs from 2025
NEW_SONGS_2025 = set()

def format_song_name(song: str) -> str:
    """
    Format song name with dot indicator if it's a new song in 2025.

    Args:
        song: The song name

    Returns:
        Formatted song name with dot indicator if new
    """
    if song in NEW_SONGS_2025:
        return f'<span class="new-song-indicator" title="New Song: 2025 was the first time this song appeared">●</span> {song}'
    return song

def generate_html(leader_stats: Dict, global_stats: Dict, publisher_stats: Dict, output_path: str):
    """
    Generate self-contained HTML file with embedded CSS and JavaScript.
    """
    global NEW_SONGS_2025
    # Store new songs for use in formatting
    NEW_SONGS_2025 = set(global_stats['new_songs_2025'])

    # Sort leaders alphabetically for consistent display
    sorted_leaders = sorted(leader_stats.keys())

    # Generate leader sections HTML
    leader_sections_html = ''
    for leader in sorted_leaders:
        stats = leader_stats[leader]
        leader_sections_html += generate_leader_section(stats)

    # Generate global section HTML
    global_section_html = generate_global_section(global_stats)

    # Generate publisher section HTML
    publisher_section_html = generate_publisher_section(publisher_stats)

    # Generate navigation menu
    nav_menu_html = generate_nav_menu(sorted_leaders)

    # Complete HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="WBC CM Worship Journey 2025">
    <meta name="author" content="Agentic coded by Michael Hui">
    <title>WBC CM Worship Journey 2025</title>
    <style>
        {get_embedded_css()}
    </style>
</head>
<body>
    <nav class="main-nav">
        {nav_menu_html}
    </nav>

    <header class="hero">
        <h1>WBC CM Worship Journey 2025</h1>
        <p class="subtitle">Comprehensive statistics on the selection of praise songs</p>
    </header>

    <main>
        <section id="section-a" class="section">
            <div class="section-header">
                <h2>Section A: Praise Leaders Rewind 2025</h2>
                <p class="section-description">Individual statistics for each praise leader</p>
            </div>
            <div class="leaders-container">
                {leader_sections_html}
            </div>
        </section>

        <section id="section-b" class="section">
            <div class="section-header">
                <h2>Section B: Praise History 2025</h2>
                <p class="section-description">Global worship statistics across all services</p>
            </div>
            <div class="global-container">
                {global_section_html}
            </div>
        </section>

        {publisher_section_html}
    </main>

    <footer>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Data source: "Praise History" and "Song Index" on Google Drive</p>
        <p>This is an AI agent-coded product</p>
    </footer>

    <script>
        {get_embedded_javascript()}
    </script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def generate_nav_menu(leaders: List[str]) -> str:
    """Generate navigation menu HTML."""
    leader_links = ''.join([
        f'<a href="#leader-{leader.lower().replace(" ", "-")}" class="nav-link">{leader}</a>'
        for leader in leaders
    ])

    return f"""
        <div class="nav-brand">Worship Journey 2025</div>
        <div class="nav-links">
            <a href="#section-a" class="nav-link">Praise Leaders</a>
            <a href="#section-b" class="nav-link">Global Stats</a>
            <a href="#publisher" class="nav-link">Publisher</a>
            <a href="#all-songs" class="nav-link">All Songs</a>
            <div class="dropdown">
                <button class="dropdown-btn">Leaders ▾</button>
                <div class="dropdown-content">
                    {leader_links}
                </div>
            </div>
        </div>
        <button class="mobile-menu-btn" onclick="toggleMobileMenu()">☰</button>
    """


def generate_leader_section(stats: Dict) -> str:
    """Generate HTML for a single leader's statistics."""
    leader = stats['name']
    leader_id = leader.lower().replace(' ', '-')

    # Generate tables - include single occurrence note for leader stats
    praise1_table = generate_top_songs_table(stats['praise1_top20'], include_single_occurrence_note=True)
    praise2_table = generate_top_songs_table(stats['praise2_top20'], include_single_occurrence_note=True)
    peace_table = generate_top_songs_table(stats['peace_top20'], include_single_occurrence_note=True)
    combined_table = generate_top_songs_table(stats['combined_top20'], include_single_occurrence_note=True)
    new_songs_list = generate_song_list(stats['new_songs_2025'])
    overlap_html = generate_overlap_section(stats['top2_leaders_overlap'])
    publisher_table = generate_publisher_percentage_table(stats['publisher_percentages'])

    return f"""
    <article id="leader-{leader_id}" class="leader-card" data-leader-id="{leader_id}">
        <header class="leader-header" onclick="toggleLeaderCard('{leader_id}')">
            <div class="leader-header-content">
                <h3>{leader}</h3>
                <span class="expand-icon">▼</span>
            </div>
            <div class="stats-summary">
                <div class="stat-item">
                    <span class="stat-value">{stats['total_services']}</span>
                    <span class="stat-label">Services</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{stats['total_songs']}</span>
                    <span class="stat-label">Songs</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{len(stats['new_songs_2025'])}</span>
                    <span class="stat-label">New Songs</span>
                    <span class="stat-percentage" style="display: none;">({len(stats['new_songs_2025']) / stats['total_songs'] * 100 if stats['total_songs'] > 0 else 0:.1f}%)</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{stats['common_songs_count']}</span>
                    <span class="stat-label">Songs in common with others</span>
                </div>
            </div>
        </header>

        <div class="leader-content">
            <div class="stat-section">
                <h4>Top Praise 1 Songs</h4>
                {praise1_table}
            </div>

            <div class="stat-section">
                <h4>Top Praise 2 Songs</h4>
                {praise2_table}
            </div>

            <div class="stat-section">
                <h4>Top 3 Peace Songs</h4>
                {peace_table}
            </div>

            <div class="stat-section">
                <h4>Top 20 All Songs Combined</h4>
                {combined_table}
            </div>

            <div class="stat-section">
                <h4>New Songs in 2025</h4>
                <p class="section-note">Songs that appeared in 2025 for the first time (not previously in our song library)</p>
                {new_songs_list}
            </div>

            <div class="stat-section">
                <h4>Song Publisher</h4>
                <p class="section-note">Percentage of publishers for songs led by this leader (excluding peace songs)</p>
                {publisher_table}
            </div>

            <div class="stat-section">
                <h4>Most Similar Leaders</h4>
                <p class="section-note">Leaders with most songs in common</p>
                {overlap_html}
            </div>
        </div>
    </article>
    """


def generate_new_song_usage_section(new_song_usage: Dict) -> str:
    """
    Generate HTML for new song usage statistics section.

    Args:
        new_song_usage: Dict with 'combined', 'saturday', 'sunday' stats

    Returns:
        HTML string for the new song usage section
    """
    combined = new_song_usage['combined']
    saturday = new_song_usage['saturday']
    sunday = new_song_usage['sunday']

    # Format dates as comma-separated for compact display
    saturday_dates_str = ', '.join(saturday.get('dates', []))
    sunday_dates_str = ', '.join(sunday.get('dates', []))

    return f"""
    <div class="stat-section collapsible">
        <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
            <span>New Songs Usage</span>
            <span class="expand-icon">▼</span>
        </h4>
        <div class="collapsible-content">
            <p class="section-note">Statistics about introduction of new songs in worship services. A worship is counted if it introduces at least one new song for the first time (in that category).</p>
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Total Worships</th>
                        <th>Worships with New Songs</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Combined</td>
                        <td>{combined['total_worships']}</td>
                        <td>{combined['worships_with_new_songs']}</td>
                        <td>{combined['percentage']:.1f}%</td>
                    </tr>
                    <tr>
                        <td>Saturday Worship</td>
                        <td>{saturday['total_worships']}</td>
                        <td>{saturday['worships_with_new_songs']}</td>
                        <td>{saturday['percentage']:.1f}%</td>
                    </tr>
                    <tr>
                        <td>Sunday Worship</td>
                        <td>{sunday['total_worships']}</td>
                        <td>{sunday['worships_with_new_songs']}</td>
                        <td>{sunday['percentage']:.1f}%</td>
                    </tr>
                </tbody>
            </table>
            <div style="margin-top: 10px; font-size: 0.75em; line-height: 1.4; color: #555;">
                <b>Sat:</b> {saturday_dates_str}
            </div>
            <div style="margin-top: 6px; font-size: 0.75em; line-height: 1.4; color: #555;">
                <b>Sun:</b> {sunday_dates_str}
            </div>
        </div>
    </div>
    """


def generate_global_section(stats: Dict) -> str:
    """Generate HTML for global statistics."""
    praise1_table = generate_top_songs_table(stats['praise1_top20'])
    praise2_table = generate_top_songs_table(stats['praise2_top20'])
    combined_table = generate_top_songs_table(stats['combined_top20'])
    multi_leader_table = generate_multi_leader_table(stats['top10_multi_leader'])
    peace_table = generate_top_songs_table(stats['peace_top3'])
    new_songs_list = generate_song_list(stats['new_songs_2025'])
    unique_songs_list = generate_song_list(stats['unique_songs_2025'])

    # Generate new song usage section if data is available
    new_song_usage_html = ''
    if 'new_song_usage' in stats:
        new_song_usage_html = generate_new_song_usage_section(stats['new_song_usage'])

    return f"""
    <div class="global-stats">
        <div class="highlight-card">
            <h3>Total Unique Songs in 2025</h3>
            <div class="big-number">{stats['total_unique_songs']}</div>
        </div>

        <div class="info-box">
            <p><span class="new-song-indicator">●</span> New Song: 2025 was the first time this song appeared</p>
        </div>

        {new_song_usage_html}

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 20 Praise 1 Songs</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                {praise1_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 20 Praise 2 Songs</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                {praise2_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 20 Praise 1 & 2 Combined</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                {combined_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 10 Multi-Leader Songs</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Songs chosen by at least 3 different praise leaders (excluding peace songs)</p>
                {multi_leader_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 3 Peace Songs</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                {peace_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>New Songs in 2025</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Songs that appeared in 2025 for the first time (not previously in our song library)</p>
                {new_songs_list}
            </div>
        </div>

        <div id="all-songs" class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>All Unique Songs in 2025</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Complete alphabetical list of all songs used in 2025</p>
                {unique_songs_list}
            </div>
        </div>
    </div>
    """


def generate_top_songs_table(songs: List[Tuple[str, int]], include_single_occurrence_note: bool = False) -> str:
    """Generate HTML table for top songs."""
    if not songs:
        if include_single_occurrence_note:
            return '<p class="no-data">All selected songs appeared only once</p>'
        return '<p class="no-data">No data available</p>'

    rows = ''
    for i, (song, count) in enumerate(songs, 1):
        formatted_song = format_song_name(song)
        rows += f'<tr><td>{i}</td><td>{formatted_song}</td><td>{count}</td></tr>\n'

    # Add note if list has less than 20 entries and we should show it
    note_html = ''
    if include_single_occurrence_note and len(songs) < 20:
        note_html = '<p class="single-occurrence-note">All other songs appeared only once</p>'

    return f"""
    <table class="stats-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Song</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    {note_html}
    """


def generate_multi_leader_table(songs: List[Tuple[str, int, List[str], int]]) -> str:
    """Generate HTML table for multi-leader songs."""
    if not songs:
        return '<p class="no-data">No songs chosen by 3+ leaders</p>'

    rows = ''
    for i, (song, leader_count, leaders, total_count) in enumerate(songs, 1):
        formatted_song = format_song_name(song)
        leaders_str = ', '.join(leaders)
        rows += f'<tr><td>{i}</td><td>{formatted_song}</td><td>{leader_count}</td><td>{total_count}</td><td class="leaders-cell">{leaders_str}</td></tr>\n'

    return f"""
    <table class="stats-table multi-leader-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Song</th>
                <th>Leaders</th>
                <th>Total</th>
                <th>Leader Names</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


def generate_publisher_table(publishers: List[Tuple[str, int, List[Tuple[str, int]]]]) -> str:
    """
    Generate HTML table for publisher statistics with expandable rows.

    Args:
        publishers: List of (publisher_name, total_count, songs_list)
                   Note: songs_list may be limited to top 10

    Returns:
        HTML string for the publisher table
    """
    if not publishers:
        return '<p class="no-data">No publisher data available</p>'

    rows = ''
    for i, (publisher, total_count, songs) in enumerate(publishers, 1):
        # Get display name for publisher
        display_name = get_publisher_display_name(publisher)

        # Generate song list for this publisher
        song_rows = ''
        songs_total = 0
        for song, count in songs:
            formatted_song = format_song_name(song)
            song_rows += f'<tr><td>{formatted_song}</td><td>{count}</td></tr>\n'
            songs_total += count

        if not song_rows:
            song_rows = '<tr><td colspan="2">No songs</td></tr>'

        # Add note if only showing top 10 and there are more songs
        note_html = ''
        if len(songs) >= 10 and songs_total < total_count:
            remaining_count = total_count - songs_total
            note_html = f'<p class="publisher-note">Showing top 10 songs only. {remaining_count} additional occurrences from other songs not shown.</p>'

        nested_table = f"""
        <table class="nested-songs-table">
            <thead>
                <tr>
                    <th>Song</th>
                    <th>Occurrences</th>
                </tr>
            </thead>
            <tbody>
                {song_rows}
            </tbody>
        </table>
        {note_html}
        """

        rows += f"""
        <tr class="publisher-row" onclick="togglePublisherRow(this)">
            <td>{i}</td>
            <td>{display_name}</td>
            <td>{total_count}</td>
            <td><span class="expand-icon">▼</span></td>
        </tr>
        <tr class="publisher-songs-row" style="display: none;">
            <td colspan="4">
                {nested_table}
            </td>
        </tr>
        """

    return f"""
    <table class="stats-table publisher-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Publisher</th>
                <th>Total Occurrences</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


def generate_unmatched_songs_table(songs: List[Tuple[str, int]]) -> str:
    """
    Generate HTML table for songs not matched to any publisher.

    Args:
        songs: List of (song_name, count) tuples

    Returns:
        HTML string for the unmatched songs table
    """
    if not songs:
        return '<p class="no-data">All songs matched to publishers!</p>'

    rows = ''
    for song, count in songs:
        formatted_song = format_song_name(song)
        rows += f'<tr><td>{formatted_song}</td><td>{count}</td></tr>\n'

    return f"""
    <table class="stats-table">
        <thead>
            <tr>
                <th>Song</th>
                <th>Occurrences</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


def generate_publisher_section(stats: Dict) -> str:
    """
    Generate HTML for Section C: Publisher.

    Args:
        stats: Publisher statistics dictionary

    Returns:
        HTML string for the complete publisher section
    """
    top20_table = generate_publisher_table(stats['top20_publishers'])
    top20_praise1_table = generate_publisher_table(stats['top20_praise1'])
    top20_praise2_table = generate_publisher_table(stats['top20_praise2'])
    top20_peace_table = generate_publisher_table(stats['top20_peace'])
    unmatched_table = generate_unmatched_songs_table(stats['unmatched_songs'])
    all_publishers_table = generate_publisher_table(stats['all_publishers'])

    return f"""
    <section id="publisher">
        <div class="section-header">
            <h2>Section C: Publisher</h2>
            <p class="section-description">Analysis of songs by copyright/publisher ownership</p>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 20 Publishers by Song Occurrences (Excluding Peace Songs)</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Top 20 publishers with highest song occurrences in Praise 1 & 2 (excluding Peace songs) in 2025. Click publisher row to view songs.</p>
                {top20_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 20 Publishers by Song Occurrences in Praise 1</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Top 20 publishers with highest song occurrences in Praise 1 in 2025. Click publisher row to view songs.</p>
                {top20_praise1_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 20 Publishers by Song Occurrences in Praise 2</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Top 20 publishers with highest song occurrences in Praise 2 in 2025. Click publisher row to view songs.</p>
                {top20_praise2_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Top 20 Publishers by Song Occurrences in Peace Songs</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Top 20 publishers with highest song occurrences in Peace in 2025. Click publisher row to view songs.</p>
                {top20_peace_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Songs Not Matched to Any Publisher</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Songs that could not be matched to any publisher in the metadata</p>
                {unmatched_table}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>All Publishers (Complete List)</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Complete list of all publishers from metadata, sorted by 2025 occurrences. Click publisher row to view songs.</p>
                {all_publishers_table}
            </div>
        </div>
    </section>
    """


def generate_song_list(songs: List[str]) -> str:
    """Generate HTML list of songs."""
    if not songs:
        return '<p class="no-data">No songs in this category</p>'

    items = ''.join([f'<li>{format_song_name(song)}</li>' for song in songs])

    return f'<ul class="song-list">{items}</ul>'


def generate_overlap_section(overlaps: List[Tuple[str, int]]) -> str:
    """Generate HTML for leader overlap statistics."""
    if not overlaps:
        return '<p class="no-data">No overlap with other leaders</p>'

    items = ''.join([
        f'<div class="overlap-item"><span class="overlap-leader">{leader}</span><span class="overlap-count">{count} songs</span></div>'
        for leader, count in overlaps
    ])

    return f'<div class="overlap-list">{items}</div>'


def generate_publisher_percentage_table(publisher_percentages: List[Tuple[str, float, int]]) -> str:
    """
    Generate HTML table for publisher percentages.
    Shows top 5 publishers, then aggregates the rest into "and other X publishers".

    Args:
        publisher_percentages: List of (publisher_name, percentage, count) tuples

    Returns:
        HTML string for the publisher percentage table
    """
    if not publisher_percentages:
        return '<p class="no-data">No publisher data available</p>'

    rows = ''

    # Separate unmatched songs from regular publishers
    unmatched_entry = None
    regular_publishers = []
    for entry in publisher_percentages:
        if entry[0] == "__UNMATCHED__":
            unmatched_entry = entry
        else:
            regular_publishers.append(entry)

    # Show top 5 publishers
    top5 = regular_publishers[:5]
    for publisher, percentage, count in top5:
        # Get display name for publisher
        display_name = get_publisher_display_name(publisher)
        rows += f'<tr><td>{display_name}</td><td>{percentage:.1f}%</td></tr>\n'

    # Aggregate remaining publishers if there are more than 5
    if len(regular_publishers) > 5:
        remaining = regular_publishers[5:]
        remaining_percentage = sum(p[1] for p in remaining)
        remaining_count = len(remaining)
        rows += f'<tr><td>and other {remaining_count} publishers</td><td>{remaining_percentage:.1f}%</td></tr>\n'

    # Add unmatched songs row at the end if present
    if unmatched_entry:
        _, percentage, count = unmatched_entry
        rows += f'<tr class="unmatched-row"><td>Unmatched songs</td><td>{percentage:.1f}%</td></tr>\n'

    return f"""
    <table class="stats-table">
        <thead>
            <tr>
                <th>Publisher</th>
                <th>Percentage</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """


def get_embedded_css() -> str:
    """Return embedded CSS styles."""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Sans CJK SC", "Microsoft YaHei";
            line-height: 1.6;
            color: #333;
            background: #f9f9f9;
        }

        /* Navigation */
        .main-nav {
            position: sticky;
            top: 0;
            background: #2C3E50;
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .nav-brand {
            font-size: 1.5rem;
            font-weight: bold;
        }

        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .nav-link {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background 0.3s;
        }

        .nav-link:hover {
            background: rgba(255,255,255,0.1);
        }

        .dropdown {
            position: relative;
            display: inline-block;
        }

        .dropdown-btn {
            background: #34495E;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }

        .dropdown-content {
            display: none;
            position: absolute;
            background: white;
            min-width: 200px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            border-radius: 4px;
            margin-top: 0.5rem;
            max-height: 400px;
            overflow-y: auto;
        }

        .dropdown-content .nav-link {
            color: #333;
            display: block;
            padding: 0.75rem 1rem;
        }

        .dropdown-content .nav-link:hover {
            background: #f0f0f0;
        }

        .dropdown.active .dropdown-content {
            display: block;
        }

        .mobile-menu-btn {
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #2C3E50 0%, #3498DB 100%);
            color: white;
            padding: 4rem 2rem;
            text-align: center;
        }

        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        /* Main Content */
        main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .section {
            margin-bottom: 4rem;
        }

        .section-header {
            text-align: center;
            margin-bottom: 3rem;
        }

        .section-header h2 {
            font-size: 2.5rem;
            color: #2C3E50;
            margin-bottom: 0.5rem;
        }

        .section-description {
            color: #666;
            font-size: 1.1rem;
        }

        /* Leader Cards */
        .leaders-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }

        .leader-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .leader-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .leader-header {
            background: linear-gradient(135deg, #F39C12 0%, #E67E22 100%);
            color: white;
            padding: 2rem;
            cursor: pointer;
            user-select: none;
        }

        .leader-header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .leader-header h3 {
            font-size: 2rem;
            margin: 0;
        }

        .expand-icon {
            font-size: 1.2rem;
            transition: transform 0.3s ease;
            display: inline-block;
        }

        .leader-card.collapsed .expand-icon {
            transform: rotate(-90deg);
        }

        .stats-summary {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
        }

        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .leader-content {
            padding: 2rem;
            max-height: 5000px;
            overflow: hidden;
            transition: max-height 0.4s ease, padding 0.4s ease;
        }

        .leader-card.collapsed .leader-content {
            max-height: 0;
            padding: 0 2rem;
        }

        .stat-section {
            margin-bottom: 2.5rem;
        }

        .stat-section h4 {
            font-size: 1.3rem;
            color: #2C3E50;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid #F39C12;
            padding-bottom: 0.5rem;
        }

        /* Collapsible sections in global stats */
        .collapsible {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 1rem;
        }

        .collapsible-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            background: #f5f5f5;
            padding: 1rem 1.5rem;
            margin: 0;
            border: none;
            border-bottom: none;
            transition: background 0.3s ease;
        }

        .collapsible-header:hover {
            background: #e8e8e8;
        }

        .collapsible-content {
            max-height: 5000px;
            overflow: hidden;
            padding: 1.5rem;
            transition: max-height 0.4s ease, padding 0.4s ease;
        }

        .collapsible.collapsed .collapsible-content {
            max-height: 0;
            padding: 0 1.5rem;
        }

        .collapsible.collapsed .expand-icon {
            transform: rotate(-90deg);
        }

        .single-occurrence-note {
            color: #666;
            font-style: italic;
            margin-top: 1rem;
            padding: 0.75rem;
            background: #f9f9f9;
            border-left: 3px solid #F39C12;
            border-radius: 4px;
        }

        .section-note {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            font-style: italic;
        }

        /* Tables */
        .stats-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 4px;
            overflow: hidden;
        }

        .stats-table th {
            background: #2C3E50;
            color: white;
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
        }

        .stats-table td {
            padding: 0.75rem;
            border-bottom: 1px solid #eee;
        }

        .stats-table tbody tr:hover {
            background: #f5f5f5;
        }

        .stats-table tbody tr:nth-child(even) {
            background: #fafafa;
        }

        /* Unmatched row styling */
        .stats-table .unmatched-row {
            background: #FFF3CD;
            font-style: italic;
            color: #856404;
            border-top: 2px solid #FFC107;
        }

        .stats-table .unmatched-row:hover {
            background: #FFE69C;
        }

        .leaders-cell {
            font-size: 0.9rem;
            color: #666;
        }

        /* Song Lists */
        .song-list {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 0.5rem;
        }

        .song-list li {
            background: #f0f0f0;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            border-left: 3px solid #F39C12;
        }

        /* New Song Indicator */
        .new-song-indicator {
            color: #E74C3C;
            font-size: 0.8em;
            margin-right: 0.3rem;
            font-weight: bold;
            cursor: help;
            transition: color 0.2s ease;
        }

        .new-song-indicator:hover {
            color: #C0392B;
        }

        /* Info Box */
        .info-box {
            background: #FFF3CD;
            border: 1px solid #FFC107;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            text-align: center;
        }

        .info-box p {
            margin: 0;
            color: #856404;
            font-size: 1rem;
        }

        /* Overlap Section */
        .overlap-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .overlap-item {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .overlap-leader {
            font-weight: 600;
            color: #2C3E50;
        }

        .overlap-count {
            background: #F39C12;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.9rem;
        }

        /* Publisher Tables */
        .publisher-table {
            width: 100%;
        }

        .publisher-row {
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .publisher-row:hover {
            background-color: #f8f9fa;
        }

        .publisher-row .expand-icon {
            display: inline-block;
            transition: transform 0.3s;
            font-size: 1rem;
            color: #3498DB;
        }

        .publisher-row.expanded .expand-icon {
            transform: rotate(180deg);
        }

        .publisher-songs-row {
            background: #f8f9fa;
        }

        .publisher-songs-row td {
            padding: 1rem !important;
        }

        .nested-songs-table {
            width: 100%;
            margin: 0;
            background: white;
            border-radius: 4px;
        }

        .nested-songs-table thead {
            background: #ecf0f1;
        }

        .nested-songs-table th {
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 2px solid #bdc3c7;
        }

        .nested-songs-table td {
            padding: 0.75rem;
            border-bottom: 1px solid #ecf0f1;
        }

        .nested-songs-table tr:last-child td {
            border-bottom: none;
        }

        .nested-songs-table tr:hover {
            background-color: #f8f9fa;
        }

        .publisher-note {
            margin-top: 1rem;
            padding: 0.75rem;
            background: #FFF3CD;
            border-left: 3px solid #FFC107;
            border-radius: 4px;
            color: #856404;
            font-size: 0.9rem;
            font-style: italic;
        }

        /* Global Stats */
        .global-container {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .highlight-card {
            background: linear-gradient(135deg, #3498DB 0%, #2C3E50 100%);
            color: white;
            padding: 3rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 2rem;
        }

        .highlight-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }

        .big-number {
            font-size: 4rem;
            font-weight: bold;
        }

        .no-data {
            color: #999;
            font-style: italic;
            padding: 1rem;
            text-align: center;
        }

        /* Footer */
        footer {
            background: #2C3E50;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }

            .nav-links {
                display: none;
            }

            .mobile-menu-btn {
                display: block;
            }

            .nav-links.mobile-active {
                display: flex;
                flex-direction: column;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: #2C3E50;
                padding: 1rem;
            }

            .stats-summary {
                justify-content: center;
            }

            .song-list {
                grid-template-columns: 1fr;
            }

            .stats-table {
                font-size: 0.9rem;
            }

            .stats-table th,
            .stats-table td {
                padding: 0.5rem;
            }
        }

        @media (min-width: 1200px) {
            .leaders-container {
                grid-template-columns: 1fr;
            }
        }
    """


def get_embedded_javascript() -> str:
    """Return embedded JavaScript."""
    return """
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                const target = document.querySelector(href);
                if (target) {
                    // Check if this is a leader card link
                    if (href.startsWith('#leader-')) {
                        const leaderId = href.substring(8); // Remove '#leader-' prefix
                        const leaderCard = document.querySelector(`[data-leader-id="${leaderId}"]`);

                        if (leaderCard) {
                            // Collapse all leader cards
                            const allLeaderCards = document.querySelectorAll('.leader-card');
                            allLeaderCards.forEach(card => {
                                card.classList.add('collapsed');
                            });

                            // Expand the target leader card
                            leaderCard.classList.remove('collapsed');

                            // Wait for expansion animation to complete before scrolling
                            // The CSS transition is 0.4s, so wait 450ms to be safe
                            setTimeout(() => {
                                target.scrollIntoView({
                                    behavior: 'smooth',
                                    block: 'start'
                                });
                            }, 450);
                            return;
                        }
                    }

                    // For non-leader links, scroll immediately
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Mobile menu toggle
        function toggleMobileMenu() {
            const navLinks = document.querySelector('.nav-links');
            navLinks.classList.toggle('mobile-active');
        }

        // Toggle leader card - when one is expanded, collapse all others
        function toggleLeaderCard(leaderId) {
            const clickedCard = document.querySelector(`[data-leader-id="${leaderId}"]`);
            const allLeaderCards = document.querySelectorAll('.leader-card');

            // If the clicked card is already expanded, just collapse it
            if (!clickedCard.classList.contains('collapsed')) {
                clickedCard.classList.add('collapsed');
                return;
            }

            // Collapse all leader cards
            allLeaderCards.forEach(card => {
                card.classList.add('collapsed');
            });

            // Expand the clicked card
            clickedCard.classList.remove('collapsed');
        }

        // Toggle global section - independent collapsing
        function toggleGlobalSection(header) {
            const section = header.parentElement;
            section.classList.toggle('collapsed');
        }

        // Toggle publisher row to show/hide songs
        function togglePublisherRow(row) {
            const songsRow = row.nextElementSibling;
            const expandIcon = row.querySelector('.expand-icon');

            // Check if this row is currently expanded
            const isCurrentlyExpanded = row.classList.contains('expanded');

            if (songsRow && songsRow.classList.contains('publisher-songs-row')) {
                // If clicking an already expanded row, just collapse it
                if (isCurrentlyExpanded) {
                    songsRow.style.display = 'none';
                    expandIcon.textContent = '▼';
                    row.classList.remove('expanded');
                } else {
                    // Collapse all other publisher rows in all tables
                    const allPublisherRows = document.querySelectorAll('.publisher-row');
                    allPublisherRows.forEach(r => {
                        const sRow = r.nextElementSibling;
                        const eIcon = r.querySelector('.expand-icon');
                        if (sRow && sRow.classList.contains('publisher-songs-row')) {
                            sRow.style.display = 'none';
                            eIcon.textContent = '▼';
                            r.classList.remove('expanded');
                        }
                    });

                    // Expand the clicked row
                    songsRow.style.display = 'table-row';
                    expandIcon.textContent = '▲';
                    row.classList.add('expanded');
                }
            }
        }

        // Initialize all leader cards as collapsed by default
        document.addEventListener('DOMContentLoaded', () => {
            const leaderCards = document.querySelectorAll('.leader-card');
            leaderCards.forEach(card => {
                card.classList.add('collapsed');
            });

            // Initialize all global sections as collapsed by default
            const globalSections = document.querySelectorAll('.collapsible');
            globalSections.forEach(section => {
                section.classList.add('collapsed');
            });
        });

        // Highlight active section in navigation
        window.addEventListener('scroll', () => {
            const sections = document.querySelectorAll('.section');
            const navLinks = document.querySelectorAll('.nav-link');

            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop - 100) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                }
            });
        });

        // Dropdown toggle
        document.querySelector('.dropdown-btn').addEventListener('click', function(e) {
            e.stopPropagation();
            this.parentElement.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            const dropdown = document.querySelector('.dropdown');
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });

        // Close dropdown when a link is clicked
        document.querySelectorAll('.dropdown-content .nav-link').forEach(link => {
            link.addEventListener('click', () => {
                document.querySelector('.dropdown').classList.remove('active');
            });
        });
    """


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("Worship Journey 2025 - Data Processing")
    print("=" * 50)

    # Load CSV data
    print("\n1. Loading CSV data...")
    csv_path = 'praisehistory.csv'
    services = load_csv_data(csv_path)
    print(f"   Loaded {len(services)} service records")

    # Filter by year
    services_2025 = [s for s in services if s['year'] == 2025]
    print(f"   Found {len(services_2025)} services in 2025")

    # Load historical songs for new song detection
    historical_songs_set = load_historical_songs()
    print(f"   Loaded {len(historical_songs_set)} historical songs from uniquesong_until2024.csv")

    # Calculate leader statistics
    print("\n2. Calculating Section A - Praise Leader Statistics...")
    leader_stats = calculate_leader_stats(services, historical_songs_set, year=2025)
    print(f"   Analyzed {len(leader_stats)} praise leaders")

    # Calculate global statistics
    print("\n3. Calculating Section B - Global Statistics...")
    global_stats = calculate_global_stats(services, historical_songs_set, year=2025)
    print(f"   Found {global_stats['total_unique_songs']} unique songs")

    # Calculate new song usage statistics and add to global_stats
    new_song_usage_stats = calculate_new_song_usage_stats(services, historical_songs_set, year=2025)
    global_stats['new_song_usage'] = new_song_usage_stats
    print(f"   New song usage: {new_song_usage_stats['combined']['worships_with_new_songs']}/{new_song_usage_stats['combined']['total_worships']} worships introduced new songs")

    # Calculate publisher statistics
    print("\n4. Calculating Section C - Publisher Statistics...")
    publisher_stats = calculate_publisher_stats(services, year=2025)
    print(f"   Found {len(publisher_stats['top20_publishers'])} publishers with songs in 2025")
    print(f"   {len(publisher_stats['unmatched_songs'])} songs not matched to any publisher")

    # Generate HTML
    print("\n5. Generating HTML output...")
    output_path = 'index.html'
    generate_html(leader_stats, global_stats, publisher_stats, output_path)
    print(f"   HTML saved to: {output_path}")

    print("\n" + "=" * 50)
    print("Processing complete!")
    print(f"\nOpen {output_path} in your browser to view the results.")


if __name__ == '__main__':
    main()
