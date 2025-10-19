# 🏈 NFL Matchup Analyzer

A Python-based NFL analytics tool that tracks strength-vs-weakness matchups and identifies defensive positional weaknesses using real-time NFL data.

## Features

- **Defense Positional Weaknesses**: Identify which NFL defenses are most vulnerable to specific positions (QB, RB, WR, TE)
- **Matchup Analysis**: Find favorable matchups by comparing top players against weak defenses
- **Touchdown Tracking**: Track season-long TD leaders across all positions
- **Interactive Web App**: Built with Streamlit for easy data exploration
- **Real-time Data**: Powered by nflreadpy for up-to-date NFL statistics

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

**Run the Web App:**
```bash
streamlit run app.py
```

**Run the Analysis Script:**
```bash
python analysis.py
```

## Web App Features

### 🛡️ Defense Weaknesses Tab
- Filter by position (QB, RB, WR, TE)
- View worst and best defenses against each position
- Interactive charts showing TDs allowed

### 🔥 Matchup Analysis Tab
- Week-by-week game breakdowns
- Identifies favorable offensive matchups
- Highlights strength-vs-weakness opportunities

### 🏆 TD Leaders Tab
- Season touchdown leaders by position
- Rushing, receiving, and passing TD stats
- Team affiliations

## Data Source

This project uses [nflreadpy](https://github.com/nflverse/nflreadpy), a Python package for accessing NFL data from the [nflverse](https://github.com/nflverse) ecosystem.

## License

This project is licensed under the MIT License.
```

---

## **FILE 6: LICENSE**
Create a file called `LICENSE` and paste this:
```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
