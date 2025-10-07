extends Node

signal connected
signal data_received(data: Dictionary)
signal disconnected
signal error

var _tcp_client: StreamPeerTCP = StreamPeerTCP.new()
var _status: int = StreamPeerTCP.STATUS_NONE

func _ready() -> void:
	_status = _tcp_client.get_status()
	set_process(true)  # 🚀 this enables _process calls

func connect_to_host(host: String, port: int) -> void:
	print("Connecting to %s:%d" % [host, port])
	_status = StreamPeerTCP.STATUS_NONE
	if _tcp_client.connect_to_host(host, port) != OK:
		print("Error connecting to host.")
		emit_signal("error")

func send_json(payload: Dictionary) -> bool:
	if _status != StreamPeerTCP.STATUS_CONNECTED:
		print("Error: Not connected, cannot send JSON.")
		return false

	var json_str: String = JSON.stringify(payload)
	var buffer: PackedByteArray = json_str.to_utf8_buffer()

	var err: int = _tcp_client.put_data(buffer)
	if err != OK:
		print("Error writing to stream: ", err)
		return false

	# Optional newline to indicate end of message
	_tcp_client.put_data("\n".to_utf8_buffer())
	return true

func _process(delta: float) -> void:
	_tcp_client.poll()
	var new_status: int = _tcp_client.get_status()
	if new_status != _status:
		_status = new_status
		match _status:
			StreamPeerTCP.STATUS_NONE:
				print("Disconnected from host.")
				emit_signal("disconnected")
			StreamPeerTCP.STATUS_CONNECTING:
				print("Connecting to host.")
			StreamPeerTCP.STATUS_CONNECTED:
				print("Connected to host.")
				emit_signal("connected")
				_send_test_circuit() #Test circuit is immediately sent!
			StreamPeerTCP.STATUS_ERROR:
				print("Error with socket stream.")
				emit_signal("error")

	if _status == StreamPeerTCP.STATUS_CONNECTED:
		var available_bytes: int = _tcp_client.get_available_bytes()
		if available_bytes > 0:
			var packet: Array = _tcp_client.get_partial_data(available_bytes)
			if packet[0] != OK:
				print("Error getting data from stream: ", packet[0])
				emit_signal("error")
			else:
				var raw_text: String = packet[1].get_string_from_utf8().strip_edges()
				if raw_text == "":
					return

				var parsed: Variant = JSON.parse_string(raw_text)
				if typeof(parsed) != TYPE_DICTIONARY:
					print("Invalid JSON received: ", raw_text)
					emit_signal("error")
				else:
					emit_signal("data_received", parsed as Dictionary)

func _send_test_circuit() -> void:
	var circuit := {
		"components": [
			{"type": "R", "value": 500, "nodes": [1, 2], "id": "R1"},
			{"type": "C", "value": 1e-6, "nodes": [2, 0], "id": "C1"},
			{"type": "V", "value": 20, "nodes": [1, 0], "id": "V1"}
		],
		"analysis": "transient",
		"duration": 0.1,
		"points": 750
	}
	var json_str := JSON.stringify(circuit)
	var err := _tcp_client.put_data(json_str.to_utf8_buffer())
	if err == OK:
		print("Sent data")
	else:
		print("OH FUCK NO!")
