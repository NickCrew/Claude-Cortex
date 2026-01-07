# Multi-File Output System

## Overview
This system enables Claude to deliver multiple files in a single JSON payload. The JSON is processed by a bash script that writes all files in parallel with stylized output.

## How to Use
When the user needs multiple files generated as a single output, follow these instructions:

1. Understand the user's request for multiple files
2. Format your response as a valid JSON object following the schema below
3. Inform the user they can save this output to a file and process it with the write_files.sh script

## JSON Schema for Multi-File Output

```json
{
  "files": [
    {
      "file_name": "path/to/file1.extension",
      "file_type": "text",
      "file_content": "The content of the first file"
    },
    {
      "file_name": "path/to/file2.extension",
      "file_type": "text",
      "file_content": "The content of the second file"
    },
    {
      "file_name": "path/to/binary_file.bin",
      "file_type": "binary",
      "file_content": "base64_encoded_content_here"
    }
  ]
}
```

## Field Definitions
- `file_name`: The path where the file should be written (including filename and extension)
  - IMPORTANT: Always use project-relative paths (e.g., "src/main/java/...") or absolute paths
  - Files will be written to exactly the location specified - no test directories are used
  - For tool creation, always use actual project paths, not test directories
- `file_type`: Either "text" (default) or "binary" for base64-encoded content
- `file_content`: The actual content of the file (base64 encoded for binary files)

## Important Rules
1. ALWAYS validate the JSON before providing it to ensure it's properly formatted
2. ALWAYS ensure all file paths are properly escaped
3. For binary files, encode the content as base64 and specify "binary" as the file_type
4. NEVER include explanatory text or markdown outside the JSON structure
5. When asked to generate multiple files, ALWAYS use this format unless explicitly directed otherwise

## How Users Can Process the Output
Instruct users to:
1. Save the JSON output to a file (e.g., `files.json`)
2. Run the write_files.sh script:
   ```bash
   ./write_files.sh files.json
   ```

## Script Features
The write_files.sh script includes the following enhancements:
- Stylized output with color-coded and emoji status indicators
- Compact progress display with timestamp and elapsed time
- Green circle (🟢) for success items  
- White circle (⚪) for neutral items
- Red circle (🔴) for error conditions
- Calendar emoji (📅) for timestamps
- Clock emoji (⏱️) for elapsed time display
- Support for both text and binary files
- Parallel extraction for improved performance
- Detailed error reporting and logging options
- Verbose mode for detailed progress tracking

## Advanced Usage Options
```bash
# Basic usage
./write_files.sh files.json

# Verbose output with detailed progress
./write_files.sh files.json --verbose

# Log details to a file for debugging
./write_files.sh files.json --log-to-file logs/extraction.log

# Write results to a file (silent mode)
./write_files.sh files.json --output-file results.md

# Suppress all console output
./write_files.sh files.json --silent

# Disable compact output format
./write_files.sh files.json --no-compact
```

## Example Response
When asked to generate multiple files, your entire response should be a valid JSON object like this:

```json
{
  "files": [
    {
      "file_name": "example.py",
      "file_type": "text",
      "file_content": "def hello_world():\n    print(\"Hello, world!\")\n\nif __name__ == \"__main__\":\n    hello_world()"
    },
    {
      "file_name": "README.md",
      "file_type": "text",
      "file_content": "# Example Project\n\nThis is an example README file."
    }
  ]
}
```

## Command to Add to CLAUDE.md
To add this system to CLAUDE.md, add the following section:

```markdown
## Multi-File Output System
- When the user mentions "multi-file output", "generate files as json", or similar requests for bundled file generation, use the multi-file output system
- Execute using: `./write_files.sh <json_file>`
- Provide output as a single JSON object following the schema in `./multi_file_instructions.md`
- The JSON must include an array of files, each with file_name, file_type, and file_content fields
- For binary files, encode content as base64 and set file_type to "binary"
- NEVER include explanatory text or markdown outside the JSON structure
```
