"""
WireHopper - Python Component for Mac/Windows
Manages wire display, tree operations, and canvas cleanup in Grasshopper

Component Inputs:
    Action: String - The operation to perform (see documentation)
    Mode: Integer - Wire display mode (0=Hidden, 1=Faint, 2=Default)
    Target: String - Target scope ("All", "Selected", or specific param type)
    Length: Float - For length-based operations (in pixels)
    
Component Outputs:
    Info: String - Status message
    Count: Integer - Number of wires affected

Author: Eesha Jain (Python port)
Version: 1.0 (Mac/Windows compatible)
"""

import Grasshopper as gh
from Grasshopper.Kernel import GH_ParamWireDisplay, IGH_Param, IGH_Component
from Grasshopper.Kernel.Parameters import *
import System
from System import Guid
import Rhino
import scriptcontext as sc
import math

class WireHopperPython:
    """Main class containing all wire operations"""
    
    def __init__(self):
        self.doc = gh.Instances.ActiveCanvas.Document if gh.Instances.ActiveCanvas else None
        self.wire_modes = {
            0: GH_ParamWireDisplay.hidden,
            1: GH_ParamWireDisplay.faint,
            2: GH_ParamWireDisplay.default
        }
        
    # ==================== CORE WIRE OPERATIONS ====================
    
    def apply_wire_mode(self, param, mode):
        """Apply wire display mode to a single parameter"""
        if param and mode in self.wire_modes:
            param.WireDisplay = self.wire_modes[mode]
            if param.Attributes:
                param.Attributes.ExpireLayout()
    
    def set_all_wires(self, mode):
        """Set wire mode for ALL wires in document"""
        if not self.doc:
            return 0
            
        count = 0
        for obj in self.doc.Objects:
            if isinstance(obj, IGH_Param):
                self.apply_wire_mode(obj, mode)
                count += 1
            elif isinstance(obj, IGH_Component):
                for param in obj.Params.Input:
                    self.apply_wire_mode(param, mode)
                    count += 1
                for param in obj.Params.Output:
                    self.apply_wire_mode(param, mode)
                    count += 1
        
        # Set global setting
        gh.Instances.Settings.SetValue("Draw Wires", mode)
        
        if gh.Instances.ActiveCanvas:
            gh.Instances.ActiveCanvas.Refresh()
        
        return count
    
    def set_selected_wires(self, mode):
        """Set wire mode for SELECTED objects only"""
        if not self.doc:
            return 0
            
        count = 0
        for obj in self.doc.SelectedObjects():
            if isinstance(obj, IGH_Param):
                self.apply_wire_mode(obj, mode)
                count += 1
            elif isinstance(obj, IGH_Component):
                for param in obj.Params.Input:
                    self.apply_wire_mode(param, mode)
                    count += 1
                for param in obj.Params.Output:
                    self.apply_wire_mode(param, mode)
                    count += 1
        
        if gh.Instances.ActiveCanvas:
            gh.Instances.ActiveCanvas.Refresh()
        
        return count
    
    # ==================== DISCONNECT OPERATIONS ====================
    
    def disconnect_selected(self, target="All"):
        """Disconnect wires from selected objects"""
        if not self.doc:
            return 0
            
        count = 0
        for obj in self.doc.SelectedObjects():
            if isinstance(obj, IGH_Component):
                if target in ["All", "Inputs"]:
                    for inp in obj.Params.Input:
                        count += len(inp.Sources)
                        inp.RemoveAllSources()
                
                if target in ["All", "Outputs"]:
                    for out in obj.Params.Output:
                        recipients = list(out.Recipients)
                        for rec in recipients:
                            rec.RemoveSource(out)
                            count += 1
                
                obj.ExpireSolution(True)
                
            elif isinstance(obj, IGH_Param):
                if target in ["All", "Inputs"]:
                    count += len(obj.Sources)
                    obj.RemoveAllSources()
                
                if target in ["All", "Outputs"]:
                    recipients = list(obj.Recipients)
                    for rec in recipients:
                        rec.RemoveSource(obj)
                        count += 1
                
                obj.ExpireSolution(True)
        
        return count
    
    # ==================== TREE OPERATIONS ====================
    
    def apply_tree_function(self, function_name, target="Both"):
        """Apply tree functions to selected parameters"""
        if not self.doc:
            return 0
            
        count = 0
        for obj in self.doc.SelectedObjects():
            if isinstance(obj, IGH_Component):
                params = []
                if target in ["Both", "Inputs"]:
                    params.extend(obj.Params.Input)
                if target in ["Both", "Outputs"]:
                    params.extend(obj.Params.Output)
                
                for param in params:
                    if self._apply_function_to_param(param, function_name):
                        count += 1
                        if param.Attributes:
                            param.Attributes.ExpireLayout()
                
                obj.ExpireSolution(True)
                
            elif isinstance(obj, IGH_Param) and target == "Both":
                if self._apply_function_to_param(obj, function_name):
                    count += 1
                    if obj.Attributes:
                        obj.Attributes.ExpireLayout()
                    obj.ExpireSolution(True)
        
        if count > 0:
            self.doc.NewSolution(True)
        
        return count
    
    def _apply_function_to_param(self, param, function_name):
        """Helper to apply specific tree function"""
        if function_name == "Flatten":
            prop = param.GetType().GetProperty("DataMapping")
            if prop:
                prop.SetValue(param, System.Enum.Parse(prop.PropertyType, "Flatten"))
                return True
        
        elif function_name == "Graft":
            prop = param.GetType().GetProperty("DataMapping")
            if prop:
                prop.SetValue(param, System.Enum.Parse(prop.PropertyType, "Graft"))
                return True
        
        elif function_name == "Simplify":
            param.Simplify = not param.Simplify
            return True
        
        elif function_name == "Reverse":
            param.Reverse = not param.Reverse
            return True
        
        elif function_name == "RemoveAll":
            prop = param.GetType().GetProperty("DataMapping")
            if prop:
                prop.SetValue(param, System.Enum.Parse(prop.PropertyType, "None"))
            param.Simplify = False
            param.Reverse = False
            return True
        
        return False
    
    # ==================== LENGTH-BASED OPERATIONS ====================
    
    def clean_by_length(self, max_length, mode):
        """Hide/modify wires longer than specified length"""
        if not self.doc:
            return 0
            
        count = 0
        for obj in self.doc.Objects:
            params = []
            
            if isinstance(obj, IGH_Param):
                params.append(obj)
            elif isinstance(obj, IGH_Component):
                params.extend(obj.Params.Input)
                params.extend(obj.Params.Output)
            
            for param in params:
                for source in param.Sources:
                    if source.Attributes and param.Attributes:
                        src_pt = source.Attributes.OutputGrip
                        dst_pt = param.Attributes.InputGrip
                        
                        dx = src_pt.X - dst_pt.X
                        dy = src_pt.Y - dst_pt.Y
                        length = math.sqrt(dx * dx + dy * dy)
                        
                        if length > max_length:
                            self.apply_wire_mode(param, mode)
                            count += 1
                            break
        
        if gh.Instances.ActiveCanvas:
            gh.Instances.ActiveCanvas.Refresh()
        
        return count
    
    def set_by_relative_length(self):
        """Auto-clean wires based on relative length (top third hidden, middle faint, bottom default)"""
        if not self.doc:
            return 0
            
        # Collect all wire lengths
        wire_lengths = []
        
        for obj in self.doc.Objects:
            params = []
            if isinstance(obj, IGH_Param):
                params.append(obj)
            elif isinstance(obj, IGH_Component):
                params.extend(obj.Params.Input)
                params.extend(obj.Params.Output)
            
            for param in params:
                for source in param.Sources:
                    if source.Attributes and param.Attributes:
                        src_pt = source.Attributes.OutputGrip
                        dst_pt = param.Attributes.InputGrip
                        
                        dx = src_pt.X - dst_pt.X
                        dy = src_pt.Y - dst_pt.Y
                        length = math.sqrt(dx * dx + dy * dy)
                        
                        wire_lengths.append((param, length))
        
        if not wire_lengths:
            return 0
        
        max_length = max(l for _, l in wire_lengths)
        tier1 = max_length / 3.0
        tier2 = max_length * 2.0 / 3.0
        
        count = 0
        for param, length in wire_lengths:
            if length >= tier2:
                self.apply_wire_mode(param, 0)  # Hidden
            elif length >= tier1:
                self.apply_wire_mode(param, 1)  # Faint
            else:
                self.apply_wire_mode(param, 2)  # Default
            count += 1
        
        if gh.Instances.ActiveCanvas:
            gh.Instances.ActiveCanvas.Refresh()
        
        return count
    
    # ==================== PARAM TYPE OPERATIONS ====================
    
    def clean_by_param_type(self, param_type, mode, include_inputs=True, include_outputs=True):
        """Clean wires by parameter type"""
        if not self.doc:
            return 0
        
        # Define parameter groups
        param_groups = {
            "Geometry": [Param_Geometry, Param_Brep, Param_Surface, Param_Mesh, 
                        Param_Curve, Param_Point, Param_Vector, Param_Line, 
                        Param_Arc, Param_Circle, Param_Plane, Param_Box],
            "Numbers": [Param_Number, Param_Integer, Param_Complex, Param_Interval],
            "Text": [Param_String],
            "Boolean": [Param_Boolean],
            "Colors": [Param_Colour]
        }
        
        if param_type not in param_groups:
            return 0
        
        target_types = param_groups[param_type]
        count = 0
        
        for obj in self.doc.Objects:
            params = []
            
            if isinstance(obj, IGH_Param):
                params.append(obj)
            elif isinstance(obj, IGH_Component):
                if include_inputs:
                    params.extend(obj.Params.Input)
                if include_outputs:
                    params.extend(obj.Params.Output)
            
            for param in params:
                param_type_obj = type(param)
                if any(param_type_obj == t or issubclass(param_type_obj, t) for t in target_types):
                    self.apply_wire_mode(param, mode)
                    count += 1
        
        if gh.Instances.ActiveCanvas:
            gh.Instances.ActiveCanvas.Refresh()
        
        return count
    
    # ==================== DATA SIZE OPERATIONS ====================
    
    def clean_by_data_size(self):
        """Set wire modes based on volatile data count"""
        if not self.doc:
            return 0
        
        # Collect all parameters with data counts
        all_params = []
        for obj in self.doc.Objects:
            if isinstance(obj, IGH_Param):
                all_params.append(obj)
            elif isinstance(obj, IGH_Component):
                all_params.extend(obj.Params.Input)
                all_params.extend(obj.Params.Output)
        
        if not all_params:
            return 0
        
        max_count = max(p.VolatileDataCount for p in all_params)
        if max_count == 0:
            max_count = 1
        
        tier1 = max_count / 3
        tier2 = max_count * 2 / 3
        
        count = 0
        for param in all_params:
            data_count = param.VolatileDataCount
            
            if data_count >= tier2:
                self.apply_wire_mode(param, 2)  # Default (most data)
            elif data_count >= tier1:
                self.apply_wire_mode(param, 1)  # Faint (medium data)
            else:
                self.apply_wire_mode(param, 0)  # Hidden (least data)
            count += 1
        
        if gh.Instances.ActiveCanvas:
            gh.Instances.ActiveCanvas.Refresh()
        
        return count
    
    # ==================== PREVIEW SYNC ====================
    
    def sync_with_preview(self):
        """Sync wire display with component preview state"""
        if not self.doc:
            return 0
        
        count = 0
        for obj in self.doc.Objects:
            preview_on = True
            
            # Check if object has preview capability
            if hasattr(obj, 'IsPreviewCapable') and hasattr(obj, 'Hidden'):
                preview_on = obj.IsPreviewCapable and not obj.Hidden
            
            mode = 2 if preview_on else 0  # Default or Hidden
            
            if isinstance(obj, IGH_Param):
                self.apply_wire_mode(obj, mode)
                count += 1
            elif isinstance(obj, IGH_Component):
                for param in obj.Params.Input:
                    self.apply_wire_mode(param, mode)
                    count += 1
                for param in obj.Params.Output:
                    self.apply_wire_mode(param, mode)
                    count += 1
        
        if gh.Instances.ActiveCanvas:
            gh.Instances.ActiveCanvas.Refresh()
        
        return count


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    # Initialize the wire hopper
    hopper = WireHopperPython()
    
    # Default outputs
    Info = "No action performed"
    Count = 0
    
    # Parse action (default to "Help" if not provided)
    action = Action.upper() if 'Action' in globals() and Action else "HELP"
    
    # Parse mode (default to 2 = Default)
    mode = int(Mode) if 'Mode' in globals() and Mode is not None else 2
    
    # Parse target (default to "All")
    target = Target if 'Target' in globals() and Target else "All"
    
    # Parse length (default to 1000)
    length = float(Length) if 'Length' in globals() and Length is not None else 1000.0
    
    # Execute action
    try:
        if action == "HELP":
            Info = """WireHopper Actions:
            
WIRE DISPLAY:
  ALL_DEFAULT, ALL_FAINT, ALL_HIDDEN - Set all wires
  SEL_DEFAULT, SEL_FAINT, SEL_HIDDEN - Set selected wires
  
DISCONNECT:
  DISCONNECT_ALL - Disconnect all wires from selected
  DISCONNECT_INPUTS - Disconnect inputs only
  DISCONNECT_OUTPUTS - Disconnect outputs only
  
TREE FUNCTIONS:
  FLATTEN, GRAFT, SIMPLIFY, REVERSE - Apply to selected
  REMOVE_TREE - Remove all tree operations
  (Use Target: Both/Inputs/Outputs)
  
CLEANUP:
  CLEAN_LENGTH - Hide wires > Length pixels (use Mode)
  AUTO_LENGTH - Auto-clean by relative length
  CLEAN_GEOMETRY, CLEAN_NUMBERS, CLEAN_TEXT - By param type
  CLEAN_DATA - By data size
  SYNC_PREVIEW - Match component preview state

Examples:
  Action='ALL_HIDDEN', Mode=0
  Action='CLEAN_LENGTH', Length=1500, Mode=0
  Action='FLATTEN', Target='Inputs'"""
        
        # Wire display actions
        elif action == "ALL_DEFAULT":
            Count = hopper.set_all_wires(2)
            Info = f"Set {Count} wires to Default"
        
        elif action == "ALL_FAINT":
            Count = hopper.set_all_wires(1)
            Info = f"Set {Count} wires to Faint"
        
        elif action == "ALL_HIDDEN":
            Count = hopper.set_all_wires(0)
            Info = f"Set {Count} wires to Hidden"
        
        elif action == "SEL_DEFAULT":
            Count = hopper.set_selected_wires(2)
            Info = f"Set {Count} selected wires to Default"
        
        elif action == "SEL_FAINT":
            Count = hopper.set_selected_wires(1)
            Info = f"Set {Count} selected wires to Faint"
        
        elif action == "SEL_HIDDEN":
            Count = hopper.set_selected_wires(0)
            Info = f"Set {Count} selected wires to Hidden"
        
        # Disconnect actions
        elif action == "DISCONNECT_ALL":
            Count = hopper.disconnect_selected("All")
            Info = f"Disconnected {Count} wires"
        
        elif action == "DISCONNECT_INPUTS":
            Count = hopper.disconnect_selected("Inputs")
            Info = f"Disconnected {Count} input wires"
        
        elif action == "DISCONNECT_OUTPUTS":
            Count = hopper.disconnect_selected("Outputs")
            Info = f"Disconnected {Count} output wires"
        
        # Tree function actions
        elif action == "FLATTEN":
            Count = hopper.apply_tree_function("Flatten", target)
            Info = f"Flattened {Count} parameters"
        
        elif action == "GRAFT":
            Count = hopper.apply_tree_function("Graft", target)
            Info = f"Grafted {Count} parameters"
        
        elif action == "SIMPLIFY":
            Count = hopper.apply_tree_function("Simplify", target)
            Info = f"Toggled Simplify on {Count} parameters"
        
        elif action == "REVERSE":
            Count = hopper.apply_tree_function("Reverse", target)
            Info = f"Toggled Reverse on {Count} parameters"
        
        elif action == "REMOVE_TREE":
            Count = hopper.apply_tree_function("RemoveAll", target)
            Info = f"Removed tree operations from {Count} parameters"
        
        # Length-based cleanup
        elif action == "CLEAN_LENGTH":
            Count = hopper.clean_by_length(length, mode)
            Info = f"Modified {Count} wires longer than {length}px"
        
        elif action == "AUTO_LENGTH":
            Count = hopper.set_by_relative_length()
            Info = f"Auto-cleaned {Count} wires by relative length"
        
        # Param type cleanup
        elif action == "CLEAN_GEOMETRY":
            Count = hopper.clean_by_param_type("Geometry", mode)
            Info = f"Modified {Count} geometry parameter wires"
        
        elif action == "CLEAN_NUMBERS":
            Count = hopper.clean_by_param_type("Numbers", mode)
            Info = f"Modified {Count} number parameter wires"
        
        elif action == "CLEAN_TEXT":
            Count = hopper.clean_by_param_type("Text", mode)
            Info = f"Modified {Count} text parameter wires"
        
        elif action == "CLEAN_BOOLEAN":
            Count = hopper.clean_by_param_type("Boolean", mode)
            Info = f"Modified {Count} boolean parameter wires"
        
        elif action == "CLEAN_COLORS":
            Count = hopper.clean_by_param_type("Colors", mode)
            Info = f"Modified {Count} color parameter wires"
        
        # Data size cleanup
        elif action == "CLEAN_DATA":
            Count = hopper.clean_by_data_size()
            Info = f"Auto-cleaned {Count} wires by data size"
        
        # Preview sync
        elif action == "SYNC_PREVIEW":
            Count = hopper.sync_with_preview()
            Info = f"Synced {Count} wires with preview state"
        
        else:
            Info = f"Unknown action: {action}. Use 'HELP' for action list."
    
    except Exception as e:
        Info = f"Error: {str(e)}"
        Count = -1
