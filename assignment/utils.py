#function to sort event based on unit and assign question alias
def get_event_alias_order(events):
    unique_units = sorted(set(event['unit'] for event in events))
    unit_to_alias = {unit: f"Q{index+1}" for index, unit in enumerate(unique_units)}
    event_order = [unit_to_alias[event['unit']] for event in events]
    return event_order
