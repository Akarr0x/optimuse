from flask import Flask, request, jsonify, Response
import json
import logging
from dao.profile_dao import LoadDataDAO
from processor.processor import EnergyProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


# Initialize DAO and Processor
dao = LoadDataDAO('../data/json_database.json')
dao.replace_ids_with_names()
processor = EnergyProcessor(dao)

@app.route('/energy_demand', methods=['GET'])
def get_energy_demand():
    """
    API endpoint to retrieve the energy demand for a specified asset by name.
    """
    asset_name = request.args.get('name', default=None, type=str)

    if asset_name is not None:
        asset_info = next((asset for asset in dao.data['asset'] if asset['name'].lower() == asset_name.lower()), None)
        if asset_info is not None:
            energy_demand_info = processor.calculate_energy_demand(asset_name)
            json_response = json.dumps(energy_demand_info, indent=4, sort_keys=False)
            return Response(json_response, mimetype='application/json')
        else:
            logging.error(f"Invalid asset name provided: {asset_name}")
            return jsonify({"error": "Invalid asset name"}), 404
    else:
        logging.error("No asset name was provided in the request")
        return jsonify({"error": "Asset name is required"}), 400

if __name__ == '__main__':
    app.run(debug=True)
