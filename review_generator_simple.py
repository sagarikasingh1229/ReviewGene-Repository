#!/usr/bin/env python3
"""
SKU Review Generator - Simplified Standalone Version
AI-Powered Review Generation for Indian E-commerce Products
"""

import os
import sys
import time
import random
import json
import csv
import glob
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import openai

# Add current directory to path for config import
sys.path.append('.')

try:
    from config import (
        OPENAI_API_KEY, OPENAI_MODEL, LANGUAGE_MIXING,
        PRODUCT_BENEFIT_ANALYSIS, PRODUCT_CLASSIFICATIONS,
        PRODUCT_KEYWORDS, CHECKPOINT_SETTINGS, REVIEW_LENGTH_SETTINGS,
        HINGLISH_PHRASES, NATURAL_MIXING_EXAMPLES, RATING_DISTRIBUTION,
        REVIEW_CONTENT_RULES, USERNAME_RULES, DATE_RULES, QUANTITY_RULES,
        OUTPUT_FORMAT
    )
    print("✅ Configuration loaded from config.py")
except ImportError as e:
    print(f"⚠️ Warning: Could not import from config.py: {e}")
    print("💡 Using environment variables and defaults")
    # Provide default values
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = "gpt-4o-mini"
    LANGUAGE_MIXING = {
        "enabled": True, 
        "primary_language": "English", 
        "distribution": {
            "Pure English": 60,      # 60% pure English
            "Hinglish": 30,          # 30% Hinglish
            "Hindi Casual": 10,      # 10% Hindi casual romanized
        }
    }
    RATING_DISTRIBUTION = {
        "5_star": 50,    # ~50% 5-star
        "4_star": 25,    # ~25% 4-star
        "3_star": 20,    # ~20% 3-star
        "2_star": 5      # ~5% 2-star
    }
    REVIEW_CONTENT_RULES = {
        "product_specific_ratio": 70,  # 70% product-specific
        "general_ratio": 30,           # 30% general
        "emojis_enabled": True,
        "emojis_percentage": 15,       # ~10-15% emojis
        "forbidden_words": ["yaar", "dost", "bhai", "friends"],
        "allowed_abbreviations": ["recd", "ok-ok", "thoda", "bilkul", "accha", "sahi"],
        "intentional_typos": True,
        "casual_tone": True
    }
    USERNAME_RULES = {
        "diversity": {
            "north_indian": 25,
            "south_indian": 20,
            "anglo": 20,
            "muslim": 15,
            "single_names": 10,
            "funky_handles": 10
        },
        "funky_handles": [
            "Appu", "rockstar99", "miss_shy", "random123", "foodie_lover89",
            "tech_guy", "mom_of_two", "fitness_freak", "bookworm", "traveler_2025"
        ],
        "must_be_unique": True,
        "no_repeat_across_skus": True
    }
    DATE_RULES = {
        "start_date": "2025-09-01",
        "end_date": "2025-12-31",
        "organic_pacing": True,
        "heavy_days_percentage": 30,
        "uniform_distribution": False
    }
    QUANTITY_RULES = {
        "reviews_per_sku": {"min": 17, "max": 22},
        "multiple_skus_per_generation": True,
        "fmcg_only": True,
        "exclude_pharma": True,
        "exclude_pl": True
    }
    OUTPUT_FORMAT = {
        "columns": ["sku_id", "sku_name", "rating", "review", "post_date", "username"],
        "separator": "\t",
        "date_format": "YYYY-MM-DD"
    }
    PRODUCT_BENEFIT_ANALYSIS = {
        "enabled": True, 
        "use_openai": True, 
        "fallback_benefits": {
            "fever": ["fever reduction", "body temperature control", "fever relief"],
            "pain": ["pain relief", "headache relief", "body pain relief", "analgesic"],
            "vitamin_c": ["vitamin C deficiency", "immunity boost", "antioxidant"],
            "vitamin_d": ["vitamin D deficiency", "bone health", "calcium absorption"],
            "skincare": ["skin hydration", "acne treatment", "anti-aging", "skin repair"],
            "haircare": ["hair growth", "dandruff control", "hair strength", "scalp health"],
            "digestive": ["digestion improvement", "acid reflux", "constipation relief", "gut health"]
        }
    }
    PRODUCT_CLASSIFICATIONS = {
        "PERSONAL CARE": {
            "SKIN CARE": {
                "BODY CARE": ["skin hydration", "moisturizing", "body care", "skin health"],
                "FACE CARE": ["skin brightening", "acne treatment", "anti-aging", "facial care"]
            }
        },
        "NUTRITION & METABOLISM": {
            "VITAMINS AND MINERALS": {
                "VITAMINS AND MINERALS": ["energy boost", "immunity support", "vitamin deficiency", "overall health"]
            }
        }
    }
    PRODUCT_KEYWORDS = {
        "fever": ["dolo", "paracetamol", "acetaminophen", "fever", "temperature"],
        "pain": ["pain", "headache", "migraine", "body pain", "analgesic"],
        "vitamin_c": ["limcee", "vitamin c", "ascorbic acid", "immunity"],
        "skincare": ["cetaphil", "cerave", "cleanser", "moisturizer", "cream"],
        "digestive": ["digestive", "probiotic", "enzyme", "acid reflux", "gut"]
    }
    CHECKPOINT_SETTINGS = {
        "enabled": True, 
        "save_interval": 50, 
        "checkpoint_dir": "checkpoints", 
        "max_checkpoints": 10, 
        "resume_enabled": True, 
        "backup_interval": 100
    }
    REVIEW_LENGTH_SETTINGS = {
        "max_sentences": 3, 
        "target_length": "5-30 words", 
        "distribution": {
            "short": 25, 
            "medium": 40, 
            "long": 35
        },
        "word_limits": {
            "short": {"min": 5, "max": 7},
            "medium": {"min": 8, "max": 14},
            "long": {"min": 15, "max": 30}
        }
    }


class NameGenerator:
    """Handles generation of diverse usernames with multiple patterns"""
    
    def __init__(self):
        self.first_names = self._read_names_from_csv("data/indian_first_names.csv")
        self.last_names = self._read_names_from_csv("data/indian_last_names.csv")
        
        # Fallback names if CSV reading fails
        if not self.first_names:
            self.first_names = ["Arjun", "Diya", "Amit", "Priya", "Rahul", "Neha", "Kavitha", "Nitin", "Sneha", "Vikram"]
        if not self.last_names:
            self.last_names = ["Patel", "Sharma", "Singh", "Kumar", "Verma", "Gupta", "Nair", "Menon", "Reddy", "Iyer"]
        
        # Track used usernames to ensure uniqueness
        self.used_usernames = set()
        
        # Nicknames and variations
        self.nicknames = [
            "Appu", "Bunny", "Chintu", "Dolly", "Golu", "Happy", "Jolly", "Kittu", "Lucky", "Mickey",
            "Nikki", "Oscar", "Pinky", "Queen", "Ricky", "Sunny", "Tinku", "Usha", "Vicky", "Winnie",
            "Xena", "Yoyo", "Zara", "Aadi", "Bebo", "Chiku", "Didi", "Esha", "Fiza", "Gigi"
        ]
        
        # Alphanumeric patterns
        self.alphanumeric_patterns = [
            "{name}{year}", "{name}{number}", "{name}_{number}", "{name}{random}",
            "{number}{name}", "{random}{name}", "{name}{emoji}", "{emoji}{name}"
        ]
        
        # Numbers and years for alphanumeric
        self.years = ["2020", "2021", "2022", "2023", "2024", "2025"]
        self.numbers = ["123", "456", "789", "007", "99", "88", "77", "66", "55", "44", "33", "22", "11"]
        self.random_chars = ["xyz", "abc", "def", "qwe", "asd", "zxc", "rty", "fgh", "vbn", "mkl"]
        
        # Emojis for fun usernames
        self.emojis = ["😊", "🌟", "💫", "✨", "🎉", "🎈", "🎊", "🎋", "🎍", "🎎", "🎏", "🎐", "🎀", "🎁", "🎂", "🎃", "🎄", "🎅", "🎆", "🎇"]
        
        # Other language scripts (Hindi, Tamil, Telugu, etc.)
        self.hindi_names = ["अर्जुन", "दीया", "अमित", "प्रिया", "राहुल", "नेहा", "कविता", "नितिन", "स्नेहा", "विक्रम"]
        self.tamil_names = ["அருஜுன்", "தீயா", "அமித்", "பிரியா", "ராகுல்", "நேஹா", "கவிதா", "நிதின்", "ஸ்னேஹா", "விக்ரம்"]
        self.telugu_names = ["అర్జున్", "దీయా", "అమిత్", "ప్రియా", "రాహుల్", "నేహా", "కవిత", "నితిన్", "స్నేహ", "విక్రమ్"]
        
        # Funky handles from config
        self.funky_handles = USERNAME_RULES.get("funky_handles", [
            "Appu", "rockstar99", "miss_shy", "random123", "foodie_lover89",
            "tech_guy", "mom_of_two", "fitness_freak", "bookworm", "traveler_2025"
        ])
    
    def _read_names_from_csv(self, filename: str) -> List[str]:
        """Read names from CSV file"""
        try:
            names = []
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Get the first column value (header is first_name or last_name)
                        if row and list(row.values())[0].strip():
                            names.append(list(row.values())[0].strip())
            return names
        except Exception as e:
            print(f"⚠️ Warning: Could not read {filename}: {e}")
            return []
    
    def generate_username(self) -> str:
        """Generate diverse usernames with multiple patterns"""
        # Define distribution for different username types
        username_types = {
            "first_last_combination": 30,    # 30% First + Last name
            "first_name_only": 20,           # 20% First name only
            "last_name_only": 15,            # 15% Last name only
            "nickname": 10,                   # 10% Nicknames
            "alphanumeric": 15,              # 15% Alphanumeric
            "other_script": 5,               # 5% Other language scripts
            "funky_handle": 5                # 5% Funky handles
        }
        
        # Select username type based on distribution
        rand = random.random() * 100
        cumulative = 0
        
        for username_type, percentage in username_types.items():
            cumulative += percentage
            if rand < cumulative:
                return self._generate_specific_username_type(username_type)
        
        # Fallback to first_last_combination
        return self._generate_specific_username_type("first_last_combination")
    
    def _generate_specific_username_type(self, username_type: str) -> str:
        """Generate specific type of username"""
        if username_type == "first_last_combination":
            return self._generate_first_last_combination()
        elif username_type == "first_name_only":
            return self._generate_first_name_only()
        elif username_type == "last_name_only":
            return self._generate_last_name_only()
        elif username_type == "nickname":
            return self._generate_nickname()
        elif username_type == "alphanumeric":
            return self._generate_alphanumeric()
        elif username_type == "other_script":
            return self._generate_other_script()
        elif username_type == "funky_handle":
            return self._generate_funky_handle()
        else:
            return self._generate_first_last_combination()
    
    def _generate_first_last_combination(self) -> str:
        """Generate First + Last name combination"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        username = f"{first_name} {last_name}"
        
        # Ensure uniqueness
        attempts = 0
        while username in self.used_usernames and attempts < 50:
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            username = f"{first_name} {last_name}"
            attempts += 1
        
        self.used_usernames.add(username)
        return username
    
    def _generate_first_name_only(self) -> str:
        """Generate first name only"""
        first_name = random.choice(self.first_names)
        
        # Sometimes add a number or year
        if random.random() < 0.3:
            if random.random() < 0.5:
                first_name += random.choice(self.years)
            else:
                first_name += random.choice(self.numbers)
        
        # Ensure uniqueness
        attempts = 0
        while first_name in self.used_usernames and attempts < 50:
            first_name = random.choice(self.first_names)
            if random.random() < 0.3:
                if random.random() < 0.5:
                    first_name += random.choice(self.years)
                else:
                    first_name += random.choice(self.numbers)
            attempts += 1
        
        self.used_usernames.add(first_name)
        return first_name
    
    def _generate_last_name_only(self) -> str:
        """Generate last name only"""
        last_name = random.choice(self.last_names)
        
        # Sometimes add a number or year
        if random.random() < 0.3:
            if random.random() < 0.5:
                last_name += random.choice(self.years)
            else:
                last_name += random.choice(self.numbers)
        
        # Ensure uniqueness
        attempts = 0
        while last_name in self.used_usernames and attempts < 50:
            last_name = random.choice(self.last_names)
            if random.random() < 0.3:
                if random.random() < 0.5:
                    last_name += random.choice(self.years)
                else:
                    last_name += random.choice(self.numbers)
            attempts += 1
        
        self.used_usernames.add(last_name)
        return last_name
    
    def _generate_nickname(self) -> str:
        """Generate nickname"""
        nickname = random.choice(self.nicknames)
        
        # Sometimes add a number or emoji
        if random.random() < 0.4:
            if random.random() < 0.6:
                nickname += random.choice(self.numbers)
            else:
                nickname += random.choice(self.emojis)
        
        # Ensure uniqueness
        attempts = 0
        while nickname in self.used_usernames and attempts < 50:
            nickname = random.choice(self.nicknames)
            if random.random() < 0.4:
                if random.random() < 0.6:
                    nickname += random.choice(self.numbers)
                else:
                    nickname += random.choice(self.emojis)
            attempts += 1
        
        self.used_usernames.add(nickname)
        return nickname
    
    def _generate_alphanumeric(self) -> str:
        """Generate alphanumeric username"""
        # Choose a base name (first name or nickname)
        base_name = random.choice(self.first_names + self.nicknames)
        
        # Choose a pattern
        pattern = random.choice(self.alphanumeric_patterns)
        
        # Generate username based on pattern
        if "{name}{year}" in pattern:
            username = base_name + random.choice(self.years)
        elif "{name}{number}" in pattern:
            username = base_name + random.choice(self.numbers)
        elif "{name}_{number}" in pattern:
            username = base_name + "_" + random.choice(self.numbers)
        elif "{name}{random}" in pattern:
            username = base_name + random.choice(self.random_chars)
        elif "{number}{name}" in pattern:
            username = random.choice(self.numbers) + base_name
        elif "{random}{name}" in pattern:
            username = random.choice(self.random_chars) + base_name
        elif "{name}{emoji}" in pattern:
            username = base_name + random.choice(self.emojis)
        elif "{emoji}{name}" in pattern:
            username = random.choice(self.emojis) + base_name
        else:
            username = base_name + random.choice(self.numbers)
        
        # Ensure uniqueness
        attempts = 0
        while username in self.used_usernames and attempts < 50:
            base_name = random.choice(self.first_names + self.nicknames)
            pattern = random.choice(self.alphanumeric_patterns)
            if "{name}{year}" in pattern:
                username = base_name + random.choice(self.years)
            elif "{name}{number}" in pattern:
                username = base_name + random.choice(self.numbers)
            elif "{name}_{number}" in pattern:
                username = base_name + "_" + random.choice(self.numbers)
            elif "{name}{random}" in pattern:
                username = base_name + random.choice(self.random_chars)
            elif "{number}{name}" in pattern:
                username = random.choice(self.numbers) + base_name
            elif "{random}{name}" in pattern:
                username = random.choice(self.random_chars) + base_name
            elif "{name}{emoji}" in pattern:
                username = base_name + random.choice(self.emojis)
            elif "{emoji}{name}" in pattern:
                username = random.choice(self.emojis) + base_name
            else:
                username = base_name + random.choice(self.numbers)
            attempts += 1
        
        self.used_usernames.add(username)
        return username
    
    def _generate_other_script(self) -> str:
        """Generate username in other language scripts"""
        # Choose a script
        script_choice = random.choice(["hindi", "tamil", "telugu"])
        
        if script_choice == "hindi":
            username = random.choice(self.hindi_names)
        elif script_choice == "tamil":
            username = random.choice(self.tamil_names)
        elif script_choice == "telugu":
            username = random.choice(self.telugu_names)
        else:
            username = random.choice(self.hindi_names)
        
        # Sometimes add a number
        if random.random() < 0.3:
            username += random.choice(self.numbers)
        
        # Ensure uniqueness
        attempts = 0
        while username in self.used_usernames and attempts < 50:
            script_choice = random.choice(["hindi", "tamil", "telugu"])
            if script_choice == "hindi":
                username = random.choice(self.hindi_names)
            elif script_choice == "tamil":
                username = random.choice(self.tamil_names)
            elif script_choice == "telugu":
                username = random.choice(self.telugu_names)
            else:
                username = random.choice(self.hindi_names)
            
            if random.random() < 0.3:
                username += random.choice(self.numbers)
            attempts += 1
        
        self.used_usernames.add(username)
        return username
    
    def _generate_funky_handle(self) -> str:
        """Generate funky handle"""
        username = random.choice(self.funky_handles)
        
        # Sometimes modify it
        if random.random() < 0.4:
            username += random.choice(self.numbers)
        
        # Ensure uniqueness
        attempts = 0
        while username in self.used_usernames and attempts < 50:
            username = random.choice(self.funky_handles)
            if random.random() < 0.4:
                username += random.choice(self.numbers)
            attempts += 1
        
        self.used_usernames.add(username)
        return username
    
    def get_name_count(self) -> tuple:
        """Get count of available names"""
        return len(self.first_names), len(self.last_names)
    
    def reset_used_usernames(self):
        """Reset used usernames for new generation"""
        self.used_usernames.clear()


class ReviewContentGenerator:
    """Generates review content using OpenAI API"""
    
    def __init__(self, api_key: str, model: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.generated_reviews = set()  # Track generated reviews to avoid duplicates
    
    def generate_review(self, sku_name: str, sku_id: str, brand: str = None,
                       classifier_1: str = None, classifier_2: str = None,
                       classifier_3: str = None, points: float = None,
                       product_benefits: Dict = None) -> str:
        """Generate a realistic customer review"""
        try:
            # Prepare the prompt with all product details
            prompt = self._create_review_prompt(
                sku_name, brand, classifier_1, classifier_2, classifier_3,
                points, product_benefits
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at generating SHORT, authentic customer reviews that sound like real Indians writing them. Keep reviews to maximum 2 sentences - like real customers actually write. IMPORTANT: Generate a good mix of English, Hinglish, and Hindi reviews (aim for 20% pure English, 25% English+Hindi, 25% Hinglish+English). CRITICAL: Do NOT mention SKU codes, product IDs, or start reviews with brand names. Focus on natural language mixing, product-specific details with actual medical benefits, and authentic Indian review style. MOST IMPORTANT: Each review must be UNIQUE and DIFFERENT from others - avoid repetitive phrases, vary sentence structures, focus on different benefits, and use creative language patterns."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.9
            )
            
            review = response.choices[0].message.content.strip()
            
            # Check if this review is too similar to previously generated ones
            if self._is_review_too_similar(review):
                print(f"⚠️ Generated review too similar, regenerating...")
                # Try one more time with higher temperature
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert at generating SHORT, authentic customer reviews that sound like real Indians writing them. Keep reviews to maximum 2 sentences - like real customers actually write. IMPORTANT: Generate a good mix of English, Hinglish, and Hindi reviews (aim for 20% pure English, 25% English+Hindi, 25% Hinglish+English). CRITICAL: Do NOT mention SKU codes, product IDs, or start reviews with brand names. Focus on natural language mixing, product-specific details with actual medical benefits, and authentic Indian review style. MOST IMPORTANT: Each review must be UNIQUE and DIFFERENT from others - avoid repetitive phrases, vary sentence structures, focus on different benefits, and use creative language patterns."},
                        {"role": "user", "content": prompt + "\n\nIMPORTANT: Make this review completely different from typical reviews. Be creative and unique!"}
                    ],
                    max_tokens=100,
                    temperature=0.95
                )
                review = response.choices[0].message.content.strip()
            
            # Store this review to check future duplicates
            self.generated_reviews.add(review)
            return review
            
        except Exception as e:
            print(f"Error generating review for {sku_name}: {e}")
            return self._generate_fallback_review_with_benefits(
                sku_name, brand, points, product_benefits
            )
    
    def _create_review_prompt(self, sku_name: str, brand: str,
                             classifier_1: str, classifier_2: str, classifier_3: str,
                             points: float, product_benefits: Dict) -> str:
        """Create the review generation prompt with new requirements"""
        # Extract benefit information safely
        primary_benefit = product_benefits.get('primary_benefit', 'general health support') if product_benefits else 'general health support'
        benefits = product_benefits.get('benefits', []) if product_benefits else []
        medical_conditions = product_benefits.get('medical_conditions', []) if product_benefits else []
        
        # Select language pattern and review length
        selected_pattern = self._select_language_pattern(LANGUAGE_MIXING.get("distribution", {}))
        selected_length = self.select_review_length()
        word_limits = REVIEW_LENGTH_SETTINGS.get("word_limits", {}).get(selected_length, {"min": 5, "max": 15})
        
        # Determine content focus (product-specific vs general)
        content_focus = "product-specific" if random.random() < REVIEW_CONTENT_RULES.get("product_specific_ratio", 70) / 100 else "general"
        
        # Add emoji if enabled
        add_emoji = random.random() < REVIEW_CONTENT_RULES.get("emojis_percentage", 15) / 100
        
        prompt = f"""
        You are a Super AI that generates synthetic customer reviews for FMCG SKUs only.
        Your outputs must always be 1000000% accurate and follow every instruction from start to finish — no forgetting, no skipping, no duplicating.

        Generate a realistic customer review for: "{sku_name}"

        PRODUCT DETAILS:
        - Product Name: {sku_name}
        - Brand: {brand or 'Not specified'}
        - Category: {classifier_1 or 'Not specified'}
        - Sub-category: {classifier_2 or 'Not specified'}
        - Specific Type: {classifier_3 or 'Not specified'}
        - Primary Benefit: {primary_benefit}
        - Additional Benefits: {', '.join(benefits[:3]) if benefits else 'General health support'}

        CRITICAL REQUIREMENTS:

        1. LANGUAGE MIXING (Selected: {selected_pattern}):
           - 60% English: "Used daily after bath, skin didn't feel dry even in AC rooms"
           - 30% Hinglish: "Finally sugar free biscuit jo tasty bhi hai, mom diabetic hai so perfect"
           - 10% Hindi Casual: "Cap loose tha, wipes thoda dry lage baad me"
           
           ❌ FORBIDDEN: "yaar", "dost", "bhai", "friends" — NO buddy tone
           ✅ ALLOWED: "recd", "ok-ok", "thoda", "bilkul", "accha", "sahi"

        2. REVIEW LENGTH (Selected: {selected_length}):
           - Short (5-7 words): {word_limits.get('min', 5)}-{word_limits.get('max', 7)} words
           - Medium (8-14 words): 8-14 words  
           - Long (15-30 words): 15-30 words
           
           Target: {word_limits.get('min', 5)}-{word_limits.get('max', 15)} words

        3. CONTENT FOCUS (Selected: {content_focus}):
           - Product-specific (70%): hydration, sugar-free, rash-free, taste, freshness, skin benefits
           - General (30%): delivery, packaging, price, value for money

        4. TONE & STYLE:
           - Must sound real and casual like on e-commerce sites
           - Include intentional typos, abbreviations, shorthand
           - Reviews must vary in style: some blunt, some chatty, some detailed
           - Personal experience only — NO medical guarantees
           - Casual, authentic, imperfect writing style

        5. EMOJIS: {'✅ Include 1-2 emojis' if add_emoji else '❌ No emojis'}

        6. FORBIDDEN:
           - SKU codes, product IDs, technical specifications
           - Starting with brand names
           - Medical guarantees or unsafe claims
           - Formal Hindi ("utpad vishwasniya laga")
           - Repetitive phrases

        EXAMPLES OF GOOD REVIEWS:
        - "Used daily after bath, skin didn't feel dry even in AC rooms. impressed!"
        - "Finally sugar free biscuit jo tasty bhi hai, mom diabetic hai so perfect."
        - "Cap loose tha, wipes thoda dry lage baad me."
        - "Quality bahut acchi hai, really happy with the purchase"
        - "Delivery fast thi, product bhi perfect condition mein aaya"

        EXAMPLES OF WHAT NOT TO DO:
        - ❌ "CeraVe ka yeh cream bahut accha hai" (starts with brand)
        - ❌ "Product CER0576 bahut accha hai" (mentions SKU)
        - ❌ "yaar bahut accha hai dost" (buddy tone)
        - ❌ "utpad vishwasniya laga" (formal Hindi)

        Generate ONE review that follows ALL these rules exactly:"""
        
        return prompt
    
    def _select_language_pattern(self, distribution: dict) -> str:
        """Select language pattern based on distribution weights"""
        if not distribution:
            return "Mixed Natural"
        
        # Convert distribution to list of tuples for weighted selection
        patterns = list(distribution.keys())
        weights = list(distribution.values())
        
        # Normalize weights to sum to 1
        total_weight = sum(weights)
        if total_weight == 0:
            return "Mixed Natural"
        
        normalized_weights = [w / total_weight for w in weights]
        
        # Use random.choices for weighted selection
        import random
        selected = random.choices(patterns, weights=normalized_weights, k=1)[0]
        return selected
    
    def _is_review_too_similar(self, new_review: str) -> bool:
        """Check if a new review is too similar to previously generated ones"""
        if not self.generated_reviews:
            return False
        
        new_review_lower = new_review.lower()
        
        # Check for common repetitive phrases
        repetitive_phrases = [
            "kaafi effective hain",
            "cravings bilkul kam ho gayi hain",
            "bahut accha hai",
            "bilkul sahi hai",
            "perfect hai",
            "recommend karunga",
            "satisfied hun"
        ]
        
        # Count how many repetitive phrases are in the new review
        repetitive_count = sum(1 for phrase in repetitive_phrases if phrase in new_review_lower)
        
        # If more than 2 repetitive phrases, consider it too similar
        if repetitive_count >= 2:
            return True
        
        # Check for exact matches (shouldn't happen but safety check)
        if new_review in self.generated_reviews:
            return True
        
        # Check for very similar structure (same starting words)
        for existing_review in self.generated_reviews:
            existing_words = existing_review.lower().split()[:3]  # First 3 words
            new_words = new_review_lower.split()[:3]
            
            if existing_words == new_words:
                return True
        
        return False
    
    def _generate_fallback_review_with_benefits(self, sku_name: str, brand: str,
                                             points: float, product_benefits: Dict) -> str:
        """Generate fallback review when API fails"""
        # Extract benefit information safely
        primary_benefit = product_benefits.get('primary_benefit', 'general health support') if product_benefits else 'general health support'
        benefits = product_benefits.get('benefits', []) if product_benefits else []
        
        # Create brand context
        brand_context = f" from {brand}" if brand else ""
        
        # Define benefit phrases
        benefit_phrases = []
        if benefits:
            benefit_phrases = [f"really helps with {benefits[0].lower()}" if benefits else "provides good health support"]
        
        # Base fallback reviews
        fallback_reviews = [
            f"Product bahut accha hai yaar! {primary_benefit} ke liye perfect hai{brand_context}.",
            f"Great product hai, {primary_benefit} ke liye bilkul sahi hai{brand_context}.",
            f"Works perfectly for {primary_benefit}, bilkul perfect hai{brand_context}.",
            f"Kaafi sahi hai yaar, {primary_benefit} ke liye recommend karunga{brand_context}.",
            f"Product accha hai, {primary_benefit} ke liye very good value{brand_context}.",
            f"This product works perfectly for {primary_benefit}, highly recommend!",
            f"Excellent quality and effective results for {primary_benefit}.",
            f"Great value for money, {primary_benefit} ke liye perfect choice.",
            f"Amazing results, this product exceeded my expectations for {primary_benefit}."
        ]
        
        # Add benefit-specific reviews if available (keep them short)
        if benefit_phrases:
            fallback_reviews.extend([
                f"Really good hai yaar! {benefit_phrases[0]}.",
                f"Product accha hai, {benefit_phrases[0]}.",
                f"Quality bahut acchi hai, {benefit_phrases[0]}."
            ])
        
        # Add rating-specific reviews if available (keep them short)
        if points:
            if points >= 4.5:
                fallback_reviews.append(f"Highly rated product! {primary_benefit} ke liye perfect choice.")
            elif points >= 4.0:
                fallback_reviews.append(f"Good rating - {points}/5 stars. {primary_benefit} ke liye reliable hai.")
            elif points >= 3.0:
                fallback_reviews.append(f"Mixed reviews - {points}/5 stars. But {primary_benefit} ke liye kaam kar gaya.")
        
        return random.choice(fallback_reviews)
    
    def generate_rating(self) -> int:
        """Generate rating based on new distribution"""
        rand = random.random()
        if rand < RATING_DISTRIBUTION.get("5_star", 50) / 100:
            return 5      # ~50% 5-star
        elif rand < (RATING_DISTRIBUTION.get("5_star", 50) + RATING_DISTRIBUTION.get("4_star", 25)) / 100:
            return 4      # ~25% 4-star
        elif rand < (RATING_DISTRIBUTION.get("5_star", 50) + RATING_DISTRIBUTION.get("4_star", 25) + RATING_DISTRIBUTION.get("3_star", 20)) / 100:
            return 3      # ~20% 3-star
        else:
            return 2      # ~5% 2-star
    
    def generate_date(self) -> str:
        """Generate date from 2025-09-01 onwards with organic pacing"""
        start_date = datetime.strptime(DATE_RULES.get("start_date", "2025-09-01"), "%Y-%m-%d")
        end_date = datetime.strptime(DATE_RULES.get("end_date", "2025-12-31"), "%Y-%m-%d")
        
        # Calculate days range
        days_range = (end_date - start_date).days
        
        # Generate organic pacing (some heavy days, some light)
        if random.random() < DATE_RULES.get("heavy_days_percentage", 30) / 100:
            # Heavy day - more reviews
            review_date = start_date + timedelta(days=random.randint(0, days_range))
        else:
            # Light day - fewer reviews
            review_date = start_date + timedelta(days=random.randint(0, days_range))
        
        return review_date.strftime("%Y-%m-%d")
    
    def select_review_length(self) -> str:
        """Select review length based on new distribution"""
        distribution = REVIEW_LENGTH_SETTINGS.get("distribution", {})
        rand = random.random()
        
        if rand < distribution.get("short", 25) / 100:
            return "short"
        elif rand < (distribution.get("short", 25) + distribution.get("medium", 40)) / 100:
            return "medium"
        else:
            return "long"


class ProductBenefitAnalyzer:
    """Analyzes product benefits using OpenAI API"""
    
    def __init__(self, api_key: str, model: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def analyze_product_benefits(self, sku_name: str, brand: str = None, 
                               classifier_1: str = None, classifier_2: str = None, 
                               classifier_3: str = None) -> Dict:
        """Analyze product benefits using OpenAI API"""
        try:
            # Simple fallback benefits for now
            fallback_benefits = {
                'primary_benefit': 'general health support',
                'benefits': ['overall wellness', 'health maintenance'],
                'medical_conditions': ['general health'],
                'usage_notes': 'Follow package instructions',
                'target_audience': 'Adults seeking health support',
                'source': 'Product analysis',
                'brand': brand or 'Not specified',
                'classifications': [classifier_1 or '', classifier_2 or '', classifier_3 or '']
            }
            
            # Prepare prompt for OpenAI
            prompt = self._create_benefit_analysis_prompt(
                sku_name, brand, classifier_1, classifier_2, classifier_3
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert medical and pharmaceutical analyst. Provide accurate, medically sound product benefit analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse response
            content = response.choices[0].message.content
            return self._parse_benefit_response(content, fallback_benefits)
            
        except Exception as e:
            print(f"Error analyzing product benefits for {sku_name}: {e}")
            return self._get_default_benefits(brand, classifier_1, classifier_2, classifier_3)
    
    def _create_benefit_analysis_prompt(self, sku_name: str, brand: str,
                                      classifier_1: str, classifier_2: str, 
                                      classifier_3: str) -> str:
        """Create prompt for benefit analysis"""
        return f"""
        Analyze the medical benefits and uses for this product:
        
        Product: {sku_name}
        Brand: {brand or 'Not specified'}
        Category: {classifier_1 or 'Not specified'}
        Sub-category: {classifier_2 or 'Not specified'}
        Specific Type: {classifier_3 or 'Not specified'}
        
        Provide analysis in this exact JSON format:
        {{
            "primary_benefit": "Main health benefit",
            "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
            "medical_conditions": ["Condition 1", "Condition 2"],
            "usage_notes": "How to use",
            "target_audience": "Who should use this",
            "source": "Analysis source",
            "brand": "{brand or 'Not specified'}",
            "classifications": ["{classifier_1 or ''}", "{classifier_2 or ''}", "{classifier_3 or ''}"]
        }}
        
        Base your analysis on the product name, category, and known medical knowledge.
        """
    
    def _parse_benefit_response(self, content: str, fallback_benefits: Dict) -> Dict:
        """Parse OpenAI response and extract benefits"""
        try:
            # Try to parse as JSON
            parsed = json.loads(content)
            
            # Ensure all required keys exist
            required_keys = ['primary_benefit', 'benefits', 'medical_conditions', 
                           'usage_notes', 'target_audience', 'source', 'brand', 'classifications']
            
            for key in required_keys:
                if key not in parsed:
                    parsed[key] = fallback_benefits.get(key, 'Not specified')
            
            return parsed
            
        except json.JSONDecodeError:
            # Fallback to text extraction
            return self._extract_benefits_from_text(content, fallback_benefits)
    
    def _extract_benefits_from_text(self, text: str, fallback_benefits: Dict) -> Dict:
        """Extract benefits from raw text response"""
        # Simple text extraction as fallback
        lines = text.split('\n')
        benefits = []
        medical_conditions = []
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['benefit', 'help', 'treat', 'relieve']):
                benefits.append(line)
            elif any(word in line.lower() for word in ['condition', 'disease', 'symptom']):
                medical_conditions.append(line)
        
        return {
            'primary_benefit': benefits[0] if benefits else fallback_benefits.get('primary_benefit', 'General health support'),
            'benefits': benefits[:3] if benefits else fallback_benefits.get('benefits', ['General wellness']),
            'medical_conditions': medical_conditions[:2] if medical_conditions else fallback_benefits.get('medical_conditions', ['General health']),
            'usage_notes': fallback_benefits.get('usage_notes', 'Follow package instructions'),
            'target_audience': fallback_benefits.get('target_audience', 'Adults seeking health support'),
            'source': 'Text analysis fallback',
            'brand': fallback_benefits.get('brand', 'Not specified'),
            'classifications': fallback_benefits.get('classifications', [])
        }
    
    def _get_default_benefits(self, brand: str, classifier_1: str, 
                             classifier_2: str, classifier_3: str) -> Dict:
        """Get default benefits when analysis fails"""
        return {
            'primary_benefit': 'General health support',
            'benefits': ['General wellness'],
            'medical_conditions': ['General health'],
            'usage_notes': 'Follow package instructions',
            'target_audience': 'Adults seeking health support',
            'source': 'Fallback analysis',
            'brand': brand or 'Not specified',
            'classifications': [classifier_1 or '', classifier_2 or '', classifier_3 or '']
        }


class CheckpointManager:
    """Manages checkpointing and resuming functionality"""
    
    def __init__(self):
        self.checkpoint_dir = "checkpoints"
        self.save_interval = 50
        self.backup_interval = 100
        self.max_checkpoints = 10
        
        # Create checkpoint directory if it doesn't exist
        os.makedirs(self.checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(self, results: List[Dict], input_file: str, 
                       mode: str, checkpoint_number: str) -> str:
        """Save current results as a checkpoint"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{os.path.splitext(os.path.basename(input_file))[0]}_{mode}_{checkpoint_number}_{timestamp}.json"
        filepath = os.path.join(self.checkpoint_dir, filename)
        
        checkpoint_data = {
            "timestamp": timestamp,
            "input_file": input_file,
            "mode": mode,
            "checkpoint_number": str(checkpoint_number),
            "total_reviews": len(results),
            "results": results
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Checkpoint saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"⚠️ Warning: Could not save checkpoint: {e}")
            return ""
    
    def load_checkpoint(self, input_file: str, mode: str) -> Tuple[List[Dict], int]:
        """Load the latest checkpoint for resuming"""
        try:
            # Find checkpoints for this input file and mode
            pattern = os.path.join(
                self.checkpoint_dir, 
                f"{os.path.splitext(os.path.basename(input_file))[0]}_{mode}_*.json"
            )
            checkpoint_files = glob.glob(pattern)
            
            if not checkpoint_files:
                return [], 0
            
            # Sort by timestamp (newest first)
            checkpoint_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            latest_checkpoint = checkpoint_files[0]
            
            with open(latest_checkpoint, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            results = checkpoint_data.get("results", [])
            total_reviews = checkpoint_data.get("total_reviews", 0)
            
            print(f"🔄 Loaded checkpoint: {latest_checkpoint}")
            print(f"   Previous progress: {total_reviews} reviews")
            
            return results, total_reviews
            
        except Exception as e:
            print(f"⚠️ Warning: Could not load checkpoint: {e}")
            return [], 0
    
    def show_checkpoint_status(self, input_file: str, mode: str):
        """Display information about existing checkpoints"""
        try:
            pattern = os.path.join(
                self.checkpoint_dir, 
                f"{os.path.splitext(os.path.basename(input_file))[0]}_{mode}_*.json"
            )
            checkpoint_files = glob.glob(pattern)
            
            if not checkpoint_files:
                print("📊 No checkpoints found")
                return
            
            # Sort by modification time (newest first)
            checkpoint_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            print(f"📊 Found {len(checkpoint_files)} checkpoints:")
            
            for i, filepath in enumerate(checkpoint_files[:5], 1):  # Show only first 5
                filename = os.path.basename(filepath)
                file_size = os.path.getsize(filepath)
                file_size_kb = file_size / 1024
                
                print(f"   {i}. {filename} ({file_size_kb:.1f} KB)")
            
            if len(checkpoint_files) > 5:
                print(f"   ... and {len(checkpoint_files) - 5} more")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not show checkpoint status: {e}")


class ReviewGenerator:
    """Main class for generating SKU reviews"""
    
    def __init__(self):
        """Initialize the ReviewGenerator with all components"""
        # Configuration
        self.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in config.py or environment variable")
        
        # Initialize components
        self.name_generator = NameGenerator()
        self.review_generator = ReviewContentGenerator(self.api_key, self.model)
        self.benefit_analyzer = ProductBenefitAnalyzer(self.api_key, self.model)
        self.checkpoint_manager = CheckpointManager()
        
        # Display initialization info
        self._display_initialization_info()
    
    def _display_initialization_info(self):
        """Display system initialization information"""
        print(f"✅ Using OpenAI model: {self.model}")
        
        # Name database info
        first_count, last_count = self.name_generator.get_name_count()
        print(f"\n👥 Name Database:")
        print(f"   First Names: {first_count}")
        print(f"   Last Names: {last_count}")
        print(f"   Total Combinations: {first_count * last_count:,}")
        
        print(f"\n🎭 Username Diversity:")
        print(f"   • First + Last combinations: 30%")
        print(f"   • First name only: 20%")
        print(f"   • Last name only: 15%")
        print(f"   • Nicknames: 10%")
        print(f"   • Alphanumeric: 15%")
        print(f"   • Other scripts (Hindi/Tamil/Telugu): 5%")
        print(f"   • Funky handles: 5%")
        
        print(f"\n📁 File Format Support:")
        print(f"✅ Supported Formats: Excel (.xlsx, .xls) and CSV (.csv)")
        print(f"📊 Required Columns:")
        required_columns = [
            "sku_id", "Name", "brand", "product_discount_category",
            "Classifier 1", "classifier 2", "classifier 3"
        ]
        for column in required_columns:
            print(f"   • {column}")
        
        # Display config usage info
        print(f"\n⚙️ Configuration Usage:")
        print(f"   Language Mixing: {'✅ Enabled' if LANGUAGE_MIXING.get('enabled', False) else '❌ Disabled'}")
        print(f"   Review Length: {REVIEW_LENGTH_SETTINGS.get('target_length', 'Not set')}")
        print(f"   Checkpointing: {'✅ Enabled' if CHECKPOINT_SETTINGS.get('enabled', False) else '❌ Disabled'}")
        print(f"   Product Benefits: {'✅ Enhanced' if PRODUCT_BENEFIT_ANALYSIS.get('enabled', False) else '❌ Basic'}")
    
    def _enhance_benefits_with_config(self, product_benefits: Dict, sku_name: str, 
                                    classifier_1: str, classifier_2: str, classifier_3: str) -> Dict:
        """Enhance product benefits using config classifications and keywords"""
        enhanced = product_benefits.copy() if product_benefits else {}
        
        # Use PRODUCT_CLASSIFICATIONS to find relevant benefits
        if classifier_1 in PRODUCT_CLASSIFICATIONS:
            category_data = PRODUCT_CLASSIFICATIONS[classifier_1]
            
            if classifier_2 in category_data:
                subcategory_data = category_data[classifier_2]
                
                if classifier_3 in subcategory_data:
                    # Found specific classification
                    specific_benefits = subcategory_data[classifier_3]
                    if specific_benefits:
                        enhanced['specific_benefits'] = specific_benefits
                        enhanced['primary_benefit'] = specific_benefits[0] if specific_benefits else 'general health support'
                
                # Add subcategory benefits
                if isinstance(subcategory_data, dict):
                    for key, benefits in subcategory_data.items():
                        if isinstance(benefits, list):
                            enhanced[f'{key.lower()}_benefits'] = benefits
                elif isinstance(subcategory_data, list):
                    enhanced['subcategory_benefits'] = subcategory_data
        
        # Use PRODUCT_KEYWORDS to find relevant keywords
        sku_lower = sku_name.lower()
        relevant_keywords = []
        
        for keyword_category, keywords in PRODUCT_KEYWORDS.items():
            if any(keyword in sku_lower for keyword in keywords):
                relevant_keywords.extend(keywords)
        
        if relevant_keywords:
            enhanced['relevant_keywords'] = relevant_keywords[:5]  # Top 5 relevant keywords
        
        # Use FALLBACK_BENEFITS if no specific benefits found
        fallback_benefits = PRODUCT_BENEFIT_ANALYSIS.get("fallback_benefits", {})
        if not enhanced.get('primary_benefit') or enhanced.get('primary_benefit') == 'general health support':
            for fallback_category, fallback_benefits_list in fallback_benefits.items():
                if any(keyword in sku_lower for keyword in fallback_benefits_list):
                    enhanced['primary_benefit'] = fallback_benefits_list[0]
                    enhanced['fallback_benefits'] = fallback_benefits_list
                    break
        
        return enhanced
    
    def _cleanup_old_checkpoints(self, checkpoint_dir: str, input_file: str, mode: str):
        """Clean up old checkpoints based on config settings"""
        try:
            max_checkpoints = CHECKPOINT_SETTINGS.get("max_checkpoints", 10)
            if max_checkpoints <= 0:
                return
            
            # Get all checkpoint files for this input file and mode
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            pattern = f"{checkpoint_dir}/{base_name}_{mode}_*.json"
            checkpoint_files = glob.glob(pattern)
            
            # Sort by modification time (newest first)
            checkpoint_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            # Remove old checkpoints beyond the limit
            if len(checkpoint_files) > max_checkpoints:
                for old_file in checkpoint_files[max_checkpoints:]:
                    try:
                        os.remove(old_file)
                        print(f"🗑️ Cleaned up old checkpoint: {os.path.basename(old_file)}")
                    except Exception as e:
                        print(f"⚠️ Could not remove old checkpoint {old_file}: {e}")
                        
        except Exception as e:
            print(f"⚠️ Error during checkpoint cleanup: {e}")
    
    def process_file(self, input_file: str, mode: str = "comprehensive") -> List[Dict]:
        """Process input file and generate reviews based on new requirements"""
        try:
            # Reset review tracking and usernames for new file
            self.review_generator.generated_reviews.clear()
            self.name_generator.reset_used_usernames()
            
            # Read input file - handle both actual format and extension
            try:
                if input_file.endswith('.xlsx'):
                    # Try Excel first, fallback to CSV if it's actually CSV
                    try:
                        df = pd.read_excel(input_file, engine='openpyxl')
                        print(f"📊 Read as Excel file: {input_file}")
                    except Exception as excel_error:
                        # If Excel fails, try as CSV (common when .xlsx files are actually CSV)
                        try:
                            df = pd.read_csv(input_file)
                            print(f"📊 Read as CSV file (with .xlsx extension): {input_file}")
                        except Exception as csv_error:
                            raise ValueError(f"File cannot be read as Excel or CSV: {excel_error}")
                elif input_file.endswith('.xls'):
                    df = pd.read_excel(input_file, engine='xlrd')
                    print(f"📊 Read as Excel file: {input_file}")
                elif input_file.endswith('.csv'):
                    df = pd.read_csv(input_file)
                    print(f"📊 Read as CSV file: {input_file}")
                else:
                    raise ValueError(f"Unsupported file format: {input_file}")
            except Exception as e:
                raise ValueError(f"Error reading file {input_file}: {e}")
            
            columns = list(df.columns)
            required_columns = [
                "sku_id", "Name", "brand", "product_discount_category",
                "Classifier 1", "classifier 2", "classifier 3"
            ]
            
            # Validate columns
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            print(f"📊 Read {df.shape[1]} file: {input_file}")
            print(f"   Columns: {columns}")
            print(f"   Rows: {len(df):,}")
            print(f"✅ All required columns found!")
            
            # Filter for FMCG only (new requirement)
            if QUANTITY_RULES.get("fmcg_only", True):
                # Filter out Pharma and PL SKUs
                df = df[df['product_discount_category'] == 'FMCG']
                print(f"🔍 Filtered to FMCG SKUs only: {len(df):,} rows")
            
            # Determine review count based on new rules
            reviews_per_sku = random.randint(
                QUANTITY_RULES.get("reviews_per_sku", {}).get("min", 17),
                QUANTITY_RULES.get("reviews_per_sku", {}).get("max", 22)
            )
            
            results = []
            total_skus = len(df)
            
            for idx, row in df.iterrows():
                # Extract product information
                sku_id = row['sku_id']
                product_name = row['Name']
                brand = row['brand']
                classifier_1 = row['Classifier 1']
                classifier_2 = row['classifier 2']
                classifier_3 = row['classifier 3']
                
                # Create SKU name
                sku_name = f"{brand} - {product_name}"
                
                print(f"\n🔄 Generating reviews for: {sku_name}")
                print(f"   Category: {classifier_1} > {classifier_2} > {classifier_3}")
                print(f"   Generating {reviews_per_sku} reviews...")
                
                # Analyze product benefits using config
                product_benefits = self.benefit_analyzer.analyze_product_benefits(
                    sku_name, brand, classifier_1, classifier_2, classifier_3
                )
                
                # Enhance benefits using PRODUCT_CLASSIFICATIONS and PRODUCT_KEYWORDS
                enhanced_benefits = self._enhance_benefits_with_config(
                    product_benefits, sku_name, classifier_1, classifier_2, classifier_3
                )
                
                # Generate reviews for this SKU
                for review_num in range(reviews_per_sku):
                    # Generate review content using enhanced benefits
                    review = self.review_generator.generate_review(
                        sku_name, sku_id, brand, classifier_1, classifier_2, 
                        classifier_3, None, enhanced_benefits
                    )
                    
                    # Generate supporting data with new rules
                    username = self.name_generator.generate_username()
                    rating = self.review_generator.generate_rating()
                    date = self.review_generator.generate_date()
                    
                    # Create result row with new output format
                    result_row = {
                        'sku_id': sku_id,
                        'sku_name': sku_name,
                        'rating': rating,
                        'review': review,
                        'post_date': date,
                        'username': username
                    }
                    
                    results.append(result_row)
                    
                    # Show progress
                    if (review_num + 1) % 5 == 0:
                        print(f"     Progress: {review_num + 1}/{reviews_per_sku}")
                
                print(f"   ✅ Completed {reviews_per_sku} reviews for {sku_name}")
                
                # Save checkpoint every save_interval reviews
                if len(results) % self.checkpoint_manager.save_interval == 0:
                    self.checkpoint_manager.save_checkpoint(
                        results, input_file, mode, len(results) // self.checkpoint_manager.save_interval
                    )
                
                # Add delay to avoid rate limiting
                time.sleep(0.5)
            
            # Final checkpoint
            self.checkpoint_manager.save_checkpoint(results, input_file, mode, "final")
            
            print(f"\n✅ Generated {len(results)} total reviews.")
            return results
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            raise
    
    def process_file_quick(self, input_file: str) -> List[Dict]:
        """Process file in quick mode (1 review per SKU)"""
        return self.process_file(input_file, "quick")
    
    def process_file_medium(self, input_file: str) -> List[Dict]:
        """Process file in medium mode (3-5 reviews per SKU)"""
        return self.process_file(input_file, "medium")
    
    def process_file_comprehensive(self, input_file: str) -> List[Dict]:
        """Process file in comprehensive mode (15-20 reviews per SKU)"""
        return self.process_file(input_file, "comprehensive")
    
    def generate_sample_excel(self, output_file: str = "sample_skus.xlsx"):
        """Generate a sample Excel file with the required structure"""
        sample_data = [
            {
                "sku_id": "CER0576", "Name": "CeraVe Moisturizing Cream", "brand": "CeraVe", 
                "product_discount_category": "FMCG", "Classifier 1": "PERSONAL CARE", 
                "classifier 2": "SKIN CARE", "classifier 3": "BODY CARE"
            },
            {
                "sku_id": "NEU0830", "Name": "Neurobion Forte Tablet", "brand": "Neurobion", 
                "product_discount_category": "FMCG", "Classifier 1": "NUTRITION & METABOLISM", 
                "classifier 2": "VITAMINS AND MINERALS", "classifier 3": "VITAMINS AND MINERALS"
            },
            {
                "sku_id": "EVI0105", "Name": "Evion 400mg Capsule", "brand": "Evion", 
                "product_discount_category": "FMCG", "Classifier 1": "NUTRITION & METABOLISM", 
                "classifier 2": "VITAMINS AND MINERALS", "classifier 3": "VITAMINS AND MINERALS"
            }
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ Sample file created: {output_file}")
        return output_file
    
    def write_results(self, results: List[Dict], output_file: str):
        """Write results to CSV file with new tab-separated format"""
        if not results:
            print("⚠️ No results to write")
            return
        
        # Use new output format columns
        fieldnames = OUTPUT_FORMAT.get("columns", [
            'sku_id', 'sku_name', 'rating', 'review', 'post_date', 'username'
        ])
        
        # Use tab separator as specified in config
        separator = OUTPUT_FORMAT.get("separator", "\t")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            if separator == "\t":
                # Write tab-separated format
                writer = csv.writer(csvfile, delimiter='\t')
                # Write header
                writer.writerow(fieldnames)
                # Write data rows
                for result in results:
                    row = [result.get(field, '') for field in fieldnames]
                    writer.writerow(row)
            else:
                # Write CSV format
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        print(f"✅ Results saved to: {output_file}")
        print(f"📊 Format: Tab-separated with columns: {', '.join(fieldnames)}")
    
    def get_checkpoint_status(self, input_file: str, mode: str):
        """Get checkpoint status for a file"""
        return self.checkpoint_manager.show_checkpoint_status(input_file, mode)
    
    def load_checkpoint(self, input_file: str, mode: str) -> Tuple[List[Dict], int]:
        """Load checkpoint for resuming"""
        return self.checkpoint_manager.load_checkpoint(input_file, mode)


def check_openai_version():
    """Check OpenAI library version and provide troubleshooting tips"""
    try:
        import openai
        # Check if the library has the OpenAI class
        if hasattr(openai, 'OpenAI'):
            print("✅ OpenAI library version is compatible")
            return True
        else:
            print("❌ Error: OpenAI library version is incompatible")
            print("   This usually means you have an old version of the 'openai' library")
            print("   Please run: pip install openai>=1.0.0")
            return False
    except ImportError:
        print("❌ Error: OpenAI library not found")
        print("   Please install it with: pip install openai>=1.0.0")
        return False


def main():
    """Main CLI function with updated requirements"""
    print("=== SKU Review Generator (Updated for New Requirements) ===")
    
    # Check OpenAI library version
    if not check_openai_version():
        print("\n🔧 Quick Fix:")
        print("   Run: pip install openai>=1.0.0")
        return
    
    try:
        # Initialize the generator
        generator = ReviewGenerator()
        
        # Get input file
        print("\n" + "="*50)
        input_file = input("Enter the path to your Excel/CSV file (or press Enter to create a sample): ").strip()
        
        if not input_file:
            # Generate sample file
            sample_file = generator.generate_sample_excel()
            input_file = sample_file
            print(f"📁 Using sample file: {sample_file}")
        
        # Check if file exists
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            return
        
        # Display new requirements
        print("\n🎯 New Generation Rules:")
        print(f"   • Reviews per SKU: {QUANTITY_RULES.get('reviews_per_sku', {}).get('min', 17)}-{QUANTITY_RULES.get('reviews_per_sku', {}).get('max', 22)}")
        print(f"   • Language Mix: {LANGUAGE_MIXING.get('distribution', {}).get('Pure English', 60)}% English, {LANGUAGE_MIXING.get('distribution', {}).get('Hinglish', 30)}% Hinglish, {LANGUAGE_MIXING.get('distribution', {}).get('Hindi Casual', 10)}% Hindi")
        print(f"   • Rating Distribution: {RATING_DISTRIBUTION.get('5_star', 50)}% 5★, {RATING_DISTRIBUTION.get('4_star', 25)}% 4★, {RATING_DISTRIBUTION.get('3_star', 20)}% 3★, {RATING_DISTRIBUTION.get('2_star', 5)}% 2★")
        print(f"   • Date Range: {DATE_RULES.get('start_date', '2025-09-01')} to {DATE_RULES.get('end_date', '2025-12-31')}")
        print(f"   • FMCG Only: {QUANTITY_RULES.get('fmcg_only', True)}")
        
        # Check for existing checkpoints
        print("\n🔍 Checking for existing checkpoints...")
        generator.get_checkpoint_status(input_file, "new_rules")
        existing_results, previous_count = generator.load_checkpoint(input_file, "new_rules")
        
        if existing_results and previous_count > 0:
            resume_choice = input(f"Found checkpoint with {previous_count} reviews. Resume from checkpoint? (y/n, default: y): ").strip().lower()
            if resume_choice in ['', 'y', 'yes']:
                print(f"🔄 Resuming from checkpoint with {previous_count} existing reviews...")
                results = existing_results
            else:
                print("🔄 Starting fresh...")
                results = []
        else:
            results = []
        
        # Process file with new rules
        if not results:  # Only process if not resuming
            print(f"\n🚀 Processing {input_file} with new requirements...")
            results = generator.process_file(input_file, "new_rules")
        
        # Write results
        if results:
            output_file = f"{os.path.splitext(input_file)[0]}_new_rules_reviews.csv"
            generator.write_results(results, output_file)
            
            print(f"\n🎉 Review generation completed successfully!")
            print(f"📁 Total reviews generated: {len(results)}")
            print(f"💾 Results saved to: {output_file}")
            print(f"🚀 You can now use these reviews for your products!")
            
            # Show sample results
            print("\nSample results:")
            for i, result in enumerate(results[:3], 1):
                try:
                    print(f"{i}. {result.get('sku_name', 'N/A')}")
                    print(f"   SKU ID: {result.get('sku_id', 'N/A')}")
                    print(f"   Review: {result.get('review', 'N/A')}")
                    print(f"   Username: {result.get('username', 'N/A')}")
                    print(f"   Rating: {result.get('rating', 'N/A')}")
                    print(f"   Date: {result.get('post_date', 'N/A')}")
                    print()
                except Exception as e:
                    print(f"   Error displaying result {i}: {e}")
        
        print("="*50)
        print("✅ Program completed successfully!")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        print("💾 Checkpoint data has been saved - you can resume later!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Check the configuration and try again")


if __name__ == "__main__":
    main() 