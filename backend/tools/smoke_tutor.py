"""A local live-provider smoke check. Code is read without terminal echo."""
import getpass
import httpx

with httpx.Client(base_url='http://127.0.0.1:8000', timeout=60) as client:
    login = client.post('/login', json={'profile_id': 'ayesha', 'code': getpass.getpass('Ayesha study code: ')})
    login.raise_for_status()
    headers = {'Authorization': 'Bearer ' + login.json()['token']}
    health = client.get('/health').json()
    print('Health:', health)
    response = client.post('/ask', headers=headers, json={'book': 'chemistry', 'chapter': 14, 'question': 'What is internal energy? Explain it simply.'})
    print('Tutor HTTP status:', response.status_code)
    if response.is_success:
        result = response.json()
        print('Supported:', result['supported'])
        print('Answer:', result['answer'])
        print('Source PDF pages:', [row['page_number'] for row in result['sources']])
    else:
        print('Tutor did not produce an answer; no provider credentials were logged.')
