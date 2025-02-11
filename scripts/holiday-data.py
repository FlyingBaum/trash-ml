import pandas as pd
from datetime import datetime, timedelta

df_holidays = pd.read_csv('../data/holidays.csv', sep=',', quotechar='"')

def parse_holiday_period(holiday_str, year):
    """
    Wandelt einen Ferien-Zeitraum-String (z.B. "14.04. - 25.04. / 02.05. / 30.05.")
    in eine Liste von (start_date, end_date)-Tupeln um.
    """
    # Vereinheitliche die Trennzeichen
    holiday_str = holiday_str.replace('/', '+')
    parts = holiday_str.split('+')
    intervals = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start_str, end_str = part.split('-')
            # Entferne überflüssige Punkte und Leerzeichen
            start_str = start_str.strip().rstrip('.')
            end_str = end_str.strip().rstrip('.')
            # Erzeuge Start- und Enddatum
            start_date = datetime.strptime(f"{start_str}.{year}", "%d.%m.%Y")
            end_date = datetime.strptime(f"{end_str}.{year}", "%d.%m.%Y")
            # Falls das Enddatum vor dem Startdatum liegt (z.B. 23.12. - 04.01.), 
            # dann ordne das Enddatum dem Folgejahr zu.
            if start_date > end_date:
                end_date = datetime.strptime(f"{end_str}.{year+1}", "%d.%m.%Y")
            intervals.append((start_date, end_date))
        else:
            # Einzeltermin – hier ebenfalls überflüssige Punkte entfernen
            date_str = part.strip().rstrip('.')
            date_obj = datetime.strptime(f"{date_str}.{year}", "%d.%m.%Y")
            intervals.append((date_obj, date_obj))
    return intervals

holidays = {}

for idx, row in df_holidays.iterrows():
    bundesland = row['Bundesland']
    year = int(row['Jahr'])
    if bundesland not in holidays:
        holidays[bundesland] = {}
    if year not in holidays[bundesland]:
        holidays[bundesland][year] = set()
        
    # Alle Ferien-Spalten (ab der 3. Spalte) durchgehen
    for col in df_holidays.columns[2:]:
        # Prüfen, ob in der Spalte ein Wert steht
        if pd.isna(row[col]):
            continue
        holiday_str = row[col]
        intervals = parse_holiday_period(holiday_str, year)
        for start_date, end_date in intervals:
            # Füge alle Tage im Intervall (inklusive Start und Ende) hinzu
            delta_days = (end_date - start_date).days
            for i in range(delta_days + 1):
                tag = start_date + timedelta(days=i)
                holidays[bundesland][year].add(tag)

result_rows = []
for bundesland, years in holidays.items():
    for year, holiday_set in years.items():
        start_year = datetime(year, 1, 1)
        end_year = datetime(year, 12, 31)
        for tag in pd.date_range(start_year, end_year):
            tag_dt = tag.to_pydatetime()
            result_rows.append({
                'Bundesland': bundesland,
                'Datum': tag,
                'is_holiday': tag_dt in holiday_set
            })

holidays_df = pd.DataFrame(result_rows)