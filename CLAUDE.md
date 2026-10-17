# MazeMaster

## Overview
[Describe what this project does]

## Maze Generation Rules
1. All mazes have black walls and white paths
2. Two black pixels touching by only a corner are impassible
3. The outer perimiter of the maze must be black except for 2 endpoints
4. Start and end are ambiguous
5. Mazes must be saved as png files with indexed colors
6. Maze dimensions and colors must not be hard coded

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Project Structure
```
MazeMaster/
├── src/                # Application source code
│   └── __init__.py
├── tests/              # Test suite
│   └── __init__.py
├── .venv/              # Virtual environment (not tracked by git)
├── .gitignore
├── CLAUDE.md
└── requirements.txt
```

## Running Tests
```bash
python -m pytest tests/
```

## Development Notes
- [Add architectural decisions, gotchas, or guidelines here]
