"""
TSV recipe validation utilities
"""
import csv
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_tsv_materials(tsv_path):
    """Load material names from TSV file"""
    materials = set()
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            materials.add(row['Material'].strip().lower())
    return materials

def validate_materials(recipe, material_ref):
    """Validate recipe materials against reference list"""
    issues = []
    for material in recipe.get('materials', {}):
        if material.lower() not in material_ref:
            issues.append(f"Unknown material: {material}")
    return issues

def validate_recipe_materials(recipe, tsv_materials):
    """Check recipe materials against TSV reference"""
    issues = []
    for material in recipe.get('materials', {}):
        if material.lower() not in tsv_materials:
            issues.append(f"Unknown material: {material}")
    return issues

def validate_recipes(recipe_file, tsv_file=None, material_ref=None):
    """Validate all recipes against reference(s)"""
    tsv_materials = set()
    if tsv_file:
        tsv_materials = load_tsv_materials(tsv_file)
    
    if material_ref:
        with open(material_ref, 'r') as f:
            ref_materials = set(json.load(f)['materials'])
        tsv_materials.update(ref_materials)
    
    with open(recipe_file, 'r') as f:
        recipes = json.load(f)['recipes']
    
    report = {
        'valid': 0,
        'issues': [],
        'total': len(recipes)
    }
    
    for recipe in recipes:
        issues = validate_recipe_materials(recipe, tsv_materials)
        if not issues:
            report['valid'] += 1
        else:
            report['issues'].append({
                'recipe': recipe['recipe_name'],
                'issues': issues
            })
    
    return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate recipes against material references')
    parser.add_argument('--recipes', required=True, help='Path to recipes JSON file')
    parser.add_argument('--tsv', help='Path to reference TSV file')
    parser.add_argument('--material_ref', help='Path to material reference JSON file')
    args = parser.parse_args()
    
    report = validate_recipes(args.recipes, args.tsv, args.material_ref)
    
    logger.info(f"Validation complete. {report['valid']}/{report['total']} recipes valid")
    if report['issues']:
        logger.warning("\nIssues found:")
        for issue in report['issues']:
            logger.info(f"\nRecipe: {issue['recipe']}")
            for detail in issue['issues']:
                logger.info(f"- {detail}")

if __name__ == "__main__":
    main()
