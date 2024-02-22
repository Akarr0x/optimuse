from processor.processor import EnergyProcessor
import logging
import json

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


class LoadDataDAO:
    """
    A Data Access Object (DAO) class responsible for loading data from a JSON file.

    Attributes:
        file_path (str): The path to the JSON file to be loaded.
        data (dict): The data loaded from the JSON file.
    """

    def __init__(self, file_path: str):
        """
        Initializes the LoadDataDAO with a specified path to the JSON data file.

        Parameters:
            file_path (str): The path to the JSON file.
        """
        self.file_path = file_path
        self.data = None
        self.load_data()

    def load_data(self):
        """
        Loads the data from the JSON file specified by the file_path attribute.

        Raises:
            FileNotFoundError: If the JSON file cannot be found at the specified path.
            json.JSONDecodeError: If the file is not a valid JSON file.
        """
        try:
            with open(self.file_path, 'r') as user_file:
                self.data = json.load(user_file)
        except FileNotFoundError as e:
            print(f"Error: The file was not found at the specified path: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: The file is not a valid JSON file: {e}")
            raise

    def replace_ids_with_names(self):
        """
        Replaces the IDs in the 'asset_energy_system', 'asset_energy_demand', and
        'asset_energy_output' with their corresponding names from 'asset', 'energy_system',
        and 'energy_type' for better readability of the data.
        """
        if not self.data:
            raise ValueError("No data available to replace IDs with names.")

        # Create mappings for asset, energy system, and energy type names
        asset_names = {asset['id']: asset['name'] for asset in self.data.get('asset', [])}
        energy_system_names = {es['id']: es['name'] for es in self.data.get('energy_system', [])}
        energy_type_names = {et['id']: et['name'] for et in self.data.get('energy_type', [])}

        # Check if the mappings have been created successfully
        if not asset_names or not energy_system_names or not energy_type_names:
            raise ValueError("One or more mappings are empty, check the integrity of the input data.")

        # Replace IDs with names using the pre-built mappings
        for asset_energy_system in self.data.get('asset_energy_system', []):
            asset_id = asset_energy_system.get('asset')
            es_id = asset_energy_system.get('energy_system')
            et_id = asset_energy_system.get('energy_type')
            # If any of the IDs is None, it indicates an issue with the data.
            if asset_id is None or es_id is None or et_id is None:
                logging.warning(f"Skipping entry due to missing data: {asset_energy_system}")
                continue

            asset_energy_system['asset'] = asset_names.get(asset_id, "Unknown Asset")
            asset_energy_system['energy_system'] = energy_system_names.get(es_id, "Unknown Energy System")
            asset_energy_system['energy_type'] = energy_type_names.get(et_id, "Unknown Energy Type")

        # Process 'asset_energy_demand'
        energy_demand_dict = {}
        for item in self.data.get('asset_energy_demand', []):
            asset_id = item.get('asset')
            et_id = item.get('energy_type')
            demand = item.get('energy_demand')

            # Skip entries with missing data
            if asset_id is None or et_id is None or demand is None:
                logging.warning(f"Skipping entry due to missing data: {item}")
                continue

            asset_name = asset_names.get(asset_id, "Unknown Asset")
            energy_type = energy_type_names.get(et_id, "Unknown Energy Type")

            # Initialize the asset entry if not already present
            if asset_name not in energy_demand_dict:
                energy_demand_dict[asset_name] = {}

            energy_demand_dict[asset_name][energy_type] = demand

        self.data['asset_energy_demand'] = energy_demand_dict

        # Process 'asset_energy_output'
        energy_output_dict = {}
        for item in self.data.get('asset_energy_output', []):
            asset_id = item.get('asset')
            output = item.get('energy_output')

            # Skip entries with missing data
            if asset_id is None or output is None:
                logging.warning(f"Skipping entry due to missing data: {item}")
                continue  # Optionally, log this issue or raise an error

            asset_name = asset_names.get(asset_id, "Unknown Asset")
            energy_output_dict[asset_name] = output

        self.data['asset_energy_output'] = energy_output_dict

    def get_asset_name(self, asset_id) -> str:
        """
        Retrieve the asset name for a given asset ID.

        Parameters:
            asset_id (int): The unique identifier for the asset.

        Returns:
            str: The name of the asset corresponding to the given ID.
        """
        asset_names = {asset['id']: asset['name'] for asset in self.data['asset']}
        return asset_names.get(asset_id)

    def get_energy_system_name(self, es_id) -> str:
        """
        Retrieve the energy system name for a given energy system ID.

        Parameters:
            es_id (int): The unique identifier for the energy system.

        Returns:
            str: The name of the energy system corresponding to the given ID.
        """
        energy_system_names = {es['id']: es['name'] for es in self.data['energy_system']}
        return energy_system_names.get(es_id)

    def get_energy_type_name(self, et_id) -> str:
        """
        Retrieve the energy type name for a given energy type ID.

        Parameters:
            et_id (int): The unique identifier for the energy type.

        Returns:
            str: The name of the energy type corresponding to the given ID.
        """
        energy_type_names = {et['id']: et['name'] for et in self.data['energy_type']}
        return energy_type_names.get(et_id)


dao = LoadDataDAO("/Users/alessandrodiamanti/Downloads/json_database.json")
dao.replace_ids_with_names()

processor = EnergyProcessor(dao)
energy_demand_summary = processor.energy_demand_summary
energy_reduction = processor.get_reduced_energy_demand

