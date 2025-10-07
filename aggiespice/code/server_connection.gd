var _process: Process

func start_simulation_process():
	_process = Process.new()
	var args = ["path/to/your/simulation_worker.py"]
	_process.start("python", args)

func send_to_process(circuit_data: Dictionary):
	var json_data = JSON.stringify(circuit_data) + "\n"
	_process.write(json_data.to_utf8_buffer())
	
	# Read response (you'll want to do this asynchronously)
	var output = _process.read_line()
	return JSON.parse_string(output)
