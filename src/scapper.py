import requests,lxml, re, json, urllib.requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
}
params = {
    "q":"vaporwave aesthetic",
    "tbm":"isch",
    "hl":"en",
    "gl":"in",
    "ijn":"0"
}
html = requests.get("https://www.google.com/search",params=params, headers=headers, timeout=30)
soup = BeautifulSoup(html.text,"lxml")

def get_images_with_request_headers():
    del params["ijn"]
    params["content-type"] = "image/png"
    return [img["src"] for img in soup.select("img")]

def get_selected_search_data():
    suggested_Searches = []
    all_script_tag = soup.select("script")
    matched_images = " ".join(re.findall(r"AF_initDataCallback\(({key: 'ds:1'.*?)\);</script>",str(all_script_tag)))
    matched_images_data_fix = json.dumps(matched_images)
    matched_images_data_json = json.loads(matched_images_data_fix)
    suggested_Search_thumbnails = ",".join(re.findall(r'{key(.*?)\[null,\"Size\"',matched_images_data_json))
    suggested_Search_thumbnails_encoded = re.findall(r'\"(https:\/\/encrypted.*?)\"',suggested_Search_thumbnails)

    for suggested_Searches, suggested_Search_fixed_thumbnails in zip(soup.select(".PKhmud.sc-it.tzVsfd"), suggested_Search_thumbnails_encoded):
        suggested_Searches.append({
            "name":suggested_Searches.select_one(".VlHyHc").text,
            "link":f"https://www.google.com{suggested_Searches.a['href']}",
            "chips":" ".join(re.findall(r"&chips=(.*?)&",suggested_Searches.a["href"])),
            "thumbnail":bytes(suggested_Search_fixed_thumbnails,"ascii").decode("unicode-escape")
        })
    return suggested_Searches

def get_original_images():
    google_images = []
    all_script_tag = soup.select("script")

    matched_images_data = " ".join(re.findall(r"AF_initDataCallback\(([^<]+)\);",str(all_script_tag)))

    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    matched_google_images_data = re.findall(r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}',matched_images_data_json)

    matched_google_images_thumbnails = ", ".join(
        re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                   str(matched_google_images_data))).split(", ")

    thumbnails = [
        bytes(bytes(thumbnail, "ascii").decode("unicode-escape"),"ascii").decode("unicode-escape") for thumbnail in matched_google_images_thumbnails]

    removed_matched_google_images_thumbnails = re.sub(
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]'
    )
