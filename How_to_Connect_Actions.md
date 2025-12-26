# How to Connect Actions to WireHopper Python Component

## Setup Overview

```
[Text Panel] → [Action input] → [WireHopper Python Component] → [Info output] → [Panel]
   "ALL_HIDDEN"                                                    [Count output] → [Panel]
```

## Method 1: Simple Text Panel (Recommended for Single Actions)

**Steps:**
1. **Create a Panel** component (Params > Input > Panel)
2. **Double-click the panel** and type your action name (e.g., `ALL_HIDDEN`)
3. **Wire the panel output** to the `Action` input on your Python component
4. **Toggle the button** or update the panel to execute

**Example:**
```
┌──────────────┐
│  ALL_HIDDEN  │ ───→ [Action] → [WireHopper] → Results
└──────────────┘
   (Panel)
```

## Method 2: Button + Panel Combo (Best for Multiple Quick Actions)

**Steps:**
1. **Create a Button** (Params > Input > Button)
2. **Create a Panel** with your action name
3. **Wire the Button to the Panel** (forces refresh)
4. **Wire the Panel to Action input**
5. **Click the button** to execute

**Example:**
```
┌─────────┐     ┌──────────────┐
│ [CLICK] │ ──→ │  ALL_HIDDEN  │ ───→ [Action] → [WireHopper]
└─────────┘     └──────────────┘
  (Button)         (Panel)
```

**Create multiple buttons for different actions:**
```
┌─────────┐     ┌──────────────┐
│ Hide All│ ──→ │  ALL_HIDDEN  │ ───┐
└─────────┘     └──────────────┘    │
                                     ├──→ [Action]
┌─────────┐     ┌──────────────┐    │
│ Show All│ ──→ │  ALL_DEFAULT │ ───┤
└─────────┘     └──────────────┘    │
                                     │
┌─────────┐     ┌──────────────┐    │
│AutoClean│ ──→ │  AUTO_LENGTH │ ───┘
└─────────┘     └──────────────┘
```

## Method 3: Value List (Best for Switching Between Actions)

**Steps:**
1. **Create a Value List** (Params > Input > Value List)
2. **Double-click it** to edit
3. **Add your actions**, one per line:
   ```
   Hide All = ALL_HIDDEN
   Show All = ALL_DEFAULT
   Faint All = ALL_FAINT
   Selected Hidden = SEL_HIDDEN
   Auto Clean = AUTO_LENGTH
   Clean by Data = CLEAN_DATA
   Flatten = FLATTEN
   Graft = GRAFT
   Disconnect All = DISCONNECT_ALL
   ```
4. **Wire Value List output** to `Action` input
5. **Right-click Value List** and select an action from the dropdown

**Example:**
```
┌──────────────────┐
│ Value List       │
│ ✓ Hide All       │
│   Show All       │───→ [Action] → [WireHopper]
│   Faint All      │
│   Auto Clean     │
└──────────────────┘
```

## Method 4: Stream Filter (Advanced - Conditional Actions)

Use boolean logic to switch between actions:

```
[Boolean Toggle] ──→ [Stream Filter] ──→ [Action]
                         ↑
                    ┌────┴─────┐
                    │          │
              [ALL_HIDDEN] [ALL_DEFAULT]
                Panel         Panel
```

When True, outputs first input; when False, outputs second input.

## Method 5: Keyboard Input (for frequent use)

**Steps:**
1. **Create a Text Panel**
2. **Double-click to edit**
3. **Type your action name**
4. **Press Enter** to update (triggers execution)
5. **Change text** as needed for different actions

## Complete Example Setup

Here's a full working setup:

```
INPUTS:
┌──────────────┐
│ ALL_HIDDEN   │ ──→ [Action] ──┐
└──────────────┘                │
                                │
┌──────────────┐                │
│      0       │ ──→ [Mode] ────┤
└──────────────┘                │
                                ├──→ [WireHopper Python]
┌──────────────┐                │
│    Both      │ ──→ [Target]───┤
└──────────────┘                │
                                │
┌──────────────┐                │
│    1500      │ ──→ [Length]───┘
└──────────────┘

OUTPUTS:
                                ┌──→ [Info] ──→ ┌──────────────┐
[WireHopper Python] ────────────┤               │ Modified 47  │
                                │               │ wires        │
                                └──→ [Count] ──→└──────────────┘
```

## Pro Tips

### Tip 1: Create a Control Panel
Group all your common actions together:

```
┌─────────────────────────────────────┐
│      WIREHOPPER CONTROLS            │
├─────────────────────────────────────┤
│ [Hide All]  [Show All]  [Faint All] │
│ [Hide Long Wires]  [Auto Clean]     │
│ [Flatten Selected]  [Disconnect]    │
└─────────────────────────────────────┘
```

### Tip 2: Use Data Dam for Manual Control
Add a **Data Dam** component after your panels to prevent auto-execution:

```
[Panel: ALL_HIDDEN] ──→ [Data Dam] ──→ [Action]
                         (Extract button to run)
```

### Tip 3: Color Code Your Buttons
Right-click buttons and panels to change colors for visual organization:
- 🔴 Red = Destructive (Disconnect, Hide)
- 🟢 Green = Show/Default
- 🔵 Blue = Analysis (Auto Clean, Data Size)

### Tip 4: Label Everything
Double-click near components to add text labels:
```
   HIDE ALL WIRES
┌─────────┐     ┌──────────────┐
│ [CLICK] │ ──→ │  ALL_HIDDEN  │ ───→ [Action]
└─────────┘     └──────────────┘
```

### Tip 5: Create a Template
Save your configured WireHopper component as a **User Object**:
1. Select your configured component with all inputs
2. Right-click → Create User Object
3. Name it "WireHopper Controller"
4. Save to your Grasshopper user objects folder
5. Reuse in any definition!

## Common Setup Examples

### Example A: Simple Hide/Show Toggle
```
[Boolean Toggle] ──→ [Stream Filter] ──→ [Action] ──→ [WireHopper]
                          ↑
                    ┌─────┴──────┐
              [ALL_HIDDEN]   [ALL_DEFAULT]
```

### Example B: Length Slider
```
[Number Slider: 500-3000] ──→ [Length]  ──┐
[Panel: CLEAN_LENGTH]     ──→ [Action]  ──┼──→ [WireHopper]
[Number Slider: 0-2]      ──→ [Mode]    ──┘
```

### Example C: Multi-Action Toolbar
```
┌──────┐  ┌────────────┐
│Button├─→│ ALL_HIDDEN │──┐
└──────┘  └────────────┘  │
                          │
┌──────┐  ┌────────────┐  │
│Button├─→│ALL_DEFAULT │──┤
└──────┘  └────────────┘  │
                          ├──→[Action]──→[WireHopper]
┌──────┐  ┌────────────┐  │
│Button├─→│AUTO_LENGTH │──┤
└──────┘  └────────────┘  │
                          │
┌──────┐  ┌────────────┐  │
│Button├─→│CLEAN_DATA  │──┘
└──────┘  └────────────┘
```

## Troubleshooting Connection Issues

**Problem:** "Nothing happens when I click"
- ✓ Make sure panel is connected to Action input
- ✓ Check that text in panel exactly matches action name
- ✓ Try adding a button before the panel to force refresh

**Problem:** "Invalid action" error
- ✓ Action names are case-insensitive but must be spelled correctly
- ✓ Use Action = "HELP" to see all valid action names
- ✓ Check for typos or extra spaces

**Problem:** "Component doesn't update"
- ✓ Python components cache results - change the input to force recalculation
- ✓ Right-click component → Recompute
- ✓ Add a button to force refresh

**Problem:** "Multiple actions at once?"
- ❌ Only one action runs at a time
- ✓ Use Stream Filter or Value List to switch between actions
- ✓ Create multiple WireHopper components for simultaneous operations

## Next Steps

1. **Start simple:** Just connect one panel with "ALL_HIDDEN" to test
2. **Add more actions:** Create buttons for your most-used operations
3. **Build a toolbar:** Group related actions together
4. **Save as template:** Create a User Object for reuse

Need help with a specific setup? Just ask!
