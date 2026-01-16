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

# Song name parsing
- the word "祢" is considered the same as "你"
- in song names processing, Disregard appending strings like "Medly", "Chorus Only", ," (Canto)"," (skip verse)"," by Esther Chow"," C1 C2","(Mando)","Communion","Holy Communion","Baptism"
- "Communion","Holy Communion","Baptism" are not a song, consider that empty, skip those.
- some very specific cases I want you to maintain a static mapping:
-- these are the same: "房角石頭（Cornerstone）","Cornerstone", "房角基石","Cornerstone 房角基石"
-- same: "唯獨在基督裡 (In Christ Alone)","唯獨在基督裡"
-- same: "奇異恩典 Amazing Grace (My Chains are Gone)","奇異恩典（除掉困鎖）","奇異恩典(除掉困鎖)",
-- same: 獻上頌讚,獻上頌讚 (Shout To The Lord),獻上頌讚 Shout to The Lord
-- same: King of Kings 萬代君主,萬代君主

#Praise leader name parsing
- "P1: Phoebe" is considered as "Phoebe"
- "A: Cannis" is "Cannis"

You want 祢, 你, and 袮 to be treated as equivalent characters (so songs with any of these variations are considered the same)