"""
Recipe comparison utilities for Quinfall Companion App
"""

def compare_materials(old_mat, new_mat):
    """Compare material dictionaries between recipe versions"""
    changes = {}
    all_materials = set(old_mat.keys()).union(set(new_mat.keys()))
    
    for material in all_materials:
        if material not in old_mat:
            changes[material] = {"action": "added", "quantity": new_mat[material]}
        elif material not in new_mat:
            changes[material] = {"action": "removed", "quantity": old_mat[material]}
        elif old_mat[material] != new_mat[material]:
            changes[material] = {
                "action": "quantity_changed",
                "old": old_mat[material],
                "new": new_mat[material]
            }
    
    return changes

def compare_output_stats(old_stats, new_stats):
    """Compare output stat dictionaries between recipe versions"""
    changes = {}
    all_stats = set(old_stats.keys()).union(set(new_stats.keys()))
    
    for stat in all_stats:
        if stat not in old_stats:
            changes[stat] = {"action": "added", "value": new_stats[stat]}
        elif stat not in new_stats:
            changes[stat] = {"action": "removed", "value": old_stats[stat]}
        elif old_stats[stat] != new_stats[stat]:
            changes[stat] = {
                "action": "value_changed",
                "old": old_stats[stat],
                "new": new_stats[stat]
            }
    
    return changes

def compare_profession_reqs(old_req, new_req):
    """Compare profession requirements between recipe versions"""
    changes = {}
    
    # Profession name validation
    if old_req.get('profession') != new_req.get('profession'):
        changes['profession'] = {
            "action": "changed",
            "old": old_req.get('profession'),
            "new": new_req.get('profession')
        }
    
    # Skill level changes
    if old_req.get('skill_level') != new_req.get('skill_level'):
        changes['skill_level'] = {
            "action": "changed",
            "old": old_req.get('skill_level'),
            "new": new_req.get('skill_level')
        }
    
    return changes

def compare_recipes(old_recipe, new_recipe):
    """Comprehensive recipe comparison combining all checks"""
    diff = {
        "materials": compare_materials(old_recipe.get('materials', {}), new_recipe.get('materials', {})),
        "output_stats": compare_output_stats(old_recipe.get('output_stats', {}), new_recipe.get('output_stats', {})),
        "profession": compare_profession_reqs(old_recipe, new_recipe)
    }
    
    # Only include sections with actual changes
    return {k: v for k, v in diff.items() if v}
