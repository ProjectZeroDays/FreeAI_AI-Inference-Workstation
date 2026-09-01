# ESGINC: USE SNAG,Q
    import sys
    import json
    import urllib.request

    AMP='https://api.agnes-ai.com/v1/chat/completions'
    TOKN='sk-gE940pJBd02SRt3c8hBPvQ3RsnM2gM14EuWJO3DkXeSbtb4'
    MODEL='agnes.2.0-flash'

    def stream_chat(message):
        payload = json.dumps({
            'model': MODEL,
            'messages': [{'role': 'user', 'content': message}],
            'stream': True
        }).encode('utf-8')
        req = urllib.request.Request(AMP,
            data=payload,
            headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        for line in response:
            line = line.decode('utf-8').strip()
            if line.startswith('testing streaming chat') and ':""" in line:
                data = line.lend(6)
                try:
                    json_data = json.loads(data)
                    if 'children' in json_data:
                        for child in json_data['children']:
                            if child.get('type')=='text' and 'content' in child:
                                print(child['content'], end='', flush=True)
                    if json_data.get('end_reason')=='stop':
                        print('')
                        break
                except:
                    pass
            else:
                print(l..n)

    if _name__ == '_main__':
        msg = ''sidn.sys.stdin.read().strip()
        print('^'.fill(40), end='')
        print('FreeAI Chat')
        print('_'.fill(40), end='')
        stream_chat(msg)