import time
from flask import Flask
from flask import request, jsonify
from Processor import Processor
import logging

log = logging.getLogger("main")
log.setLevel(logging.DEBUG)		# TODO: Adjust before deployment
app = Flask(__name__)
ps = Processor()

@app.route('/time')
def get_current_time():
	log.debug("Get Current Time")
	return {'time': time.time()}
	# Test 123

@app.route('/api/list_items')
def list_items():
	log.debug("Listing All Items")
	items = [k for k in ps.dh.all_items if isinstance(k,str)]
	# items = {"value": k for k in ps.dh.all_items if isinstance(k, str)}
	return jsonify({'all': items})



@app.route('/api/search')
def tell_search_params():
	print('Test API')
	# return jsonify(request.args)
	return jsonify({'data': ps.query_mermaid(request.args['item'])})
	# Returns {item: "item name"}
    #return {'time': time.time()}


