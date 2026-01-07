# TCD Technical Scorecard

A Streamlit app to view, sort, filter, and export student scores from the TCD Technical training program.

## Features

- 📊 **Interactive Dashboard** - View all student scores with sorting and filtering
- 🔍 **Search** - Find students by name or roll number
- 📈 **Sorting** - Sort by any column (Rank, Name, Roll No, Pseudocode, Coding, Daily Test, Total)
- 📉 **Filtering** - Filter by minimum total score
- 📥 **CSV Export** - Download filtered or complete data as CSV
- 📊 **Statistics** - View mean, median, max, min for each score category

## Quick Start

### Option 1: Run the batch file (Recommended)

Simply double-click `run.bat` or run it from command prompt:

```cmd
cd c:\ct3-results\app
run.bat
```

This will automatically:
1. Create a virtual environment (if not exists)
2. Install dependencies
3. Start the Streamlit app

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```cmd
   cd c:\ct3-results\app
   python -m venv venv
   ```

2. **Activate virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```cmd
   streamlit run app.py
   ```

5. **Open in browser:** http://localhost:8501

## Files

| File | Description |
|------|-------------|
| `app.py` | Main Streamlit application |
| `parser.py` | HTML parser module that extracts JSON data |
| `requirements.txt` | Python dependencies |
| `run.bat` | Windows batch file for easy setup and run |

## Data Source

The app reads data from:
- `TCD_Technical_GITAM_20 Dec 2025 to 6 Jan 2026.HTML` (in parent directory)

## Output CSV Format

The exported CSV contains these columns:
- **Rank** - Student rank based on total score
- **Name** - Student name
- **RollNo** - Student roll number
- **OverallPseudocode** - Pseudocode test score
- **OverallCoding** - Coding test score
- **OverallDailyTest** - Daily test score
- **Total** - Sum of all three scores
