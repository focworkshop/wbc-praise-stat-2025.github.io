Claude’s Plan
Worship Journey 2025 - Implementation Plan
Project Overview
Create a Python-based data processing system that analyzes worship service data from praisehistory.csv and generates a single, self-contained HTML file displaying comprehensive statistics for 2025 worship services.

Data Source Analysis
File: t:\praise_team_rewind\praisehistory.csv

Structure:

Column 0: Date (YYYY-MM-DD format)
Column 1: Flow Designed by (Praise Leader)
Column 2: Praise Theme Keywords
Columns 3-8: Praise 1 songs and keys (3 song-key pairs)
Columns 9-14: Praise 2 songs and keys (3 song-key pairs)
Columns 15-16: Peace song and key (1 pair)
Data Boundaries:

2025: Line 900+
2024: Line 798+
2023: Line 716+
2022: Line 633+
Identified 2025 Praise Leaders:
Keith, Shirley, Jeanne, Cannis, Michael, Joseph, TL, Lobo, Alan, Maree, Phoebe

Implementation Architecture
Python Module Structure

worship_journey.py          # Main orchestration script
├── load_csv_data()        # Load and parse CSV
├── parse_services()       # Extract service records
├── calculate_leader_stats() # Section A statistics
├── calculate_global_stats() # Section B statistics
└── generate_html()        # Create output HTML
Key Data Structures

ServiceRecord = {
    'date': datetime,
    'year': int,
    'praise_leader': str,
    'theme': str,
    'praise1': [songs],    # From columns 3,5,7
    'praise2': [songs],    # From columns 9,11,13
    'peace': [song]        # From column 15
}

LeaderStats = {
    'name': str,
    'total_services': int,
    'total_songs': int,
    'praise1_top20': [(song, count)],
    'praise2_top20': [(song, count)],
    'peace_top20': [(song, count)],
    'combined_top20': [(song, count)],
    'new_songs_2025': [songs],
    'common_songs_count': int,
    'top2_leaders_overlap': [(leader, count)]
}

GlobalStats = {
    'total_unique_songs': int,
    'praise1_top20': [(song, count)],
    'praise2_top20': [(song, count)],
    'combined_top20': [(song, count)],
    'top10_multi_leader': [(song, leader_count, [leaders])],
    'peace_top3': [(song, count)],
    'new_songs_2025': [songs],
    'songs_2024_not_2025': [songs]
}
Implementation Steps
Step 1: CSV Parsing & Data Loading
Read CSV with UTF-8 encoding
Handle multi-line entries (consolidate continuation rows)
Extract songs from alternating song-key columns
Parse dates and filter by year (2022-2025)
Clean and normalize song names
Handle combined songs (e.g., "Song1 + Song2" patterns)
Step 2: Data Cleaning Functions
Song Extraction:

Parse columns 3,5,7 for Praise 1
Parse columns 9,11,13 for Praise 2
Parse column 15 for Peace
Skip empty cells
Song Cleaning:

Split combined songs (detect " + ", " / " patterns)
Normalize whitespace
Remove trailing punctuation
Handle multi-line song names
Preserve Chinese/English characters
Leader Normalization:

Remove annotations like "(HC)", "(AGW)"
Trim whitespace
Handle special cases (joint worship, team entries)
Step 3: Section A - Praise Leader Statistics
For each leader in 2025:

Service Count: Count rows where leader appears
Total Songs: Sum all songs from praise1, praise2, peace
Top 20 Songs by Category:
Praise1: Count occurrences, rank top 20
Praise2: Count occurrences, rank top 20
Peace: Count occurrences, rank top 20
Combined: Count all songs together, rank top 20
New Songs in 2025: Compare leader's 2025 songs vs their 2022-2024 songs
Common Songs Count: Count songs this leader chose that other leaders also chose
Top 2 Leader Overlap: Find 2 leaders with most songs in common with this leader
Step 4: Section B - Global Statistics
For all 2025 services combined:

Total Unique Songs: Count distinct songs across all categories
Top 20 by Category:
Praise1 only: Top 20 by occurrence
Praise2 only: Top 20 by occurrence
Praise1 + Praise2 combined: Top 20 by occurrence
Multi-Leader Songs: For praise1+praise2 (excluding peace), find songs chosen by ≥3 leaders, rank top 10
Top 3 Peace Songs: Count peace song occurrences, show top 3
New Songs 2025: Songs in 2025 not in 2022/2023/2024
Songs 2024 Not 2025: Songs in 2024 that don't appear in 2025
Step 5: HTML Generation
Structure:

Single self-contained HTML file
Embedded CSS and JavaScript (no external files)
Two main sections with smooth navigation
Section A Layout:

Leader navigation menu
For each leader, display card with:
Summary stats (services, total songs)
Top 20 tables for each category
New songs list
Overlap analysis
Section B Layout:

Global statistics dashboard
Total unique songs highlight
Top 20 tables for each category
Multi-leader songs table
Peace songs table
New/deprecated songs lists
Design Requirements:

Modern minimalist aesthetic
Responsive grid layout (mobile + desktop)
Smooth scrolling between sections
Color palette: Deep blue (#2C3E50), soft gold (#F39C12), off-white background
Typography: System fonts with Chinese fallback
Card-based component design
Tables with alternating row colors
Sticky navigation header
JavaScript Features:

Smooth scroll to sections
Navigation highlighting on scroll
Mobile menu toggle
Step 6: Edge Case Handling
Empty cells: Treat as None, skip in processing
Multi-line entries: Consolidate rows without dates into previous row
Combined songs: Split on " + ", " / ", "V1 V2 +" patterns
Communion markers: Handle "+ Communion" annotations
Leader variations: Normalize "(HC)", "(AGW)" suffixes
Date parsing: Handle YYYY-MM-DD format
Encoding: UTF-8 for Chinese character support
Critical Files
Input:

praisehistory.csv - Source data
Output:

worship_journey.py - Main Python script
index.html - Generated HTML output
Verification Plan
Data Accuracy Checks:

Manually verify one leader's service count against CSV
Cross-check top 5 songs for one leader
Verify new songs list for one leader
Check multi-leader song counts
HTML Validation:

Test in Chrome, Firefox, Safari
Test responsive design on mobile
Verify smooth scrolling works
Check Chinese character rendering
Confirm no external resource dependencies
Validate HTML structure
Performance:

Ensure HTML file size < 5MB
Page load time < 2 seconds
Smooth scrolling with full dataset
Implementation Approach
Single Python Script: Create one comprehensive script for simplicity
Function-based Structure: Modular functions for each processing step
Inline HTML Template: Embed HTML template as Python string with f-string formatting
Collections Library: Use Counter for efficient song counting
CSV Reader: Use Python csv module with UTF-8 encoding
Data Flow: CSV → ServiceRecords → Statistics → HTML Output
Estimated Complexity
Moderate complexity due to CSV parsing edge cases
Multi-column song extraction requires careful indexing
Statistics calculations are straightforward with Counter
HTML generation is template-based with data embedding