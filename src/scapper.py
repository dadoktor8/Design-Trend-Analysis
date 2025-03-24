import requests,lxml, re, json, urllib.request, os
from bs4 import BeautifulSoup

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
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
    save_directory = os.path.join("..","data/images")
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
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',"",str(matched_google_images_data)
    )
    matched_google_full_resolution_image = re.findall(r"?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",removed_matched_google_images_thumbnails)
    full_res_images = [
        bytes(bytes(img,"ascii").decode("unicode-escape"),"ascii").decode("unicode-escape") for img in matched_google_full_resolution_image
    ]
    for index, (metadata,thumbnail,original) in enumerate(zip(soup.select('.isv-r.PNCib.MSM1fd.BUooTd'),thumbnails, full_res_images),start=1):
        google_images.append({
            "title":metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["title"],
            "link":metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["href"],
            "source":metadata.select_one(".fxgdke").text,
            "thumbnail":thumbnail,
            "original":original
        })

        print(f"Downloading{index} image .....")
        opener=urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0')]
        urllib.request.install_opener(opener)

        file_path = os.path.join(save_directory,f'original_size_image_{index}.jpg')

        urllib.request.urlretrieve(original, file_path)
        #urllib.request.urlretrieve(original, f'Bs4_Images/original_size_img_{index}.jpg')
    return google_images