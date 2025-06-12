#!/usr/bin/env python3
"""
Meeting Script Generator

This script processes meeting notes from a text file and generates structured
scripts using a local language model.
"""

import os
import argparse
import json
import sys
from typing import Dict, Optional
from bardapi import Bard
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MeetingScriptGenerator:
    def __init__(self, api_key: Optional[str] = None, model: str = "bard"):
        """Initialize the MeetingScriptGenerator with Bard API.
        
        Args:
            api_key: Bard API key (optional, will use BARD_API_KEY from .env if not provided)
            model: For compatibility, not used with Bard
        """
        self.api_key = api_key or os.getenv("BARD_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Bard API key not provided. Set BARD_API_KEY in .env file or pass as argument"
            )
        
        # Initialize Bard with the API key
        self.bard = Bard(token=self.api_key)
        self.model = "Bard"
    


    def read_meeting_notes(self, file_path: str) -> str:
        """Read meeting notes from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Meeting notes file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading meeting notes: {str(e)}")

    def _validate_python_code(self, code: str) -> str:
        """
        Validate and clean the generated Python code.
        
        Args:
            code: The generated Python code
            
        Returns:
            str: Validated and cleaned Python code
        """
        # Remove any markdown code blocks
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].strip()
            
        # Remove any leading/trailing whitespace
        code = code.strip()
        
        # Ensure it starts with a shebang if it's a script
        if not code.startswith("#!"):
            code = "#!/usr/bin/env python3\n\n" + code
            
        # Basic syntax check
        try:
            compile(code, "<string>", "exec")
            return code
        except SyntaxError as e:
            # Try to fix common indentation issues
            try:
                import re
                # Fix inconsistent indentation
                lines = code.split('\n')
                fixed_lines = []
                for line in lines:
                    # Remove any leading spaces that aren't multiples of 4
                    fixed_line = re.sub(r'^\s+', lambda m: ' ' * (len(m.group(0)) // 4 * 4), line)
                    fixed_lines.append(fixed_line)
                fixed_code = '\n'.join(fixed_lines)
                compile(fixed_code, "<string>", "exec")
                return fixed_code
            except:
                # If we can't fix it, return the original with an error comment
                return f"""#!/usr/bin/env python3
# WARNING: Generated code contains syntax errors
# Please review and fix the following code:

{code}
"""

    def _extract_code_from_response(self, response_text: str) -> str:
        """Extract code block from the model's response."""
        if '```python' in response_text:
            return response_text.split('```python')[1].split('```')[0].strip()
        elif '```' in response_text:
            return response_text.split('```')[1].strip()
        return response_text.strip()

    def generate_script(self, meeting_notes: str, script_type: str = "script") -> Dict:
        """
        Generate a Python script based on meeting notes using Bard API.
        
        Args:
            meeting_notes (str): The content of the meeting notes
            script_type (str): Type of script to generate ('script', 'module', or 'class')
            
        Returns:
            dict: Response containing the generated Python script
        """
        prompt = """You are an expert Python developer. Your task is to create a complete, 
functional Python script based on the provided requirements. Follow these guidelines:

1. Generate ONLY the Python code - no explanations, markdown, or additional text
2. Start with '#!/usr/bin/env python3' shebang
3. Include all necessary imports at the top
4. Implement the functionality described in the meeting notes
5. Add clear docstrings and comments
6. Include proper error handling with try/except blocks
7. Follow PEP 8 style guide strictly
8. Make sure the code is self-contained and can run independently
9. Include 'if __name__ == "__main__":' block if appropriate
10. Add type hints for function parameters and return values
11. Include example usage in docstrings
12. Add input validation where appropriate

Here are the meeting notes to base the script on:
"""

        try:
            # Send the prompt to Bard
            response = self.bard.get_answer(
                f"{prompt}\n\n{meeting_notes}"
            )
            
            if response and 'content' in response:
                code = self._extract_code_from_response(response['content'])
                
                # Add a header with generation info
                from datetime import datetime
                header = f"""#!/usr/bin/env python3
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Model: {self.model}
# Source: Meeting notes

"""
                
                return {"script": header + code}
            else:
                raise Exception("No response generated from the model")
                
        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")

    def save_script(self, script_data: Dict, output_path: str) -> None:
        """Save the generated script to a file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as file:
                if 'script' in script_data:
                    file.write(script_data['script'])
                else:
                    json.dump(script_data, file, indent=2)
            print(f"Script successfully saved to: {output_path}")
        except Exception as e:
            raise Exception(f"Error saving script: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Generate Python scripts from meeting notes using Google\'s Bard API')
    parser.add_argument('input_file', help='Path to the input text file with meeting notes')
    parser.add_argument('-o', '--output', default=None,
                      help='Output file path for the generated script (default: generated_script_<timestamp>.py)')
    
    # Bard API options
    parser.add_argument('--api-key', default=None, help='Bard API key (default: use BARD_API_KEY from .env)')
    
    # Script options
    parser.add_argument('--script-type', default='script',
                      choices=['script', 'module', 'class'],
                      help='Type of Python code to generate (script, module, or class)')
    
    # Output directory from .env or default to current directory
    output_dir = os.getenv('OUTPUT_DIR', 'output_scripts')
    
    args = parser.parse_args()
    
    try:
        # Initialize the generator
        print("Using Google's Bard API")
        generator = MeetingScriptGenerator(api_key=args.api_key)
        
        # Read meeting notes
        print(f"Reading meeting notes from: {args.input_file}")
        meeting_notes = generator.read_meeting_notes(args.input_file)
        
        # Generate script
        print("Generating script... (this may take a moment)")
        script_data = generator.generate_script(meeting_notes, args.script_type)
        
        # Determine output path
        if not args.output:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"generated_script_{timestamp}.py"
            os.makedirs(output_dir, exist_ok=True)
            args.output = os.path.join(output_dir, output_filename)
        
        # Save the generated script
        generator.save_script(script_data, args.output)
        
        print("\nScript generation completed successfully!")
        print(f"Script saved to: {os.path.abspath(args.output)}")
        
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        print("\nMake sure you have:"
              "\n1. Set the BARD_API_KEY environment variable"
              "\n2. Installed the required packages: pip install -r requirements.txt"
              "\n3. Have a stable internet connection"
              "\n\nTo get a Bard API key:"
              "\n1. Go to https://bard.google.com/"
              "\n2. Sign in with your Google account"
              "\n3. Open browser developer tools (F12)"
              "\n4. Go to Application > Cookies"
              "\n5. Find the cookie named '__Secure-1PSID'"
              "\n6. Copy its value and set it as BARD_API_KEY"
              "\n   in your environment: export BARD_API_KEY='your-key-here'"
              "\n   or in a .env file: BARD_API_KEY=your-key-here",
              file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    main()
