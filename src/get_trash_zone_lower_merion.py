################################################################################################################################################################################
#   Zone and day LM specific
################################################################################################################################################################################

from dataclasses import dataclass
import json
import logging
import urllib3

http = urllib3.PoolManager()
logger = logging.getLogger(__name__)


def lambda_handler(event, _):
    """Return tuple of collection_day and holiday zone"""

    address = event.get("address")
    zip = event.get("zip")
    
    zone_items = get_zone(address, zip)
    if not zone_items or len(zone_items) != 1:
        return None
    zone_item = zone_items[0]
    #TODO: Remove me!
    logger.warning(f"Return zone item: {zone_item}")
    return zone_item.collection_day, zone_item.holiday_zone

    
def get_zone_items(address) -> list[dict]:
    """Get token and then zone information from matching addresses from LM API"""
    
    # Get LM token
    token_url = "https://www.lowermerion.org/Home/GetToken"     
    token_headers = {
        "Accept": "application/json",
        "User-Agent": "recyclobuddy",
        "Content-Type": "application/json",
    }
    try:
        x = http.request('POST', token_url, headers=token_headers)
        response_dict = json.loads(x._body)
        token = response_dict.get("Token")
    except Exception as e:
        logger.error(f"Failed to get LM token: {e}")
        return

    # Get zone information using token
    search_url = "https://flex.visioninternet.com/api/FeFlexComponent/Get"
    bearer_token = "Bearer " + token
    search_headers = {
        "Accept": "application/json",
        "User-Agent": "recyclobuddy",
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }
    payload = {"pageSize":20,"pageNumber":1,"sortOptions":[],"searchText": address,"searchFields":["Address"],"searchOperator":"OR","searchSeparator":",","Data":{"componentGuid":"f05e2a62-e807-4f30-b450-c2c48770ba5c","listUniqueName":"VHWQOE27X21B7R8"},"filterOptions":[]}
    try:
        y = http.request('POST', search_url, headers=search_headers, body=json.dumps(payload))
    except Exception as e:
        logger.error(f"Failed to get LM zone items: {e}")
        return

    y_dict = json.loads(y._body)
    records = y_dict.get("records")
    if not records:
        return
    items = records.get("items")
    return items
    

def get_day_number(day_text):
    """Get the day number from the day text"""
    if (day_text == "Monday" or day_text=="Mon" or day_text == "MONDAY" or day_text=="MON"):
        return 1
    if (day_text == "Tuesday" or day_text == "Tue" or day_text == "TUESDAY" or day_text == "TUE"):
        return 2
    if (day_text == "Wednesday" or  day_text == "Wed" or day_text == "WEDNESDAY" or  day_text == "WED"):
        return 3
    if (day_text == "Thursday" or  day_text == "Thu" or day_text == "THURSDAY" or  day_text == "THU"):
        return 4
    if (day_text == "Friday" or day_text == "Fri" or day_text == "FRIDAY" or day_text == "FRI"):
        return 5
    if (day_text == "Saturday" or day_text == "Sat" or day_text == "SATURDAY" or day_text == "SAT"):
        return 6
    if (day_text == "Sunday" or  day_text == "Sun" or day_text == "SUNDAY" or  day_text == "SUN"):
        return 7
    return 0


@dataclass
class ZoneItem:
    """Class for relevant itms returned from LM address search"""
    collection_day: int
    holiday_zone: str
    address: str


def get_zone_from_items(items, address, zip):
    """Attempt to match zip as well as address. Return a list of zone information and addresses"""
    zip_string = f"({zip})"

    match_address = [item for item in items if address in item.get("Address")]
    match_zip = [item for item in match_address if zip_string in item.get("Address")]

    if match_zip:
        match_elements = match_zip
    elif match_address:
        match_elements = match_address
    else:
        return []

    return [ZoneItem(
        collection_day=get_day_number(match_element.get("Collection")), 
        holiday_zone=match_element.get("HolZone"),
        address=match_element.get("Address")
    ) for match_element in match_elements]


def get_zone(address, zip) -> list[ZoneItem]:
    """Get a list of ZoneItems, log if none found or multiple items are found"""
    items = get_zone_items(address)
    if not items:
        logger.warning(f"Failed to locate LM zone information for address: {address} and zip: {zip}")
    if len(items) > 1:
        logger.error(f"Returned multiple zones for address: {address}. Should be unique: {items}")
    return get_zone_from_items(items, address, zip)
