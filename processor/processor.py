from collections import OrderedDict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnergyProcessor:
    def __init__(self, dao):
        self.dao = dao
        self.energy_demand_summary = None
        self.calculate_energy_demand_per_electricity()
        self.get_reduced_energy_demand()

    def calculate_energy_demand_per_electricity(self):
        """
        Calculate the energy demand for each asset, distinguishing between electricity and non-electricity sources.
        """
        self.energy_demand_summary = {asset['name']: {'electricity': 0, 'non-electricity': 0} for asset in self.dao.data.get('asset', [])}

        # Processing energy demand data.
        for entry in self.dao.data.get('asset_energy_system', []):
            try:
                asset_name = entry.get('asset')
                energy_type = entry.get('energy_type')
                energy_system = entry.get('energy_system')

                # Check for missing data and log it.
                if None in (asset_name, energy_type, energy_system):
                    logging.warning(f"Missing data for entry: {entry}")
                    continue

                # Aggregate energy demands.
                demand = self.dao.data['asset_energy_demand'].get(asset_name, {}).get(energy_type, 0)
                if not isinstance(demand, int):
                    logging.error(f"Invalid demand value: {demand} for asset: {asset_name}")
                    continue

                if energy_system == 'electricity':
                    self.energy_demand_summary[asset_name]['electricity'] += demand
                else:
                    self.energy_demand_summary[asset_name]['non-electricity'] += demand
            except Exception as e:
                logging.exception(f"Error processing energy demand for {entry}: {e}")
                continue

    def get_reduced_energy_demand(self):
        """
        Calculate the reduced energy demand for each asset after accounting for energy output.
        """
        self.energy_demand_summary_taken_out_reduced_cost = {}

        # Calculating reduced energy demand.
        for asset_name, demands in self.energy_demand_summary.items():
            output = self.dao.data['asset_energy_output'].get(asset_name, 0)

            # Ensuring we don't end up with negative demand.
            electricity_demand_after_output = max(demands['electricity'] - output, 0)
            self.energy_demand_summary_taken_out_reduced_cost[asset_name] = electricity_demand_after_output + demands[
                'non-electricity']

    def calculate_energy_demand(self, name: str) -> OrderedDict:
        """
        Calculate the energy demand and output reduction for a given asset by name.

        Parameters:
            name (str): The name of the asset to calculate demand for.

        Returns:
            OrderedDict: An ordered dictionary containing the calculated energy data.

        Raises:
            ValueError: If the total energy demand is 0, indicating no energy consumption data is available.
        """
        asset_demands = self.dao.data['asset_energy_demand'].get(name)
        if not asset_demands:
            logging.warning(f"No energy demand data found for asset: {name}")
            return OrderedDict()

        total_energy_demand = sum(asset_demands.values())
        if total_energy_demand == 0:
            logging.error(f"Total energy demand for asset '{name}' is 0")
            raise ValueError(f"Total energy demand for asset '{name}' cannot be 0")

        energy_output_reduction = self.dao.data['asset_energy_output'].get(name, 0)

        reduction_percentage = (energy_output_reduction / total_energy_demand * 100)

        response = OrderedDict([
            ("name", name),
            ("energy_types", asset_demands),
            ("total_energy_demand", total_energy_demand),
            ("energy_output_reduction", reduction_percentage)
        ])

        return response