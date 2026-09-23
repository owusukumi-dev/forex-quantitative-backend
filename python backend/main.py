from curl_cffi import requests
import json
import logging
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def fetch_sentinel_data():
    url = "https://endpoints.investing.com/pd-instruments/v1/calendars/economic/events/occurrences"


    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.investing.com',
        'referer': 'https://www.investing.com/',
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

    try:

        response = requests.get(url, headers=headers, params=params, impersonate="chrome", timeout=15)

        if response.status_code == 200:
            return response.json()
        elif response.status_code in [403, 401]:
            logging.error(f"Access Denied ({response.status_code}). WAF/Cloudflare blocked the request.")
            return None
        else:
            logging.warning(f"Unexpected status code: {response.status_code}")
            return None

    except Exception as e:
        logging.error(f"Network request failed: {e}")
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

    occurrences = raw_data.get('occurrences', [])
    if not occurrences and 'data' in raw_data:
        occurrences = raw_data['data'].get('occurrences', [])

    for occ in occurrences:
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
    logging.info("Fetching market data via curl_cffi...")
    market_data = fetch_sentinel_data()

    if market_data:
        sentinel_alerts = process_sentinel_data(market_data)
        logging.info(f"Successfully processed {len(sentinel_alerts)} high-impact events.")
        print(json.dumps(sentinel_alerts, indent=4))
    else:
        logging.error("Failed to retrieve market data. No alerts generated.")
