# Safe Development Workflow

1. Create test copy:
```python
from tests.test_utils import create_test_copy
test_file = create_test_copy("ui/crafting_tab.py")
```

2. Make changes to test file
3. Run tests
4. Update original only if tests pass:
```python
update_original_if_passed(test_file, "ui/crafting_tab.py")
```
