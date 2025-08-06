"""
Quinfall Icon Manager - Download and cache authentic Quinfall icons from Fandom Wiki
"""
import os
import requests
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple
import json
from urllib.parse import urlparse
from dataclasses import dataclass
import time
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

@dataclass
class QuinfallIcon:
    """Represents a Quinfall icon with metadata"""
    name: str
    url: str
    local_path: str
    category: str
    rarity: str = "common"
    cached_at: float = 0.0
    file_size: int = 0

class QuinfallIconManager:
    """Manages downloading, caching, and serving Quinfall icons"""
    
    def __init__(self, cache_dir: str = "data/icons"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "icon_metadata.json"
        self.icons: Dict[str, QuinfallIcon] = {}
        self.load_metadata()
        
        # Known Quinfall icon URLs from Fandom Wiki
        self.known_icons = {
            # Material icons from Quinfall Wiki (Fandom)
            "iron_ore": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/6/61/Ironore.png/revision/latest?cb=20250622232916",
            "wood": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/d/df/Wood.png/revision/latest?cb=20250717035755",
            "leather_log": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/1/12/Leather_Log.png/revision/latest?cb=20250717040247",
            "resinous_hardwood": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/5/55/Resinous_hardwood.png/revision/latest?cb=20250717035917",
            
            # Tool icons from Quinfall Wiki (Fandom)
            "axe": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/b/b1/Axeeg.png/revision/latest?cb=20250702222658",
            "simple_axe": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/b/b1/Axeeg.png/revision/latest?cb=20250702222658",
            "solid_axe": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/b/b1/Axeeg.png/revision/latest?cb=20250702222658",
            "advanced_axe": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/b/b1/Axeeg.png/revision/latest?cb=20250702222658",
            
            # Other materials (placeholder - need to find actual URLs)
            "copper_ore": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/placeholder/copper.png",
            "coal": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/placeholder/coal.png",
            "bronze_ingot": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/placeholder/bronze.png",
            "steel_ingot": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/placeholder/steel.png",
            "mithril_ingot": "https://static.wikia.nocookie.net/the-unofficial-quinfall/images/placeholder/mithril.png",
            
            # Profession icons
            "blacksmithing": "⚒️",
            "armorsmithing": "🛡️",
            "weaponsmithing": "⚔️",
            "woodcutting": "🪓",
            "mining": "⛏️",
            "cooking": "🍳",
            "alchemy": "⚗️",
            "tailoring": "🧵",
            "engineering": "⚙️"
        }
    
    def load_metadata(self):
        """Load icon metadata from cache"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, icon_data in data.items():
                        self.icons[name] = QuinfallIcon(**icon_data)
            except Exception as e:
                logger.warning(f"Could not load icon metadata: {e}")
    
    def save_metadata(self):
        """Save icon metadata to cache"""
        try:
            data = {}
            for name, icon in self.icons.items():
                data[name] = {
                    'name': icon.name,
                    'url': icon.url,
                    'local_path': icon.local_path,
                    'category': icon.category,
                    'rarity': icon.rarity,
                    'cached_at': icon.cached_at,
                    'file_size': icon.file_size
                }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save icon metadata: {e}")
    
    def get_icon_path(self, material_name: str) -> Optional[str]:
        """Get local path for material icon, download if needed"""
        # Normalize material name
        normalized_name = material_name.lower().replace(' ', '_').replace('-', '_')
        
        # Check if we have this icon cached
        if normalized_name in self.icons:
            icon = self.icons[normalized_name]
            if os.path.exists(icon.local_path):
                return icon.local_path
        
        # Try to download icon if we have URL
        if normalized_name in self.known_icons:
            url = self.known_icons[normalized_name]
            if url.startswith('http'):
                return self.download_icon(normalized_name, url)
        
        # Return emoji fallback for professions
        if normalized_name in self.known_icons:
            return self.known_icons[normalized_name]
        
        return None
    
    def download_icon(self, name: str, url: str) -> Optional[str]:
        """Download icon from URL and cache locally"""
        try:
            # Generate local filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            ext = os.path.splitext(urlparse(url).path)[1] or '.png'
            local_filename = f"{name}_{url_hash}{ext}"
            local_path = self.cache_dir / local_filename
            
            # Download if not exists
            if not local_path.exists():
                logger.info(f"Downloading icon: {name} from {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)
            
            # Update metadata
            self.icons[name] = QuinfallIcon(
                name=name,
                url=url,
                local_path=str(local_path),
                category="material",
                cached_at=time.time(),
                file_size=local_path.stat().st_size if local_path.exists() else 0
            )
            self.save_metadata()
            
            return str(local_path)
            
        except Exception as e:
            logger.warning(f"Could not download icon {name}: {e}")
            return None
    
    def get_material_icon_html(self, material_name: str, size: int = 24) -> str:
        """Get HTML for material icon (image or emoji fallback)"""
        icon_path = self.get_icon_path(material_name)
        
        if icon_path and os.path.exists(icon_path):
            # Return image HTML
            return f'<img src="file:///{icon_path.replace(os.sep, "/")}" width="{size}" height="{size}" style="vertical-align: middle; margin-right: 4px;" />'
        elif icon_path and not icon_path.startswith('http'):
            # Return emoji
            return f'<span style="font-size: {size-4}px; margin-right: 4px; vertical-align: middle;">{icon_path}</span>'
        else:
            # Return generic fallback
            return f'<span style="font-size: {size-4}px; margin-right: 4px; vertical-align: middle;">📦</span>'
    
    def get_profession_icon(self, profession: str) -> str:
        """Get emoji icon for profession"""
        normalized = profession.lower().replace(' ', '').replace('-', '')
        return self.known_icons.get(normalized, '🔨')
    
    def get_rarity_color(self, rarity: str) -> str:
        """Get color for item rarity"""
        rarity_colors = {
            'common': '#9ca3af',
            'uncommon': '#10b981',
            'rare': '#3b82f6', 
            'epic': '#8b5cf6',
            'legendary': '#f59e0b',
            'artifact': '#ef4444'
        }
        return rarity_colors.get(rarity.lower(), '#9ca3af')
    
    def extract_icons_from_fandom(self, page_url: str) -> Dict[str, str]:
        """Extract icon URLs from Fandom Wiki page (placeholder for future implementation)"""
        # This would parse the page and extract image URLs
        # For now, return empty dict
        return {}
    
    def scrape_wiki_icons(self, wiki_url: str) -> Dict[str, str]:
        """
        Scrape icons from Quinfall Wiki pages automatically.
        
        Args:
            wiki_url: URL of the wiki page to scrape
            
        Returns:
            Dictionary mapping material names to icon URLs
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(wiki_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            found_icons = {}
            
            # Look for images with Quinfall Wiki URLs
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '').lower()
                
                # Check if it's a Quinfall Wiki icon
                if 'static.wikia.nocookie.net/the-unofficial-quinfall' in src:
                    # Extract material name from alt text or filename
                    if alt:
                        material_key = alt.replace(' ', '_').lower()
                        # Clean up the URL to get the full resolution version
                        clean_url = self._clean_wiki_url(src)
                        found_icons[material_key] = clean_url
                        logger.debug(f"Found icon: {alt} -> {clean_url}")
            
            return found_icons
            
        except Exception as e:
            logger.error(f"Error scraping wiki icons from {wiki_url}: {e}")
            return {}
    
    def _clean_wiki_url(self, url: str) -> str:
        """
        Clean up Fandom Wiki URLs to get full resolution images.
        Removes scale-down parameters and gets the latest revision.
        """
        # Remove scale-down parameters
        if '/scale-to-width-down/' in url:
            # Extract the base URL before scale parameters
            base_url = url.split('/scale-to-width-down/')[0]
            # Add revision/latest for full resolution
            if '/revision/latest' not in base_url:
                base_url += '/revision/latest'
            return base_url
        
        # Ensure we have revision/latest for consistency
        if '/revision/latest' not in url:
            url = url.split('?')[0] + '/revision/latest'
            
        return url
    
    def auto_discover_icons(self):
        """
        Automatically discover new icons from key Quinfall Wiki pages.
        """
        wiki_pages = [
            'https://the-unofficial-quinfall.fandom.com/wiki/Gathering',
            'https://the-unofficial-quinfall.fandom.com/wiki/Woodcutting', 
            'https://the-unofficial-quinfall.fandom.com/wiki/Category:Materials',
            'https://the-unofficial-quinfall.fandom.com/wiki/Category:Items',
            'https://the-unofficial-quinfall.fandom.com/wiki/Mining',
            'https://the-unofficial-quinfall.fandom.com/wiki/Fishing',
            'https://the-unofficial-quinfall.fandom.com/wiki/Hunting'
        ]
        
        logger.info("🔍 Auto-discovering icons from Quinfall Wiki...")
        new_icons = {}
        
        for page_url in wiki_pages:
            logger.info(f"Scraping: {page_url}")
            page_icons = self.scrape_wiki_icons(page_url)
            new_icons.update(page_icons)
            time.sleep(1)  # Be respectful to the server
        
        # Update known icons with new discoveries
        self.known_icons.update(new_icons)
        
        logger.info(f"✅ Discovered {len(new_icons)} new icons!")
        for name, url in new_icons.items():
            logger.info(f"  • {name}: {url}")
        
        return new_icons
    
    def cleanup_old_cache(self, max_age_days: int = 30):
        """Remove old cached icons"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        for name, icon in list(self.icons.items()):
            if icon.cached_at < cutoff_time:
                try:
                    if os.path.exists(icon.local_path):
                        os.remove(icon.local_path)
                    del self.icons[name]
                except Exception as e:
                    logger.warning(f"Could not remove old icon {name}: {e}")
        
        self.save_metadata()

# Global instance
icon_manager = QuinfallIconManager()
