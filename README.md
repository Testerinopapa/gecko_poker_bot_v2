# Gecko Poker Bot v2

A sophisticated poker bot implementation using Python, featuring advanced decision-making algorithms and comprehensive game analysis.

## Project Structure

```
gecko_poker_bot_v2/
├── src/
│   ├── core/
│   │   ├── gecko_bot.py         # Main bot logic
│   │   ├── game_runner.py       # Game simulation engine
│   │   ├── hand_evaluator.py    # Hand strength evaluation
│   │   ├── poker_enums.py       # Poker-related enumerations
│   │   ├── board_analyzer.py    # Board texture analysis
│   │   ├── position_manager.py  # Position-based strategy
│   │   └── table_state.py      # Game state management
│   └── visualization/
│       └── match_visualizer.py  # Results visualization
├── tests/                      # Test files
├── assets/                     # Generated visualizations
├── docs/                       # Documentation
├── requirements.txt           # Project dependencies
├── README.md                 # Project documentation
└── main.py                   # Entry point
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gecko_poker_bot_v2.git
cd gecko_poker_bot_v2
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run a simulation:
```bash
python main.py
```

This will:
1. Initialize the bot
2. Run a 10-round simulation
3. Generate visualization dashboards in the assets directory

## Features

- Advanced poker strategy implementation
- Comprehensive hand evaluation
- Position-based decision making
- Board texture analysis
- Detailed match visualization and analysis
- Simulation capabilities

## License

[Your chosen license]

## Contributing

[Your contribution guidelines] 