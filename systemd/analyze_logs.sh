#!/bin/bash

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if log file exists
if [ ! -f "../scraper.log" ]; then
    echo -e "${RED}Error: scraper.log file not found${NC}"
    exit 1
fi

echo -e "\n${BLUE}=== Log Analysis Report ===${NC}\n"

# Function to count and sort messages by type and code
analyze_logs() {
    local log_file="../scraper.log"
    
    # Count ERROR messages
    echo -e "${RED}=== ERROR Messages ===${NC}"
    grep -o "\[ERROR:[0-9]\{3\}\]" "$log_file" | sort | uniq -c | sort -k2 | while read count code; do
        code_num=$(echo "$code" | grep -o "[0-9]\{3\}")
        message=$(PYTHONPATH="../" python3 -c "from log_codes import get_message; print(get_message('ERROR', '$code_num'))")
        echo -e "${RED}$count occurrences of $code - $message${NC}"
    done
    
    # Count WARNING messages
    echo -e "\n${YELLOW}=== WARNING Messages ===${NC}"
    grep -o "\[WARN:[0-9]\{3\}\]" "$log_file" | sort | uniq -c | sort -k2 | while read count code; do
        code_num=$(echo "$code" | grep -o "[0-9]\{3\}")
        message=$(PYTHONPATH="../" python3 -c "from log_codes import get_message; print(get_message('WARN', '$code_num'))")
        echo -e "${YELLOW}$count occurrences of $code - $message${NC}"
    done
    
    # Count INFO messages
    echo -e "\n${GREEN}=== INFO Messages ===${NC}"
    grep -o "\[INFO:[0-9]\{3\}\]" "$log_file" | sort | uniq -c | sort -k2 | while read count code; do
        code_num=$(echo "$code" | grep -o "[0-9]\{3\}")
        message=$(PYTHONPATH="../" python3 -c "from log_codes import get_message; print(get_message('INFO', '$code_num'))")
        echo -e "${GREEN}$count occurrences of $code - $message${NC}"
    done
    
    # Count DEBUG messages
    echo -e "\n${BLUE}=== DEBUG Messages ===${NC}"
    grep -o "\[DEBUG:[0-9]\{3\}\]" "$log_file" | sort | uniq -c | sort -k2 | while read count code; do
        code_num=$(echo "$code" | grep -o "[0-9]\{3\}")
        message=$(PYTHONPATH="../" python3 -c "from log_codes import get_message; print(get_message('DEBUG', '$code_num'))")
        echo -e "${BLUE}$count occurrences of $code - $message${NC}"
    done
}

# Run the analysis
analyze_logs

# Print total counts
echo -e "\n${BLUE}=== Total Message Counts ===${NC}"
echo -e "${RED}Total ERROR messages: $(grep -c "\[ERROR:" "../scraper.log")${NC}"
echo -e "${YELLOW}Total WARNING messages: $(grep -c "\[WARN:" "../scraper.log")${NC}"
echo -e "${GREEN}Total INFO messages: $(grep -c "\[INFO:" "../scraper.log")${NC}"
echo -e "${BLUE}Total DEBUG messages: $(grep -c "\[DEBUG:" "../scraper.log")${NC}" 