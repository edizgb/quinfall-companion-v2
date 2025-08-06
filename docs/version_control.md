# Version Control System Documentation

## Overview
The version control system tracks changes to recipes and notifies users when updates are available.

## Key Components

### Recipe Comparison
- `compare_materials()`: Detects material changes
- `compare_output_stats()`: Tracks stat modifications
- `compare_profession_reqs()`: Validates profession requirements

### Notification System
- `RecipeUpdateNotifier`: Displays update alerts
- Integrated with CraftingTab for automatic checks

### Version Tracking
- Maintains current versions of all recipes
- Automatically checks for updates when recipes are accessed

## Usage Examples

### Checking for Updates
```python
# In CraftingTab implementation
def check_for_updates(self, recipe):
    current_version = self.current_versions.get(recipe.name)
    if current_version and recipe.version != current_version:
        changes = compare_recipes(recipe, self.get_latest_recipe(recipe.name))
        if changes:
            self.notifier.show_update_alert(changes)
    self.current_versions[recipe.name] = recipe.version
```

### Notification Flow
1. Recipe is loaded
2. Version compared against stored version
3. If changed, differences are calculated
4. User notified of specific changes
