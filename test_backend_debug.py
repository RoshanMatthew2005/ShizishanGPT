import requests
import json

print('🔍 Testing Backend Directly...')

try:
    response = requests.post(
        'http://localhost:8000/api/agent',
        json={'query': 'What is sustainable farming?', 'mode': 'auto'},
        timeout=20
    )
    
    print(f'Status: {response.status_code}')
    print(f'Response size: {len(response.text)} bytes')
    
    if response.status_code == 200:
        result = response.json()
        print(f'\nResponse structure:')
        for key, value in result.items():
            if isinstance(value, str):
                print(f'  {key}: "{value[:100]}..." ({len(value)} chars)')
            else:
                print(f'  {key}: {value}')
        
        if not result.get('final_answer') or len(result.get('final_answer', '')) < 10:
            print(f'\n❌ PROBLEM: Empty or missing final_answer!')
            print(f'Full response: {json.dumps(result, indent=2)}')
    else:
        print(f'Error: {response.text}')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
