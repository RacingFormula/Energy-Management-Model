import numpy as np
import matplotlib.pyplot as plt

class EnergyManagementModel:
    def __init__(self, config):
        self.battery_capacity = config.get("battery_capacity", 54)  # kWh
        self.energy_consumption_rate = config.get("energy_consumption_rate", 2)  # kWh per lap
        self.regeneration_rate = config.get("regeneration_rate", 0.3)  # kWh per lap
        self.race_distance = config.get("race_distance", 45)  # laps
        self.base_lap_time = config.get("base_lap_time", 75)  # seconds
        self.energy_penalty_per_kWh = config.get("energy_penalty_per_kWh", 0.5)  # seconds per kWh
        self.weather_factor = config.get("weather_factor", 1.0)  # Multiplier for energy consumption

    def simulate_strategy(self, target_speeds):
        remaining_energy = self.battery_capacity
        total_time = 0
        lap_times = []
        energy_usage = []

        for lap, speed in enumerate(target_speeds, start=1):
            # Calculate energy usage with speed adjustments
            energy_used = self.energy_consumption_rate * self.weather_factor * (1 + speed / 100)
            energy_regenerated = self.regeneration_rate * (1 - speed / 100)

            remaining_energy -= energy_used
            remaining_energy += energy_regenerated
            remaining_energy = max(0, remaining_energy)  # Clamp at 0

            # Calculate lap time impact
            lap_time = self.base_lap_time + (self.battery_capacity - remaining_energy) * self.energy_penalty_per_kWh
            lap_time *= (1 - speed / 200)  # Adjust lap time based on speed
            total_time += lap_time

            lap_times.append(lap_time)
            energy_usage.append(remaining_energy)

        return {
            "lap_times": lap_times,
            "energy_usage": energy_usage,
            "total_time": total_time
        }

    def optimise_strategy(self):
        best_strategy = None
        best_time = float("inf")
        strategies = []

        # Generate target speed profiles for optimisation
        for base_speed in np.linspace(-10, 10, 5):  # Speeds as deviations from the baseline
            target_speeds = [base_speed + np.sin(lap / 5) * 5 for lap in range(self.race_distance)]
            print(f"Simulating strategy with base speed adjustment: {base_speed} km/h")
            strategy = self.simulate_strategy(target_speeds)

            if strategy["total_time"] < best_time:
                best_time = strategy["total_time"]
                best_strategy = {
                    "target_speeds": target_speeds,
                    "lap_times": strategy["lap_times"],
                    "energy_usage": strategy["energy_usage"],
                    "total_time": strategy["total_time"]
                }

            strategies.append({
                "base_speed": base_speed,
                "lap_times": strategy["lap_times"],
                "energy_usage": strategy["energy_usage"],
                "total_time": strategy["total_time"]
            })

        return best_strategy, strategies

    def plot_results(self, best_strategy, strategies):
        laps = range(1, self.race_distance + 1)

        plt.figure(figsize=(16, 10))

        # Plot energy usage for best strategy
        plt.subplot(3, 1, 1)
        plt.plot(laps, best_strategy["energy_usage"], label="Best Strategy Energy Usage", color="green")
        plt.title("Energy Usage Over Race Distance")
        plt.xlabel("Lap")
        plt.ylabel("Remaining Energy (kWh)")
        plt.legend()
        plt.grid(True)

        # Plot lap times for best strategy
        plt.subplot(3, 1, 2)
        plt.plot(laps, best_strategy["lap_times"], label="Best Strategy Lap Times", color="blue")
        plt.title("Lap Times Over Race Distance")
        plt.xlabel("Lap")
        plt.ylabel("Lap Time (s)")
        plt.legend()
        plt.grid(True)

        # Plot total race times for all strategies
        plt.subplot(3, 1, 3)
        total_times = [strategy["total_time"] for strategy in strategies]
        labels = [f"{strategy['base_speed']} km/h" for strategy in strategies]
        plt.bar(labels, total_times, color="skyblue")
        plt.title("Total Race Time for Each Strategy")
        plt.xlabel("Strategy (Base Speed Adjustment)")
        plt.ylabel("Total Time (s)")
        plt.grid(True)

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    config = {
        "battery_capacity": 54,
        "energy_consumption_rate": 2,
        "regeneration_rate": 0.3,
        "race_distance": 45,
        "base_lap_time": 75,
        "energy_penalty_per_kWh": 0.5,
        "weather_factor": 1.0
    }

    model = EnergyManagementModel(config)
    best_strategy, strategies = model.optimise_strategy()
    model.plot_results(best_strategy, strategies)