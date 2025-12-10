import json

with open('openapi.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find where paths are in the file
with open('openapi.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Look for paths section by finding "paths": and finding the JSON object
paths_start = content.find('"paths":')
if paths_start != -1:
    # Count braces to find the end of paths object
    brace_count = 0
    pos = paths_start + len('"paths":')
    while pos < len(content) and brace_count >= 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    
    # Extract the paths JSON
    paths_json = content[paths_start:pos+1]
    paths = json.loads(paths_json)
    
    print(f"Total endpoints: {len(paths)}")
    print("\nAvailable endpoints:")
    for i, (path, methods) in enumerate(paths.items()):
        if i < 15:  # First 15 endpoints
            method_list = list(methods.keys())
            print(f"  {path}: {method_list}")
        elif i == 15:
            print(f"  ... and {len(paths)-15} more")
    
    # Look for diagnostic endpoints
    diagnostic_endpoints = [path for path in paths.keys() if 'diagnostic' in path.lower()]
    if diagnostic_endpoints:
        print(f"\n🔍 Diagnostic endpoints found: {diagnostic_endpoints}")
    else:
        print(f"\n❌ No diagnostic endpoints found")
        print(f"🔍 Available prefixes: {list(set([path.split('/')[1] if len(path.split('/')) > 1 else path for path in paths.keys()])[:5])}")
else:
    print("❌ Could not find paths section in OpenAPI spec")
