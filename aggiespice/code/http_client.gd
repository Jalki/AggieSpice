extends Node

var _http_client: HTTPRequest

func _ready():
	_http_client = HTTPRequest.new()
	add_child(_http_client)
	_http_client.request_completed.connect(_on_request_completed)

func send_simulation_http(circuit_data: Dictionary):
	var url = "http://127.0.0.1:9090"
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify(circuit_data)
	
	var error = _http_client.request(url, headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		print("Error sending HTTP request: ", error)

func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray):
	if result == HTTPRequest.RESULT_SUCCESS and response_code == 200:
		var json_str = body.get_string_from_utf8()
		var response = JSON.parse_string(json_str)
		
		if response and response.get('success', false):
			# Process successful simulation results
			update_visualization(response.time, response.voltage)
		else:
			print("Simulation failed: ", response.get('error', 'Unknown error'))
	else:
		print("HTTP request failed: ", result, " Response code: ", response_code)
