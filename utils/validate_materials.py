import json
from pathlib import Path
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_project_root():
    """Get the absolute path to project root"""
    return Path(__file__).parent.parent

def load_material_references():
    """Load the material reference list"""
    ref_path = get_project_root() / 'data' / 'material_reference.json'
    logger.info(f"Looking for material reference at: {ref_path}")
    
    try:
        if not ref_path.exists():
            raise FileNotFoundError(f"Material reference file not found at {ref_path}")
            
        with open(ref_path) as f:
            data = json.load(f)
            
        if not isinstance(data, dict) or "materials" not in data:
            raise ValueError("Invalid material reference format - missing 'materials' key")
            
        if not isinstance(data["materials"], list):
            raise ValueError("Materials must be a list")
            
        return set(data["materials"])
        
    except Exception as e:
        logger.error(f"Error loading material reference: {str(e)}")
        return None

def validate_recipe_materials(recipe_path, reference_materials):
    """Validate all materials in recipes against reference list"""
    logger.info(f"Validating recipes at: {recipe_path}")
    
    try:
        with open(recipe_path) as f:
            data = json.load(f)
            
        if not isinstance(data, dict) or "recipes" not in data:
            raise ValueError("Invalid recipe format - missing 'recipes' key")
            
        recipes = data["recipes"]
        discrepancies = []
        
        for recipe in recipes:
            if not isinstance(recipe, dict) or "materials" not in recipe:
                continue
                
            for material in recipe["materials"]:
                if material not in reference_materials:
                    discrepancies.append({
                        'recipe': recipe.get('recipe_name', 'unknown'),
                        'material': material,
                        'status': 'missing'
                    })
        
        return discrepancies
        
    except Exception as e:
        logger.error(f"Error validating recipes: {str(e)}")
        return None

if __name__ == '__main__':
    project_root = get_project_root()
    sys.path.append(str(project_root))
    
    reference_materials = load_material_references()
    if reference_materials is None:
        sys.exit(1)
        
    recipe_path = project_root / 'data' / 'recipes_blacksmithing.json'
    discrepancies = validate_recipe_materials(recipe_path, reference_materials)
    
    if discrepancies is None:
        sys.exit(1)
        
    if discrepancies:
        logger.warning(f"Found {len(discrepancies)} material discrepancies:")
        for issue in discrepancies:
            logger.warning(f"{issue['recipe']}: {issue['material']} ({issue['status']})")
        sys.exit(1)
    else:
        logger.info("All materials validated successfully")
        sys.exit(0)
