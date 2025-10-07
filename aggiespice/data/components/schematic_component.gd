extends TextureButton
class_name SchematicComponent

@export var component_data: ComponentResource
@export var current_value: float = -1.0

# Runtime data
var node_ids: Array[int] = [-1, -1]  # Connected node IDs
var schematic_position: Vector2
var is_selected: bool = false

signal component_selected(component: SchematicComponent)
signal component_double_clicked(component: SchematicComponent)
signal value_changed(component: SchematicComponent, new_value: float)

func _ready():
	if component_data:
		_setup_from_resource()
	
	pressed.connect(_on_pressed)
	gui_input.connect(_on_gui_input)

func _setup_from_resource():
	if not component_data:
		return
		
	# Set up visual appearance
	tooltip_text = component_data.component_name + "\n" + component_data.description
	tooltip_text += "\nCurrent value: " + get_display_value()
	
	if component_data.icon:
		texture_normal = component_data.icon
		
	
	modulate = component_data.color
	
	# Use default value if current_value not set
	if current_value < 0:
		current_value = component_data.default_value

func _on_pressed():
	component_selected.emit(self)

func _on_gui_input(event: InputEvent):
	if event is InputEventMouseButton and event.double_click:
		component_double_clicked.emit(self)

func get_netlist_data() -> Dictionary:
	if not component_data:
		return {}
	
	var data = component_data.get_netlist_data(current_value)
	data["nodes"] = node_ids.duplicate()
	return data

func set_nodes(new_node_ids: Array[int]):
	if new_node_ids.size() >= component_data.node_count:
		node_ids = new_node_ids.slice(0, component_data.node_count)
	else:
		push_warning("Not enough nodes for component")

func set_value(new_value: float):
	if component_data:
		# Clamp to valid range
		new_value = clamp(new_value, component_data.min_value, component_data.max_value)
		current_value = new_value
		
		# Update tooltip
		tooltip_text = component_data.component_name + "\n" + component_data.description
		tooltip_text += "\nCurrent value: " + get_display_value()
		
		value_changed.emit(self, new_value)

func get_display_value() -> String:
	if not component_data:
		return "No data"
	
	return _format_value_with_units(current_value, component_data.value_units)

func _format_value_with_units(value: float, units: String) -> String:
	# Smart formatting based on value size
	match units:
		"F":  # Capacitors - show µF, nF, pF
			if value >= 0.000001:
				return "%.2f µF" % (value * 1000000)
			elif value >= 0.000000001:
				return "%.2f nF" % (value * 1000000000)
			else:
				return "%.2f pF" % (value * 1000000000000)
		"Ω":  # Resistors - show Ω, kΩ, MΩ
			if value >= 1000000:
				return "%.2f MΩ" % (value / 1000000)
			elif value >= 1000:
				return "%.2f kΩ" % (value / 1000)
			else:
				return "%.1f Ω" % value
		"H":  # Inductors - show H, mH, µH
			if value >= 1:
				return "%.2f H" % value
			elif value >= 0.001:
				return "%.2f mH" % (value * 1000)
			else:
				return "%.2f µH" % (value * 1000000)
		_:  # Voltage, current - just show value
			return "%.2f %s" % [value, units]

# Visual feedback
func set_selected(selected: bool):
	is_selected = selected
	if selected:
		modulate = component_data.color.lightened(0.3)
	else:
		modulate = component_data.color
