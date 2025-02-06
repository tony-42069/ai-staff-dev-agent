#!/bin/bash

# Create necessary directories
mkdir -p docs/archive

# Function to create a file if it doesn't exist
create_file_if_not_exists() {
    if [ ! -f "$1" ]; then
        echo "$2" > "$1"
        echo "Created $1"
    else
        echo "$1 already exists"
    fi
}

# Project Manifest template
read -r -d '' project_manifest << 'EOF'
# 🎯 [Project Name]

## System Overview

```mermaid
graph TD
    A[Component 1] --> B[Component 2]
    B --> C[Component 3]
```

## 🔑 Key Components & Entry Points

### Core Files
1. `path/to/key/file1`
   - Purpose
   - When to modify

[Additional key files...]

## 🚀 Essential Commands

```bash
# Start Development
command1

# Run Tests
command2

# Deploy
command3
```

## 📚 Documentation Map

### For New Users
1. [Quickstart Guide](quickstart.md)
   - What's covered

### For Developers
1. [Technical Guide](technical_guide.md)
   - What's covered

### For Project Managers
1. [Roadmap](roadmap.md)
   - What's covered

## 🔄 Development Workflow

```mermaid
graph LR
    A[New Task] --> B{Type?}
    B --> C[Implementation]
```

## 🎯 Quick Reference

### Common Tasks
1. Task Name
   - Steps
   - Files involved
   - Commands needed
EOF

# Technical Guide template
read -r -d '' technical_guide << 'EOF'
# 🛠️ Technical Guide

## System Architecture

### Core Components
[Detailed architecture diagram]

### Component Details
[Component-specific information]

## Development Workflow
[Development processes]

## API Reference
[API documentation]

## Deployment
[Deployment procedures]

## Monitoring & Debugging
[Monitoring information]
EOF

# Quickstart Guide template
read -r -d '' quickstart << 'EOF'
# 🚀 Quickstart Guide

## Prerequisites
[Required software/setup]

## Installation Steps
[Step-by-step setup]

## Running the System
[How to run]

## Verification
[How to verify installation]

## Common Issues
[Troubleshooting]
EOF

# Roadmap template
read -r -d '' roadmap << 'EOF'
# 🗺️ Roadmap & Strategy

## Vision
[Project vision]

## Current Status
[Status overview]

## Upcoming Milestones
[Future plans]

## Implementation Strategy
[How we'll get there]

## Success Metrics
[How we measure success]
EOF

# Archive Summary template
read -r -d '' archive_summary << 'EOF'
# 📚 Documentation Archive Summary

## Document Evolution
[Track document changes]

## Current Documentation Structure
[Map old docs to new]

## Legacy Access
[Why we keep archives]
EOF

# Create core documentation files
create_file_if_not_exists "docs/project_manifest.md" "$project_manifest"
create_file_if_not_exists "docs/technical_guide.md" "$technical_guide"
create_file_if_not_exists "docs/quickstart.md" "$quickstart"
create_file_if_not_exists "docs/roadmap.md" "$roadmap"
create_file_if_not_exists "docs/archive/SUMMARY.md" "$archive_summary"

echo -e "\nDocumentation structure set up successfully!"
echo "Next steps:"
echo "1. Customize each document for your project"
echo "2. Move existing documentation to archive/"
echo "3. Update archive/SUMMARY.md with document mapping"
echo "4. Review and update project_manifest.md with your key files and commands"
