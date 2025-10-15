#!/usr/bin/env python3

import json
import re
from datetime import datetime

def remove_emojis():
    """Remove all emojis from the game world data"""
    
    # Load the current world data
    with open('world/world.json', 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    print(f"Processing {len(world_data['nodes'])} nodes to remove emojis")
    
    # Create backup
    backup_filename = f"world_backup_before_emoji_removal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    print(f"Backup created: {backup_filename}")
    
    # Emoji removal regex - matches most Unicode emoji ranges
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"  # dingbats
        u"\U000024C2-\U0001F251"  # enclosed characters
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        u"\U00002600-\U000026FF"  # miscellaneous symbols
        u"\U00002700-\U000027BF"  # dingbats
        "]+", flags=re.UNICODE)
    
    changes_made = 0
    
    def clean_text(text):
        """Remove emojis from text and clean up extra spaces"""
        nonlocal changes_made
        if not isinstance(text, str):
            return text
        
        original = text
        # Remove emojis
        cleaned = emoji_pattern.sub('', text)
        # Clean up multiple spaces and leading/trailing spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        if original != cleaned:
            changes_made += 1
        return cleaned
    
    # Clean node titles and descriptions
    for node_id, node_data in world_data['nodes'].items():
        if 'title' in node_data:
            node_data['title'] = clean_text(node_data['title'])
        if 'description' in node_data:
            node_data['description'] = clean_text(node_data['description'])
        
        # Clean choices
        if 'choices' in node_data:
            for choice in node_data['choices']:
                if 'text' in choice:
                    choice['text'] = clean_text(choice['text'])
                if 'details' in choice:
                    choice['details'] = clean_text(choice['details'])
    
    # Clean start entries
    if 'starts' in world_data:
        for start in world_data['starts']:
            if 'title' in start:
                start['title'] = clean_text(start['title'])
            if 'blurb' in start:
                start['blurb'] = clean_text(start['blurb'])
    
    # Clean any other text fields
    if 'metadata' in world_data:
        for key, value in world_data['metadata'].items():
            if isinstance(value, str):
                world_data['metadata'][key] = clean_text(value)
    
    # Save the cleaned world data
    with open('world/world.json', 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    
    print(f"Removed emojis from {changes_made} text fields")
    print("All emojis have been removed from the game world data")

if __name__ == "__main__":
    remove_emojis()