
import requests
import json

username = input("Enter the github username:")
repos = requests.get('https://api.github.com/users/'+username+'/repos')

for repo in repos.json():
    if not repo['private']:
        print(repo['name'])

file_name = 'git_api_data_'+username+'.json'

with open(file_name, 'w') as f:
    json.dump(repos.json(), f)
    