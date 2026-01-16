#!/usr/bin/env python3
"""
Worship Journey 2025 - Data Processing and HTML Generation
Analyzes worship service data and generates a comprehensive statistics report.
"""

import csv
import re
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple

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

def calculate_leader_stats(services: List[Dict], year: int = 2025) -> Dict[str, Dict]:
    """
    Calculate statistics for each praise leader in the specified year.
    """
    # Filter services by year
    year_services = [s for s in services if s['year'] == year]

    # Get all historical services for comparison (2022-2024)
    historical_services = [s for s in services if s['year'] in [2022, 2023, 2024]]

    # Group services by leader
    leader_services = defaultdict(list)
    for service in year_services:
        leader_services[service['praise_leader']].append(service)

    # Build historical song sets for each leader
    leader_historical_songs = defaultdict(set)
    for service in historical_services:
        leader = service['praise_leader']
        leader_historical_songs[leader].update(service['all_songs'])

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

        # New songs in 2025 (not in this leader's 2022-2024 history)
        new_songs_2025 = sorted(all_songs_set - leader_historical_songs.get(leader, set()))

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
            'top2_leaders_overlap': top2_leaders_overlap
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


# ============================================================================
# STATISTICS CALCULATION - SECTION B (GLOBAL)
# ============================================================================

def calculate_global_stats(services: List[Dict], year: int = 2025) -> Dict:
    """
    Calculate global statistics for all services in the specified year.
    """
    # Filter services by year
    year_services = [s for s in services if s['year'] == year]
    previous_year_services = [s for s in services if s['year'] == year - 1]
    historical_services = [s for s in services if s['year'] in [2022, 2023, 2024]]

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

    # New songs in 2025 (not in 2022-2024)
    historical_songs = set()
    for svc in historical_services:
        historical_songs.update(svc['all_songs'])
    new_songs_2025 = sorted(all_songs_set - historical_songs)

    # Songs in 2024 but not in 2025
    songs_2024 = set()
    for svc in previous_year_services:
        songs_2024.update(svc['all_songs'])
    songs_2024_not_2025 = sorted(songs_2024 - all_songs_set)

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
        'songs_2024_not_2025': songs_2024_not_2025,
        'unique_songs_2025': unique_songs_2025
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
        return f'<span class="new-song-indicator" title="This is a new song that appeared in 2025 but was not used in 2022-2024">●</span> {song}'
    return song

def generate_html(leader_stats: Dict, global_stats: Dict, output_path: str):
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
    </main>

    <footer>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Data source: Praise History on Google Drive</p>
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
                <h4>2025 New Songs (since 2022)</h4>
                <p class="section-note">Songs led in 2025 that were not led by this leader in 2022-2024</p>
                {new_songs_list}
            </div>

            <div class="stat-section">
                <h4>Most Similar Leaders</h4>
                <p class="section-note">Leaders with most songs in common</p>
                {overlap_html}
            </div>
        </div>
    </article>
    """


def generate_global_section(stats: Dict) -> str:
    """Generate HTML for global statistics."""
    praise1_table = generate_top_songs_table(stats['praise1_top20'])
    praise2_table = generate_top_songs_table(stats['praise2_top20'])
    combined_table = generate_top_songs_table(stats['combined_top20'])
    multi_leader_table = generate_multi_leader_table(stats['top10_multi_leader'])
    peace_table = generate_top_songs_table(stats['peace_top3'])
    new_songs_list = generate_song_list(stats['new_songs_2025'])
    deprecated_songs_list = generate_song_list(stats['songs_2024_not_2025'])
    unique_songs_list = generate_song_list(stats['unique_songs_2025'])

    return f"""
    <div class="global-stats">
        <div class="highlight-card">
            <h3>Total Unique Songs in 2025</h3>
            <div class="big-number">{stats['total_unique_songs']}</div>
        </div>

        <div class="info-box">
            <p><span class="new-song-indicator">●</span> Indicates a new song in 2025 (not used in 2022-2024)</p>
        </div>

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
                <p class="section-note">Songs that appeared in 2025 but not in 2022-2024</p>
                {new_songs_list}
            </div>
        </div>

        <div class="stat-section collapsible">
            <h4 class="collapsible-header" onclick="toggleGlobalSection(this)">
                <span>Songs from 2024 Not in 2025</span>
                <span class="expand-icon">▼</span>
            </h4>
            <div class="collapsible-content">
                <p class="section-note">Songs that were used in 2024 but not continued in 2025</p>
                {deprecated_songs_list}
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

    # Calculate leader statistics
    print("\n2. Calculating Section A - Praise Leader Statistics...")
    leader_stats = calculate_leader_stats(services, year=2025)
    print(f"   Analyzed {len(leader_stats)} praise leaders")

    # Calculate global statistics
    print("\n3. Calculating Section B - Global Statistics...")
    global_stats = calculate_global_stats(services, year=2025)
    print(f"   Found {global_stats['total_unique_songs']} unique songs")

    # Generate HTML
    print("\n4. Generating HTML output...")
    output_path = 'index.html'
    generate_html(leader_stats, global_stats, output_path)
    print(f"   HTML saved to: {output_path}")

    print("\n" + "=" * 50)
    print("Processing complete!")
    print(f"\nOpen {output_path} in your browser to view the results.")


if __name__ == '__main__':
    main()
