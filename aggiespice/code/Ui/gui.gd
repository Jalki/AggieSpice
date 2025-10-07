extends CanvasLayer

@onready var component_panel = $UI/ComponentPanel
@onready var schematic_area = $SchematicArea
@onready var properties_panel = $UI/ComponentPropertiesPanel
@onready var status_label = $UI/StatusLabel

var component_resources: Array[ComponentResource] = []
var selected_component: SchematicComponent = null

func _ready():
	# Load component resources
	component_resources = [
		load("res://components/resistor_1k.tres"),
		load("res://components/capacitor_1uF.tres"), 
		load("res://components/voltage_source_5V.tres")
	]
	
	_populate_component_panel()
	properties_panel.value_changed.connect(_on_component_value_changed)

func _populate_component_panel():
	for resource in component_resources:
		var button = SchematicComponent.new()
		button.component_data = resource
		button.component_selected.connect(_on_library_component_selected)
		component_panel.add_child(button)

func _on_library_component_selected(component: SchematicComponent):
	# Clone the component for placement in schematic
	var new_component = SchematicComponent.new()
	new_component.component_data = component.component_data
	new_component.component_selected.connect(_on_schematic_component_selected)
	new_component.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	schematic_area.add_child(new_component)
	
	# Position at center of schematic area
	new_component.position = schematic_area.size * 0.5 - new_component.size * 0.5

func _on_schematic_component_selected(component: SchematicComponent):
	# Deselect previous component
	if selected_component:
		selected_component.set_selected(false)
	
	# Select new component
	selected_component = component
	component.set_selected(true)
	
	# Show properties panel
	properties_panel.show_for_component(component)
	status_label.text = "Selected: " + component.component_data.component_name

func _on_component_value_changed(component: SchematicComponent, new_value: float):
	status_label.text = "%s value changed to %s" % [component.component_data.component_name, component.get_display_value()]

func _input(event):
	if event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_DELETE:
				if selected_component:
					_delete_selected_component()
			KEY_ESCAPE:
				_deselect_component()

func _delete_selected_component():
	if selected_component:
		selected_component.queue_free()
		selected_component = null
		properties_panel.hide()
		status_label.text = "Component deleted"

func _deselect_component():
	if selected_component:
		selected_component.set_selected(false)
		selected_component = null
	properties_panel.hide()
	status_label.text = "Ready"

func generate_netlist() -> Dictionary:
	var components_data = []
	
	for child in schematic_area.get_children():
		if child is SchematicComponent:
			var comp_data = child.get_netlist_data()
			if comp_data:
				components_data.append(comp_data)
	
	return {
		"components": components_data,
		"analysis": {"type": "transient", "duration": 0.01}
	}
