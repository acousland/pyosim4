# Pyosim4

**Pyosim4** is a Python-based simulation framework that models the behaviour and evolution of a population of individuals in a 2D grid environment. The simulation uses neural networks to control the actions of individuals based on sensor inputs and visualises the population dynamics over multiple generations.

## Features

- **Neural Network Control**: Each individual is controlled by a neural network that processes sensor inputs and generates actions.
- **Evolutionary Algorithm**: The population evolves over generations through mutation and selection based on survival.
- **Visualisation**: The simulation includes a real-time visualisation of the population and signal layers using Matplotlib.
- **Customisable Parameters**: Simulation parameters such as population size, mutation rate, and steps per generation can be customised.

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

To run the simulation, execute the following command:

```bash
python simulation.py
```

## Simulation Parameters

The simulation parameters can be customised by modifying the `Parameters` class in `simulation.py` or by providing a configuration file. The available parameters are:

- `size_x`: Width of the simulation grid.
- `size_y`: Height of the simulation grid.
- `population`: Number of individuals in the population.
- `steps_per_generation`: Number of steps per generation.
- `mutation_rate`: Mutation rate for the evolutionary algorithm.
- `survivor_fraction`: Fraction of the population that survives to the next generation.
- `visualise_interval`: Interval at which the simulation is visualised.

## Visualisation

The simulation includes a real-time visualisation of the population and signal layers. The individuals are represented by dark red or orange points on a white background, and the signal layer is visualised using the `'hot'` colormap.

## Example

Here is an example of how to run the simulation with a custom configuration file:

```bash
python simulation.py --config config.json
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project uses the following libraries:

- [Matplotlib](https://matplotlib.org/): For visualisation.
- [NumPy](https://numpy.org/): For numerical operations.

## Contact

For any questions or enquiries, please contact: [acousland@gmail.com](mailto:acousland@gmail.com)

---

*Feel free to customise this README further based on your specific requirements and preferences.*
