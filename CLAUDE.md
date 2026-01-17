# Data source
- original master source of truth is `praisehistory.csv`
- 2025 data starts after line 904
- 2024 data starts after line 798
- 2023 data starts after line 716
- 2022 data starts after line 633
- we only concern the following columns:
    - Date
    - Flow Designed by:
    - Praise Theme Keywords
    - Praise 1 (multiple values possible)
    - Praise 2 (multiple values possible)
    - Peace
- no need to concern before year 2022/
- Alias of the columns:
    - Date: `date`
    - Flow Designed by: `praise leader`
    - Praise Theme Keywords: `theme`
    - Praise 1: `praise1`
    - Praise 2: `praise2`
    - Peace: `peace`
- `Month` is referring to the month of the `date`
- `Year` is referring to the year of the `date`
- `YearMonth` is referring to the year and month of the `date`
- `song` is referring to the values of the `praise1` or `praise2` columns
- When I say "a praise leader has led a service", I mean the praise leader has a row present in a row. The date represents the date of the service.

Only read the csv file for the purpose of planning or produce the python scripts. Do not use agent model to repeatedly produce statistics.

# "Sunday Worship" and "Saturday Worship" definition
in `praisehistory.csv`, identify rows with sequencial date.
for example : 
- 2025-05-31, 2025-06-01, 
- 2025-06-07, 2025-06-08
The first row is "Saturday Worship", the second row is "Sunday Worship"


# Song name parsing
- the word "祢" is considered the same as "你"
- in song names processing, Disregard appending strings like "Medly", "Chorus Only", ," (Canto)"," (skip verse)"," by Esther Chow"," C1 C2","(Mando)","Communion","Holy Communion","Baptism"
- "Communion","Holy Communion","Baptism" are not a song, consider that empty, skip those.
- consider `(` = `（`
- consider `)` = `）`
- consider `,` = `，`
- consider `.` = `。`
- consider ` ` = ` ` (space)
- consider `:` = `：`
- consider `!` = `！`
- consider `?` = `？`
- during any song name comparison, remove whitespace betweend charaters within the songname string. consider it case-insensitive

#Praise leader name parsing
- "P1: Phoebe" is considered as "Phoebe"
- "A: Cannis" is "Cannis"

You want 祢, 你, and 袮 to be treated as equivalent characters (so songs with any of these variations are considered the same)

# Song Metadata
- song metadata contains copyright information of each song
- source of truth is `songindex*.csv`
- header at row 4
- column 0 is Index number, column 1 is song name, column 4 is copyright
- copyright owner here is aka publisher in the whole context

# static grouping for publisher names
- 余子麟,Alan Yu,林四
- Tsz-Lam Mak,麥子霖
- Stream Of Praise Music,Stream of Praise Music,	Stream of Praise,Steam of Praise,Stream of Praise Musice
- 香港基督徒音樂事工協會,香港基督徒音樂協會,香港基督徒音事工協會,香港基督徒音樂事工協會(HKACM)
- 鹹蛋⾳樂事⼯,鹹蛋音樂事工,鹹蛋音樂事
- Milk & Honey Worship,©️Milk&Honey Worship,Milk&Honey Worship
- 角聲佈道團,角聲使團
- One Circle Ltd,One Circle Limited,同心圓敬拜福音平台
- Flow Church,`Flow Music, Flow Church`,Flow Music
- Gsus Music Ministry Ltd,Gsus Music Ministry
- Esther Chow,周敏曦
- AFC Vancouver,AFC,加拿大基督使者協會
- 曾路得,Ruth Chen Music,
- Worship Nations,`Worship Nations / 玻璃海樂團`,`Worship Nations X 玻璃海樂團`,Worship Nation,`© 2019 Worship Nations`
- Grace Melodia,頌恩旋律
- CantonHymn,Cantonhymn
- `Public Domain, Son Music Worship Ministry`,Son Music

songnames grouping:
- 至愛的回嚮,至愛的迴響
- 新的異象 新的方向,`新的異象，新的方向`
- 坐在寶坐上聖潔羔羊,坐在寶座上聖潔羔羊
- 神真正心意 (The heart of worship),神真正心意 (The Heart of Worship)
- `每一天 (Day By Day)`,每一天
- `Amazing Grace (My Chains Are Gone) 奇異恩典`,`奇異恩典（除掉困鎖）`

# static mapping for song copyright
- 小小的雙手:玻璃海樂團
- 是為祢預備:Milk&Honey Worship
- 仍然敬拜:Flow Music
- 最美好的仗:香港基督徒音樂事工協會(HKACM)
- 主超過我在面對的紅海:RedSea Music
- 讚頌未停:頌恩旋律
- 坐在寶座上聖潔羔羊:Stream Of Praise Music
- 我屬祢:鹹蛋⾳樂事⼯

# "New Song" Definition
- A "new song" is the song that exists in 2025 but not inside `uniquesong_until2024.csv`
- during comparing this new song excel, if the row has `+` or `/` , split the string in to separate song names

# "New Songs Usage"
- Number of worship that used a new song
- If a worship used 3 new songs, count 3, but respect the next rule:
- if a new songs appeared multiple times, only count the first occurence.for example:week1, week5 has newsongA, that new songA only count once.

