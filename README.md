# Meeting Scripts

A tool for generating structured scripts from meeting notes using OpenAI's API.

## Features
- Process plain text meeting notes
- Generate structured scripts with action items and next steps
- Support for different script types (action items, meeting summaries, minutes)
- Easy command-line interface
- Secure API key management

## Setup

1. Clone this repository
   ```bash
   git clone https://github.com/ttreed/meeting_scripts.git
   cd meeting_scripts
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment
   - Copy `.env.example` to `.env`
   - Add your Windsurf API key to the `.env` file

## Usage

### Basic Usage

```bash
python meeting_script_generator.py path/to/meeting_notes.txt -o output_script.md
```

### Command Line Options

- `input_file`: Path to the text file containing meeting notes (required)
- `-o, --output`: Output file path (default: 'output_script.txt')
- `--api-key`: Windsurf API key (optional if set in .env)
- `--script-type`: Type of script to generate: 'action_items', 'summary', or 'minutes' (default: 'action_items')

### Example

```bash
# Generate action items from sample meeting notes
python meeting_script_generator.py examples/sample_meeting_notes.txt -o meeting_actions.md

# Generate meeting summary
python meeting_script_generator.py examples/sample_meeting_notes.txt --script-type summary -o meeting_summary.md
```

## Example Input/Output

### Input (sample_meeting_notes.txt)
```
Team Sync Meeting - June 12, 2025

Attendees: Alice, Bob, Charlie, David

Agenda:
1. Project Updates
2. Action Items Review
3. Upcoming Deadlines

Notes:
- Alice reported that the frontend team has completed the new dashboard UI
- Bob mentioned API performance issues that need investigation
- Charlie will look into the database query optimization
- David suggested implementing caching for frequently accessed data
```

### Output (action_items.md)
```markdown
# Action Items from Team Sync Meeting - June 12, 2025

## Action Items
- [ ] **Alice**: Share the new dashboard design with the team by EOD tomorrow
- [ ] **Bob**: Investigate API performance issues and report findings by Friday
- [ ] **Charlie**: Optimize slow database queries by next week
- [ ] **David**: Research caching solutions and present options in the next meeting

## Follow-up
Next Meeting: June 19, 2025, 10:00 AM
```

