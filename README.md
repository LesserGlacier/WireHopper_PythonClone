# WireHopper Python Component - User Guide

## Installation

1. **Download** the `WireHopper_Python.py` file
2. **Open Grasshopper** in Rhino (Mac or Windows)
3. **Add a GHPython component** to your canvas
4. **Double-click** the component to open the editor
5. **Copy and paste** the entire Python script into the editor
6. **Add inputs** to the component (right-click the component):
   - `Action` (String)
   - `Mode` (Integer) 
   - `Target` (String)
   - `Length` (Float)
7. **Add outputs** (right-click):
   - `Info` (String)
   - `Count` (Integer)

## Quick Start Examples

### Example 1: Hide All Wires
```
Action = "ALL_HIDDEN"
Mode = 0
```

### Example 2: Make Selected Wires Faint
```
Action = "SEL_FAINT"
Mode = 1
```

### Example 3: Hide Long Wires
```
Action = "CLEAN_LENGTH"
Mode = 0
Length = 1500
```

### Example 4: Flatten Selected Components' Inputs
```
Action = "FLATTEN"
Target = "Inputs"
```

### Example 5: Auto-Clean by Wire Length
```
Action = "AUTO_LENGTH"
```

## All Available Actions

### WIRE DISPLAY
- `ALL_DEFAULT` - Show all wires normally
- `ALL_FAINT` - Make all wires faint
- `ALL_HIDDEN` - Hide all wires
- `SEL_DEFAULT` - Show selected wires normally
- `SEL_FAINT` - Make selected wires faint  
- `SEL_HIDDEN` - Hide selected wires

### DISCONNECT OPERATIONS
- `DISCONNECT_ALL` - Disconnect all wires from selected objects
- `DISCONNECT_INPUTS` - Disconnect only input wires
- `DISCONNECT_OUTPUTS` - Disconnect only output wires

### TREE FUNCTIONS (use with Target)
- `FLATTEN` - Flatten data trees
- `GRAFT` - Graft data trees
- `SIMPLIFY` - Toggle simplify
- `REVERSE` - Toggle reverse
- `REMOVE_TREE` - Remove all tree operations

**Target values:** `Both`, `Inputs`, `Outputs`

### CANVAS CLEANUP
- `CLEAN_LENGTH` - Modify wires longer than Length value
- `AUTO_LENGTH` - Auto-clean by relative length (top 1/3 hidden, middle faint)
- `CLEAN_GEOMETRY` - Modify geometry parameter wires
- `CLEAN_NUMBERS` - Modify number parameter wires
- `CLEAN_TEXT` - Modify text parameter wires
- `CLEAN_BOOLEAN` - Modify boolean parameter wires
- `CLEAN_COLORS` - Modify color parameter wires
- `CLEAN_DATA` - Auto-clean based on data size
- `SYNC_PREVIEW` - Match wire visibility to component preview state

### HELP
- `HELP` - Display help message with all actions

## Input Parameters

### Action (String)
The operation to perform. See list above.

### Mode (Integer)
Wire display mode:
- `0` = Hidden
- `1` = Faint
- `2` = Default (normal)

### Target (String)  
For tree operations:
- `Both` - Apply to inputs and outputs
- `Inputs` - Apply to inputs only
- `Outputs` - Apply to outputs only

### Length (Float)
For length-based operations, specify the threshold in pixels (e.g., 1500)

## Tips & Tricks

### Create Buttons
You can create button components that trigger specific actions:
1. Add a **Button** component
2. Connect it to the Action input with a **Panel** containing the action name
3. Label the button clearly (e.g., "Hide All Wires")

### Common Workflows

**Clean up a messy definition:**
```
1. Action = "AUTO_LENGTH" (auto-clean by length)
2. Action = "CLEAN_DATA" (show only data-heavy wires)
3. Action = "SYNC_PREVIEW" (match preview state)
```

**Prepare for presentation:**
```
1. Action = "ALL_HIDDEN" (hide everything)
2. Select important components
3. Action = "SEL_DEFAULT" (show only selected)
```

**Debug data flow:**
```
1. Action = "ALL_HIDDEN"
2. Select component to debug
3. Action = "SEL_DEFAULT"
4. Manually trace flow
```

## Differences from C# Plugin

**What's included:**
✅ All wire display modes
✅ Disconnect operations  
✅ Tree functions (Flatten, Graft, Simplify, Reverse)
✅ Length-based cleanup
✅ Parameter type filtering
✅ Data size visualization
✅ Preview synchronization
✅ **Fully cross-platform (Mac & Windows)**

**What's NOT included:**
❌ Top-level Grasshopper menu integration
❌ Wire color customization (canvas/wire colors)
❌ Named wire views (save/restore)
❌ Undo/redo specific to wire operations
❌ Wire flow visualization (trace upstream/downstream)

These features require C# plugin capabilities that Python components can't access.

## Troubleshooting

**"No action performed"**
- Make sure you've provided an Action input
- Check that Action is a valid command (use "HELP")

**"Unknown action"**
- Action names are case-insensitive but must match exactly
- Use "HELP" to see all available actions

**Nothing happens**
- Make sure components are selected for selection-based operations
- Check that you have an active Grasshopper document

**Component throws error**
- Make sure all inputs are the correct type
- Mode should be 0, 1, or 2
- Length should be a number

## Advanced: Creating a Custom Toolbar

You can create a dedicated toolbar with common actions:

1. Create multiple **Button** components
2. Use **Text Panel** to feed different Action strings
3. Label each button clearly
4. Group them visually on your canvas
5. Save as a **Cluster** or **User Object** for reuse

Example setup:
```
[Hide All] → "ALL_HIDDEN"
[Show All] → "ALL_DEFAULT"
[Auto Clean] → "AUTO_LENGTH"
[Flatten Selected] → "FLATTEN" (Target="Both")
```

## Performance Notes

- Operations on large definitions (1000+ components) may take a few seconds
- Length calculations require reading component positions
- Data size operations scan all volatile data

## License

MIT License - Free to use and modify

---

For questions or issues, contact: toeesha@gmail.com
