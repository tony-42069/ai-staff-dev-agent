#!/usr/bin/env python
import yaml
import os

def migrate_capabilities(input_file, output_file):
    with open(input_file, 'r') as f:
        data = yaml.safe_load(f)

    # Convert each capability's requirements
    for capability in data:
        if 'requirements' in capability:
            new_reqs = []
            for req in capability['requirements']:
                if isinstance(req, str):
                    # Parse the old "type:name" format
                    if ':' in req:
                        req_type, req_name = req.split(':', 1)
                    else:
                        req_type, req_name = 'package', req
                    
                    new_reqs.append({
                        "name": req_name,
                        "type": req_type,
                        "optional": "False"
                    })
                elif isinstance(req, dict):
                    # Ensure required fields exist
                    if "name" not in req:
                        req["name"] = "unknown"
                    if "type" not in req:
                        req["type"] = "package"
                    if "optional" not in req:
                        req["optional"] = False
                    new_reqs.append(req)
                else:
                    raise ValueError(f"Unknown requirement format: {req}")
            capability['requirements'] = new_reqs

    # Create backup of original file
    backup_file = input_file + '.backup'
    if os.path.exists(input_file):
        with open(backup_file, 'w') as f:
            with open(input_file, 'r') as original:
                f.write(original.read())

    # Write updated data
    with open(output_file, 'w') as f:
        yaml.dump(data, f, sort_keys=False)

if __name__ == '__main__':
    capabilities_file = 'private/config/capabilities.yaml'
    migrate_capabilities(capabilities_file, capabilities_file)
    print(f"Migration completed. Backup created at {capabilities_file}.backup")
