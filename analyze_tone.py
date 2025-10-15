#!/usr/bin/env python3
"""Analyze tone consistency in world.json content."""

import json
import re
from collections import Counter

def analyze_tone(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', {})
    
    # Patterns that might indicate tone inconsistency
    formal_patterns = [
        r'\byou are\b', r'\byou have\b', r'\byou will\b',
        r'\bshall\b', r'\bmust\b', r'\bcannot\b',
        r'\bthus\b', r'\btherefore\b', r'\bhowever\b'
    ]
    
    casual_patterns = [
        r"you're", r"you'll", r"can't", r"won't", r"don't",
        r'\bokay\b', r'\byeah\b', r'\bwell\b'
    ]
    
    archaic_patterns = [
        r'\bthee\b', r'\bthou\b', r'\bthy\b', r'\bthine\b',
        r'\bhath\b', r'\bdoth\b', r'\bwhence\b', r'\bwhither\b'
    ]
    
    modern_slang = [
        r'\bokay\b', r'\byep\b', r'\bnope\b', r'\bgotcha\b',
        r'\bawesome\b', r'\bcool\b', r'\bweird\b'
    ]
    
    tone_indicators = {
        'formal': formal_patterns,
        'casual': casual_patterns, 
        'archaic': archaic_patterns,
        'modern': modern_slang
    }
    
    tone_analysis = {}
    sentence_lengths = []
    punctuation_usage = Counter()
    
    for node_id, node in nodes.items():
        text = node.get('text', '')
        if not text:
            continue
            
        # Analyze this node's tone
        node_tones = {}
        for tone_type, patterns in tone_indicators.items():
            count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in patterns)
            if count > 0:
                node_tones[tone_type] = count
        
        # Sentence length analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            sentence_lengths.append((node_id, avg_sentence_length, len(sentences)))
        
        # Punctuation analysis
        for char in text:
            if char in '.,;:!?-—':
                punctuation_usage[char] += 1
        
        if node_tones:
            tone_analysis[node_id] = {
                'title': node.get('title', 'No title'),
                'tones': node_tones,
                'text_preview': text[:100] + "..." if len(text) > 100 else text
            }
    
    # Find mixed tone nodes
    mixed_tone_nodes = [(node_id, data) for node_id, data in tone_analysis.items() 
                        if len(data['tones']) > 1]
    
    # Find very long or very short sentences
    long_sentences = [(node_id, avg_len, count) for node_id, avg_len, count in sentence_lengths 
                      if avg_len > 25]
    short_sentences = [(node_id, avg_len, count) for node_id, avg_len, count in sentence_lengths 
                       if avg_len < 8 and count > 1]
    
    print(f"=== Tone Consistency Analysis ===")
    print(f"Total nodes with text: {len([n for n in nodes.values() if n.get('text')])}")
    print(f"Nodes with tone indicators: {len(tone_analysis)}")
    print(f"Mixed tone nodes: {len(mixed_tone_nodes)}")
    print()
    
    print(f"=== Mixed Tone Nodes (potential inconsistencies) ===")
    for node_id, data in sorted(mixed_tone_nodes)[:10]:
        print(f"  {node_id}: {data['title']}")
        print(f"    Tones: {', '.join(f'{k}({v})' for k, v in data['tones'].items())}")
        print(f"    Preview: {data['text_preview']}")
        print()
    
    print(f"=== Very Long Sentences (>25 words avg) ===")
    for node_id, avg_len, count in sorted(long_sentences, key=lambda x: x[1], reverse=True)[:5]:
        title = nodes[node_id].get('title', 'No title')
        print(f"  {node_id}: {title} (avg {avg_len:.1f} words, {count} sentences)")
    
    print(f"\n=== Very Short Sentences (<8 words avg) ===")
    for node_id, avg_len, count in sorted(short_sentences)[:5]:
        title = nodes[node_id].get('title', 'No title')
        print(f"  {node_id}: {title} (avg {avg_len:.1f} words, {count} sentences)")
    
    print(f"\n=== Punctuation Usage ===")
    total_punct = sum(punctuation_usage.values())
    for punct, count in punctuation_usage.most_common():
        percentage = (count / total_punct) * 100 if total_punct > 0 else 0
        print(f"  '{punct}': {count} ({percentage:.1f}%)")
    
    return {
        'tone_analysis': tone_analysis,
        'mixed_tone_nodes': mixed_tone_nodes,
        'sentence_lengths': sentence_lengths
    }

if __name__ == "__main__":
    analysis = analyze_tone("world/world.json")