# PowerShell script to set up documentation structure

# Create necessary directories
New-Item -ItemType Directory -Force -Path "docs"
New-Item -ItemType Directory -Force -Path "docs/archive"

# Function to create a file if it doesn't exist
function Create-FileIfNotExists {
    param (
        [string]$path,
        [string]$content
    )
    if (-not (Test-Path $path)) {
        Set-Content -Path $path -Value $content
        Write-Host "Created $path"
    } else {
        Write-Host "$path already exists"
    }
}

# Project Manifest template
$project_manifest = @"
# 🎯 [Project Name]

## System Overview

\`\`\`mermaid
graph TD
    A[Component 1] --> B[Component 2]
    B --> C[Component 3]
\`\`\`

## 🔑 Key Components & Entry Points

### Core Files
1. \`path/to/key/file1\`
   - Purpose
   - When to modify

[Additional key files...]

## 🚀 Essential Commands

\`\`\`bash
# Start Development
command1

# Run Tests
command2

# Deploy
command3
\`\`\`

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

\`\`\`mermaid
graph LR
    A[New Task] --> B{Type?}
    B --> C[Implementation]
\`\`\`

## 🎯 Quick Reference

### Common Tasks
1. Task Name
   - Steps
   - Files involved
   - Commands needed
"@

# Technical Guide template
$technical_guide = @"
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
"@

# Quickstart Guide template
$quickstart = @"
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
"@

# Roadmap template
$roadmap = @"
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
"@

# Archive Summary template
$archive_summary = @"
# 📚 Documentation Archive Summary

## Document Evolution
[Track document changes]

## Current Documentation Structure
[Map old docs to new]

## Legacy Access
[Why we keep archives]
"@

# Create core documentation files
Create-FileIfNotExists -path "docs/project_manifest.md" -content $project_manifest
Create-FileIfNotExists -path "docs/technical_guide.md" -content $technical_guide
Create-FileIfNotExists -path "docs/quickstart.md" -content $quickstart
Create-FileIfNotExists -path "docs/roadmap.md" -content $roadmap
Create-FileIfNotExists -path "docs/archive/SUMMARY.md" -content $archive_summary

Write-Host "`nDocumentation structure set up successfully!"
Write-Host "Next steps:"
Write-Host "1. Customize each document for your project"
Write-Host "2. Move existing documentation to archive/"
Write-Host "3. Update archive/SUMMARY.md with document mapping"
Write-Host "4. Review and update project_manifest.md with your key files and commands"
