import requests
from bs4 import BeautifulSoup
import json
import logging
import time
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_fandom():
    """
    Enhanced Fandom scraping with better error handling and Quinfall-specific parsing
    """
    try:
        base_url = "https://the-quinfall.fandom.com/wiki/Category:Recipes"
        logger.info(f"🔍 Starting Fandom scraping from: {base_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            recipes = []
            
            # Try multiple selectors for recipe links
            recipe_links = []
            selectors = [
                'a.category-page__member-link',
                'a[title*="Recipe:"]',
                '.category-page__member a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    recipe_links = links
                    logger.info(f"✅ Found {len(recipe_links)} recipe links using selector: {selector}")
                    break
            
            if not recipe_links:
                logger.warning("⚠️ No recipe links found with any selector")
                return []
            
            # Process recipes with rate limiting
            for i, link in enumerate(recipe_links[:10]):  # Limit for testing
                try:
                    recipe_name = link.text.strip()
                    if 'Recipe:' in recipe_name:
                        recipe_name = recipe_name.replace('Recipe:', '').strip()
                    
                    recipe_url = link.get('href', '')
                    if recipe_url.startswith('/'):
                        recipe_url = 'https://the-quinfall.fandom.com' + recipe_url
                    
                    logger.info(f"📋 Processing recipe {i+1}/{min(len(recipe_links), 10)}: {recipe_name}")
                    
                    # Rate limiting to be respectful
                    if i > 0:
                        time.sleep(1)
                    
                    recipe_data = scrape_recipe_page(recipe_url, recipe_name, headers)
                    if recipe_data:
                        recipes.append(recipe_data)
                        logger.info(f"✅ Successfully scraped: {recipe_name}")
                    else:
                        logger.warning(f"⚠️ Failed to scrape: {recipe_name}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing recipe link: {e}")
                    continue
            
            logger.info(f"🎉 Successfully scraped {len(recipes)} recipes from Fandom")
            return recipes
        else:
            logger.error(f"❌ Failed to access Fandom: HTTP {response.status_code}")
            return []
            
    except requests.RequestException as e:
        logger.error(f"❌ Network error during Fandom scraping: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error during Fandom scraping: {e}")
        return []

def scrape_recipe_page(url: str, name: str, headers: Dict) -> Optional[Dict]:
    """
    Scrape individual recipe page with Quinfall-specific parsing
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse materials with multiple strategies
        materials = parse_recipe_materials(soup, name)
        
        # Parse profession/skill requirements
        profession, skill_level = parse_profession_requirements(soup)
        
        # Parse output information
        output_info = parse_output_info(soup)
        
        recipe_data = {
            'name': name,
            'materials': materials,
            'profession': profession,
            'skill_level': skill_level,
            'output': output_info,
            'source': 'Fandom',
            'url': url,
            'scraped_at': time.time()
        }
        
        return recipe_data
        
    except Exception as e:
        logger.error(f"❌ Error scraping recipe page {url}: {e}")
        return None

def parse_recipe_materials(soup: BeautifulSoup, recipe_name: str) -> List[Dict]:
    """
    Parse materials from recipe page using multiple strategies
    """
    materials = []
    
    # Strategy 1: Look for materials in tables
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                material_name = cells[0].get_text(strip=True)
                quantity_text = cells[1].get_text(strip=True)
                
                # Extract quantity number
                quantity = extract_quantity(quantity_text)
                if quantity and material_name:
                    materials.append({
                        'name': material_name,
                        'quantity': quantity
                    })
    
    # Strategy 2: Look for materials in lists
    if not materials:
        material_lists = soup.find_all(['ul', 'ol'])
        for ul in material_lists:
            items = ul.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if text and any(keyword in text.lower() for keyword in ['x', 'quantity', 'amount']):
                    parsed = parse_material_text(text)
                    if parsed:
                        materials.append(parsed)
    
    # Strategy 3: Look for specific Quinfall material patterns
    if not materials:
        text_content = soup.get_text()
        materials = extract_materials_from_text(text_content)
    
    logger.debug(f"🔍 Found {len(materials)} materials for {recipe_name}: {materials}")
    return materials

def parse_profession_requirements(soup: BeautifulSoup) -> tuple:
    """
    Parse profession and skill level requirements
    """
    profession = "Unknown"
    skill_level = 1
    
    # Look for profession information
    text_content = soup.get_text().lower()
    
    quinfall_professions = [
        'blacksmithing', 'armorsmithing', 'weaponsmithing', 
        'alchemy', 'cooking', 'woodworking', 'tailoring', 
        'engineering', 'jewelcrafting', 'enchanting'
    ]
    
    for prof in quinfall_professions:
        if prof in text_content:
            profession = prof.title()
            break
    
    # Look for skill level
    import re
    skill_matches = re.findall(r'level\s*(\d+)|skill\s*(\d+)|requires?\s*(\d+)', text_content)
    if skill_matches:
        for match in skill_matches:
            for group in match:
                if group and group.isdigit():
                    skill_level = int(group)
                    break
            if skill_level > 1:
                break
    
    return profession, skill_level

def parse_output_info(soup: BeautifulSoup) -> Dict:
    """
    Parse output information (item name, quantity, stats)
    """
    output_info = {
        'name': 'Unknown',
        'quantity': 1,
        'stats': {}
    }
    
    # This would need to be enhanced based on actual Fandom page structure
    # For now, return basic structure
    return output_info

def extract_quantity(text: str) -> Optional[int]:
    """
    Extract quantity number from text
    """
    import re
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return None

def parse_material_text(text: str) -> Optional[Dict]:
    """
    Parse material from text like "5x Iron Ore" or "Iron Ore (5)"
    """
    import re
    
    # Pattern: "5x Iron Ore" or "5 Iron Ore"
    match = re.match(r'(\d+)\s*x?\s*(.+)', text)
    if match:
        return {
            'name': match.group(2).strip(),
            'quantity': int(match.group(1))
        }
    
    # Pattern: "Iron Ore (5)" or "Iron Ore - 5"
    match = re.match(r'(.+?)\s*[\(\-]\s*(\d+)', text)
    if match:
        return {
            'name': match.group(1).strip(),
            'quantity': int(match.group(2))
        }
    
    return None

def extract_materials_from_text(text: str) -> List[Dict]:
    """
    Extract materials from free text using Quinfall-specific patterns
    """
    materials = []
    
    # This would need enhancement based on actual Quinfall material names
    # For now, return empty list
    return materials

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    if args.source == "fandom":
        recipes = scrape_fandom()
        with open(args.output, 'w') as f:
            json.dump(recipes, f, indent=2)
