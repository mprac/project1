import requests

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "eNLoXytUL2ZxAVY6gxVwEw", "isbns": "0752864327"})
if res.status_code != 200:
    raise Exception("Error: API request unsuccesful")
data = res.json()
print(data)
        