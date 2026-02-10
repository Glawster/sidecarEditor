# GitHub Copilot Instructions - Python/Qt Development Guidelines

## Overview

These are generic development guidelines for Python projects using Qt (PySide6) for GUI development. They establish consistent coding standards, naming conventions, and best practices that can be applied across multiple projects.

**Note**: For project-specific information, architecture details, and custom workflows, see `additional-copilot-instructions.md` in the `.github` directory.

## Development Standards

### Code Style & Quality
- **Formatting**: Use `black` for consistent code formatting
- **Linting**: Follow PEP 8 style guidelines
- **Testing**: pytest for comprehensive test coverage
- **Type hints**: Use type annotations where appropriate
- **Documentation**: Docstrings for all public functions and classes
- **Separation of Concerns**: Core business logic must have NO Qt dependencies (see additional-copilot-instructions.md for details)

### Naming Conventions
- **Classes**: PascalCase (e.g., `MainWindow`, `ImagePreview`, `DataProcessor`)
- **Functions and Variables**: snake_case (e.g., `process_data`, `calculate_total`, `load_config`)
- **Qt Signals**: camelCase (e.g., `imageSelected`, `sidecarSaved`)
- **Constants**: UPPERCASE_WITH_UNDERSCORES (e.g., `MAX_SIZE`, `DEFAULT_PATH`)
- **Private Members**: Leading underscore (e.g., `_internal_method`, `_private_var`)
- **Files**: camelCase for Python modules (e.g., `dataProcessor.py`, `fileUtils.py`)

### File Organization
- **UI Code**: Separate GUI components from business logic
- **Business Logic**: Core functionality independent of UI
- **Utilities**: Shared helper functions in dedicated modules
- **Tests**: Mirror source structure in test directory
- **Configuration**: Centralize constants and settings

## GUI Development Guidelines

### Framework Patterns
- Use Qt layouts (QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter)
- Use signals and slots for component communication
- Inherit from appropriate Qt widget classes
- Keep UI code separate from business logic
- Use status bars and progress indicators for user feedback
- Follow Qt's Model-View patterns where appropriate

### Component Standards
- **Buttons**: Use `QPushButton` or `QToolButton`
- **Labels**: Use `QLabel` for text and images
- **Text Input**: Use `QLineEdit` for single line, `QTextEdit` or `QPlainTextEdit` for multi-line
- **Lists**: Use `QListWidget` or `QListView` with models
- **Combos**: Use `QComboBox` for dropdown selections
- **Checks**: Use `QCheckBox` for boolean options
- **Radio**: Use `QRadioButton` for single-choice options
- **Containers**: Use `QWidget`, `QFrame`, `QGroupBox` for layout organization
- **Dialogs**: Use `QDialog`, `QMessageBox`, `QFileDialog` for user interaction
- **Menus**: Use `QMenuBar`, `QMenu`, `QAction` for application menus

### User Experience
- Provide progress feedback for long-running operations
- Use QMessageBox for error and info dialogs
- Use tooltips (setToolTip()) for complex UI elements
- Save and restore window geometry and state
- Follow platform-specific UI conventions (Qt handles this)
- Ensure keyboard navigation and shortcuts work properly
- Provide visual feedback for interactive elements
- Use status bars for non-intrusive notifications

## Qt-Specific Patterns

### Signals and Slots Communication
- Define custom signals using `Signal` from `PySide6.QtCore`
- Connect signals to slots using `.connect()`
- Emit signals to notify other components
- Disconnect signals when widgets are destroyed if needed

### Widget Initialization
- Call `super().__init__()` in widget constructors
- Set up UI in a separate `_setup_ui()` method
- Initialize member variables before UI setup
- Connect signals after UI is created

### Layout Management
- Always use layouts, never fixed positions
- Use spacers to control widget spacing
- Set size policies appropriately
- Use `setSizeConstraint()` for proper sizing

### Resource Management
- Clean up resources in `closeEvent()` or destructors
- Disconnect signals when appropriate
- Close file handles and network connections
- Clear large data structures when done

## Testing Requirements

### Test Structure
- Use pytest conventions (`test_*.py` files, `test_*` functions)
- Create focused, single-purpose test functions
- Use `tmp_path` fixture for temporary file/directory testing
- Mock external dependencies appropriately
- Organize tests to mirror source structure

### Test Categories
- **Unit Tests**: Test individual functions/methods in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **GUI Tests**: Test user interface behavior (where applicable)

### Coverage Expectations
- Core business logic: >90% coverage
- Critical functions: 100% coverage
- Error handling: All error paths tested
- Edge cases: Comprehensive boundary testing
- Happy path and failure scenarios both covered

### Test Best Practices
- Use descriptive test function names
- Follow Arrange-Act-Assert pattern
- Use `tmp_path` for file operations (automatic cleanup)
- Mock external services and expensive operations
- Provide descriptive error messages in assertions
- Test both success and failure scenarios
- Keep tests independent and repeatable
- Use parametrize for testing multiple inputs

## Error Handling & Logging

### How to use logUtils

### Logging Standards
- Use centralized logging configuration (from organiseMyProjects)
- Include module name and operation context
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Store logs with timestamp and rotation as appropriate

### Logging Guidelines
- **Message Format**: Keep messages lowercase and consistent
- **Major Actions**: `"doing something..."` - action being initiated
- **Action Completion**: `"...something done"` - action completed
- **General Updates**: `"...message"` - informational updates
- **Information Display**: `"...message: value"` - displaying data
- **Error Messages**: Use Sentence Case for ERROR level messages
- **Usage Example**: 
  ```python
  from src.logUtils import logger  # or appropriate import
  logger.info("...processing data")
  logger.error("Failed to process: error details")
  ```

### Error Recovery
- Implement graceful degradation for non-critical failures
- Provide user-actionable error messages
- Offer clear guidance when operations fail
- Handle missing dependencies gracefully
- Validate input before processing
- Use try-except blocks appropriately
- Log errors with sufficient context for debugging
- Maintain application stability during errors

## Code Examples

### GUI Component Example
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal

class MyWidget(QWidget):
    """Custom widget with signal example."""
    
    # Define custom signal
    processing_complete = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Action button
        self.action_button = QPushButton("Process")
        self.action_button.clicked.connect(self._on_action)
        layout.addWidget(self.action_button)
    
    def _on_action(self):
        """Handle button click."""
        self.status_label.setText("Processing...")
        # Do work here
        result = self._do_processing()
        self.status_label.setText("Complete")
        self.processing_complete.emit(result)
    
    def _do_processing(self) -> str:
        """Perform the actual processing."""
        return "result"
```

### Test Example
```python
import pytest
from pathlib import Path

def test_data_processing(tmp_path):
    """Test data processing with temporary files."""
    # Arrange
    test_file = tmp_path / "data.txt"
    test_file.write_text("test data")
    
    # Act
    result = process_file(str(test_file))
    
    # Assert
    assert result is not None
    assert result.success
    assert result.message == "processed successfully"

def test_qt_widget():
    """Test Qt widget creation."""
    # Import Qt here for test isolation
    from PySide6.QtWidgets import QApplication
    from myapp.widgets import MyWidget
    
    app = QApplication.instance() or QApplication([])
    widget = MyWidget()
    
    # Test widget state
    assert widget.status_label.text() == "Ready"
    
    # Simulate button click
    widget.action_button.click()
    assert widget.status_label.text() == "Complete"
```

### Logging Example
```python
import logging

logger = logging.getLogger(__name__)

def processData(data):
    """Process data with proper logging."""
    try:
        logger.info("...processing data")
        result = performOperation(data)
        logger.info("...data processed successfully")
        return result
    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

## Common Patterns to Follow

1. **Separation of Concerns**: Keep GUI, business logic, and data access separate
2. **Error Handling**: Use try-except blocks with proper logging
3. **User Feedback**: Provide clear status messages and progress indicators
4. **Resource Management**: Clean up resources properly (files, connections, etc.)
5. **Modular Design**: Create small, focused functions and classes
6. **Configuration Management**: Centralize settings and constants
7. **Testing**: Write tests for all new functionality
8. **Documentation**: Add docstrings to public functions and classes
9. **Type Hints**: Use type annotations for better code clarity
10. **DRY Principle**: Don't repeat yourself - extract common code

## Best Practices

### Code Quality
- Write self-documenting code with clear names
- Keep functions short and focused (single responsibility)
- Use meaningful variable and function names
- Comment only when necessary to explain "why", not "what"
- Follow PEP 8 style guidelines
- Use type hints for function signatures

### Performance
- Profile before optimizing
- Use appropriate data structures
- Avoid premature optimization
- Cache expensive computations when appropriate
- Use lazy loading for large datasets

### Security
- Validate all user input
- Never hardcode credentials
- Use secure storage for sensitive data
- Handle exceptions without leaking sensitive information
- Follow principle of least privilege

### Maintainability
- Keep dependencies minimal and well-documented
- Write tests that document expected behavior
- Use version control effectively
- Document breaking changes
- Consider backward compatibility