import httpx
import json
from datetime import datetime, timedelta, timezone

def fetch_sentinel_data():
    url = "https://endpoints.investing.com/pd-instruments/v1/calendars/economic/events/occurrences"

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://www.investing.com',
        'referer': 'https://www.investing.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    now = datetime.now(timezone.utc)
    start_str = now.strftime('%Y-%m-%dT00:00:00.000Z')
    end_str = (now + timedelta(days=7)).strftime('%Y-%m-%dT23:59:59.999Z')

    params = {
        'domain_id': '1',
        'limit': '200',
        'start_date': start_str,
        'end_date': end_str,
        'country_ids': '25,32,6,37,72,22,17,39,14,10,35,43,36,110,11,26,12,4,5,56'
    }

    with httpx.Client(timeout=15.0) as client:
        response = client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None


def process_sentinel_data(raw_data):
    if not raw_data:
        return []

    event_blueprint = {}
    for event in raw_data.get('events', []):
        event_id = event.get('event_id')
        event_blueprint[event_id] = {
            'name': event.get('short_name', 'Unknown Event'),
            'currency': event.get('currency', 'UNK'),
            'importance': event.get('importance', 'low'),
            'description': event.get('description', 'unavailable')
        }

    high_impact_alerts = []

    for occ in raw_data.get('occurrences', []):
        event_id = occ.get('event_id')
        details = event_blueprint.get(event_id)

        if not details:
            continue

        if details['importance'] == 'high':
            alert = {
                'time': occ.get('occurrence_time'),
                'currency': details['currency'],
                'event': details['name'],
                'previous': occ.get('previous', 'N/A'),
                'forecast': occ.get('forecast', 'N/A'),
                'description': details['description']
            }
            high_impact_alerts.append(alert)

    return high_impact_alerts


if __name__ == '__main__':
    market_data = fetch_sentinel_data()
    sentinel_alerts = process_sentinel_data(market_data)
    print(json.dumps(sentinel_alerts))