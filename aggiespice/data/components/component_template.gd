@tool
extends Resource
class_name ComponentResource

# Component metadata
@export_category("Component Identification")
@export var component_name: String = "Unnamed"
@export var component_type: String = "resistor"  # resistor, capacitor, voltage_source, etc.
@export var unique_id: String = ""

# Electrical properties
@export_category("Electrical Properties")
@export var default_value: float = 1000.0
@export var value_units: String = "Ω"  # Ω, F, V, A, H
@export var min_value: float = 0.0
@export var max_value: float = 1000000.0

# Visual representation
@export_category("Visual Properties")
@export var icon: Texture2D
@export var color: Color = Color.WHITE
@export var symbol_scene: PackedScene  # Optional: custom symbol scene

# Simulation data
@export_category("Simulation Properties")
@export var spice_model: String = ""  # For advanced components
@export var node_count: int = 2  # Most components have 2 nodes

# Tooltip/description
@export_multiline var description: String = ""

func _init():
	if unique_id.is_empty():
		unique_id = generate_unique_id()

func generate_unique_id() -> String:
	return component_type + "_" + str(Time.get_ticks_msec())

func get_netlist_data(value_override: float = -1.0) -> Dictionary:
	var actual_value = value_override if value_override > 0 else default_value
	return {
		"type": get_spice_type(),
		"value": actual_value,
		"id": unique_id
	}

func get_spice_type() -> String:
	match component_type:
		"resistor": return "R"
		"capacitor": return "C" 
		"inductor": return "L"
		"voltage_source_dc": return "VDC"
		"current_source_dc": return "IDC"
		"diode": return "D"
		"voltage_source_ac": return "VAC"
		"current_source_ac": return "IAC"
		_: return component_type

func get_display_value(with_units: bool = true) -> String:
	var value = default_value
	var display_value = str(value)
	
	# Format with appropriate prefixes
	var prefixes = ["", "K", "M", "G"]
	var prefix_index = 0
	while value >= 1000 and prefix_index < prefixes.size() - 1:
		value /= 1000
		prefix_index += 1
		display_value = "%.2f" % value
	
	if with_units:
		return display_value + " " + prefixes[prefix_index] + value_units
	else:
		return display_value
