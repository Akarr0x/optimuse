from collections import OrderedDict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnergyProcessor:
    def __init__(self, dao):
        self.dao = dao
        self.energy_demand_summary = None
        self.calculate_energy_demand_per_electricity()
        self.get_reduced_energy_demand()

    def distribute_reduction_with_excess_handling(self, asset_name, electricity_demand, output) -> dict:
        """
        Distributes the reduction in electricity demand equally among all components,
        taking into account the output of the building.
        If the reduction for a component exceeds its demand, the excess is redistributed

        Parameters:
        - asset_name (str): The name of the asset for which the reduction is being calculated.
        - electricity_demand (dict): A dictionary where keys are the component names and values are their respective demands.
        - output (float): The total output of the building to be distributed as a reduction in electricity demand.

        Returns:
        - dict: A dictionary with the same structure as electricity_demand, but with adjusted demands post-reduction.
        """
        components = list(electricity_demand.keys())
        total_electricity_demand = sum(electricity_demand.values())
        total_reduction = min(output, total_electricity_demand)
        excess_reduction = 0
        reduction_applied = False

        while total_reduction > 0 and components:
            initial_reduction_per_component = (total_reduction + excess_reduction) / len(components) if components else 0
            excess_reduction = 0

            for component in components[:]:
                component_demand = electricity_demand[component]
                if component_demand <= initial_reduction_per_component:
                    # If component demand is less than or equal to the reduction, adjust excess and component demand
                    excess_reduction += initial_reduction_per_component - component_demand
                    total_reduction -= component_demand
                    electricity_demand[component] = 0
                    components.remove(component)
                else:
                    # Reduce component demand and adjust total reduction accordingly
                    electricity_demand[component] -= initial_reduction_per_component
                    total_reduction -= initial_reduction_per_component
                    reduction_applied = True

            if not reduction_applied:
                break
            reduction_applied = False

            # Reallocate excess reduction to remaining components
            total_reduction += excess_reduction

        return electricity_demand

    def calculate_energy_demand_per_electricity(self):
        """
        Calculates the energy demand per each asset.
        Divides the energy demand in "electricity" and "non-electricity" for better understanding
        """
        self.energy_demand_details = {}

        self.energy_demand_summary = {
            asset['name']: {'electricity': {}, 'non-electricity': 0}
            for asset in self.dao.data.get('asset', [])
        }
        for entry in self.dao.data.get('asset_energy_system', []):
            try:
                asset_name = entry.get('asset')
                energy_type = entry.get('energy_type')
                energy_system = entry.get('energy_system')

                if None in (asset_name, energy_type, energy_system):
                    logging.warning(f"Missing data for entry: {entry}")
                    continue

                # Aggregate energy demands.
                demand = self.dao.data['asset_energy_demand'].get(asset_name, {}).get(energy_type, 0)
                if not isinstance(demand, int):
                    logging.error(f"Invalid demand value: {demand} for asset: {asset_name}")
                    continue
                key = (asset_name, energy_type)
                if asset_name not in self.energy_demand_details:
                    self.energy_demand_details[asset_name] = {}
                self.energy_demand_details[asset_name][energy_type] = self.energy_demand_details[asset_name].get(
                    energy_type, 0) + demand

                # Electricity is a dictionary for easier handling
                if energy_system == 'electricity':
                    if energy_type not in self.energy_demand_summary[asset_name]['electricity']:
                        self.energy_demand_summary[asset_name]['electricity'][energy_type] = 0
                    self.energy_demand_summary[asset_name]['electricity'][energy_type] += demand
                else:
                    self.energy_demand_summary[asset_name]['non-electricity'] += demand
            except Exception as e:
                logging.exception(f"Error processing energy demand for {entry}: {e}")
                continue

    def get_reduced_energy_demand(self):
        """
        Calculates the reduced energy demand taking into consideration only the electricity variable.
        If less than 0 just gives 0 as result
        """
        self.energy_demand_summary_taken_out_reduced_cost = {}

        for asset_name, demands in self.energy_demand_summary.items():
            output = self.dao.data['asset_energy_output'].get(asset_name, 0)
            reduced_electricity_demand_components = self.distribute_reduction_with_excess_handling(
                asset_name, demands['electricity'], output)

            total_reduced_electricity_demand = sum(reduced_electricity_demand_components.values())

            self.energy_demand_summary_taken_out_reduced_cost[asset_name] = {
                'electricity': reduced_electricity_demand_components,
                'non-electricity': demands['non-electricity']
            }

    def merge_demands(self, asset_name, original_demands):
        """
        Merges the original demands with the reduced demands for electricity components,
        ensuring reduced values are used for electricity-related energy types
        """
        reduced_demands = self.energy_demand_summary_taken_out_reduced_cost.get(asset_name, {})

        merged = {}

        for energy_type, demand in original_demands.items():
            if 'electricity' in reduced_demands and energy_type in reduced_demands['electricity']:
                merged[energy_type] = reduced_demands['electricity'][energy_type]
            else:
                merged[energy_type] = demand

        return merged

    def calculate_energy_demand(self, name: str) -> OrderedDict:
        """
        Calculates the percentage of energy reduction,
        this is calculated by dividing the energy output by the total demand needed

        Parameters:
            name (str): The name of the asset to calculate

        Returns:
            OrderedDict: An ordered dictionary containing the calculated energy data.
        """
        original_demands_for_asset = self.energy_demand_details.get(name, {})
        merged_demands = self.merge_demands(name, original_demands_for_asset)
        total_energy_demand = sum(value for value in merged_demands.values() if isinstance(value, (int, float)))
        if total_energy_demand == 0:
            logging.error(f"Total energy demand for asset '{name}' is 0")
            raise ValueError(f"Total energy demand for asset '{name}' cannot be 0")

        """
        The electricity demand may be reduced by the asset's output, but if the output exceeds the electricity demand, 
        we select the lower of the two values. 
        This assumes that if the output energy is greater than the electricity demand, 
        there is no alternative use for the surplus (such as selling it).
        """

        initial_total_demand = sum(self.energy_demand_details[name].values())
        reduced_electricity_demand = sum(self.energy_demand_summary[name]['electricity'].values())
        non_electricity_demand = self.energy_demand_summary[name]['non-electricity']
        reduced_total_demand = reduced_electricity_demand + non_electricity_demand

        # Calculate the reduction percentage
        reduction_amount = initial_total_demand - reduced_total_demand
        energy_output_reduction_percentage = (reduction_amount / initial_total_demand) * 100 if initial_total_demand > 0 else 0

        response = OrderedDict([
            ("name", name),
            ("energy_types", merged_demands),
            ("total_energy_demand", total_energy_demand),
            ("energy_output_reduction", energy_output_reduction_percentage)
        ])

        return response
