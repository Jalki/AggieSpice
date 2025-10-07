extends Node

const HOST: String = "127.0.0.1"
const PORT: int = 9090
const RECONNECT_TIMEOUT: float = 3.0

const Client = preload("res://code/simulation_client.gd")
var _client: Client = Client.new()

func _ready() -> void:
	# Connect signals
	_client.connected.connect(_handle_client_connected)
	_client.disconnected.connect(_handle_client_disconnected)
	_client.error.connect(_handle_client_error)
	_client.data_received.connect(_handle_client_data)
	set_process(true)  # 🚀 this enables _process calls
	add_child(_client)
	_client.connect_to_host(HOST, PORT)

func _connect_after_timeout(timeout: float) -> void:
	await get_tree().create_timer(timeout).timeout
	_client.connect_to_host(HOST, PORT)

func _handle_client_connected() -> void:
	print("✅ Client connected to server.")

func _handle_client_data(data: Dictionary) -> void:
	print("📊 Simulation result received:")
	if data.has("success") and data["success"]:
		print("Message: ", data["message"])
		print("First 5 time values: ", data["time"].slice(0, 5))
		print("First 5 voltages: ", data["voltage"].slice(0, 5))
	else:
		print("❌ Error from server: ", data.get("error", "Unknown"))

func _handle_client_disconnected() -> void:
	print("⚠️ Client disconnected from server.")
	_connect_after_timeout(RECONNECT_TIMEOUT)

func _handle_client_error() -> void:
	print("❌ Client error.")
	_connect_after_timeout(RECONNECT_TIMEOUT)
