import re
import requests

f = open("demo.html", "r")

pattern = r"https://leetcode\.com/problems/([\w-]+)/"

l = re.findall(pattern, f.read())

for i in range(5):
    data = requests.get(f"https://leetcode-api-pied.vercel.app/problem/{l[i]}")
    print(data.json()['title'])