extends Panel

@onready var name_label = $VBoxContainer/NameLabel
@onready var value_slider = $VBoxContainer/ValueSlider
@onready var value_spinbox = $VBoxContainer/HBoxContainer/ValueSpinBox
@onready var value_label = $VBoxContainer/HBoxContainer/ValueLabel
@onready var units_label = $VBoxContainer/UnitsLabel

var current_component: SchematicComponent = null

signal value_changed(component: SchematicComponent, new_value: float)

func _ready():
	value_slider.value_changed.connect(_on_slider_changed)
	value_spinbox.value_changed.connect(_on_spinbox_changed)
	hide()

func show_for_component(component: SchematicComponent):
	current_component = component
	if not component or not component.component_data:
		hide()
		return
	
	var data = component.component_data
	
	# Update UI
	name_label.text = data.component_name
	value_slider.min_value = data.min_value
	value_slider.max_value = data.max_value
	value_slider.value = component.current_value
	
	value_spinbox.min_value = data.min_value
	value_spinbox.max_value = data.max_value
	value_spinbox.value = component.current_value
	
	units_label.text = data.value_units
	
	_update_value_display(component.current_value)
	show()

func _on_slider_changed(value: float):
	if current_component:
		value_spinbox.value = value
		_update_component_value(value)

func _on_spinbox_changed(value: float):
	if current_component:
		value_slider.value = value
		_update_component_value(value)

func _update_component_value(value: float):
	if current_component:
		current_component.set_value(value)
		_update_value_display(value)
		value_changed.emit(current_component, value)

func _update_value_display(value: float):
	if current_component and current_component.component_data:
		var data = current_component.component_data
		var display_value = _format_value(value, data.value_units)
		value_label.text = display_value

func _format_value(value: float, units: String) -> String:
	# Format with appropriate SI prefixes
	var prefixes = ["", "K", "M", "G"]
	var prefix_names = ["", "Kilo", "Mega", "Giga"]
	var divisor = 1.0
	var prefix_index = 0
	
	# Determine appropriate prefix
	while value >= 1000 and prefix_index < prefixes.size() - 1:
		value /= 1000
		divisor *= 1000
		prefix_index += 1
	
	# Special formatting for very small values (capacitors)
	if value < 0.001 and units == "F":
		if value < 0.000000001:
			value *= 1000000000000
			return "%.2f pF" % value
		elif value < 0.000001:
			value *= 1000000000
			return "%.2f nF" % value
		else:
			value *= 1000000
			return "%.2f µF" % value
	
	# Standard formatting
	if value == int(value):
		return "%d %s%s" % [value, prefixes[prefix_index], units]
	else:
		return "%.2f %s%s" % [value, prefixes[prefix_index], units]
