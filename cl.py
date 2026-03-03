import requests
city = input( " what is city? ")
response = requests.get(f"https://wttr.in/{city}?format=3")
print("="*30)
print("===SISTEMA DE CLIMA===")
print("="*30)
print(response.text)
print("="*30)
