import re
from pathlib import Path

import httpx

from const import cookies, headers, params, json_data


def extract_youtube_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


def delete_files_with_same_base_name(directory, base_name):
    directory = Path(directory)
    for file in directory.rglob(f"{base_name}.*"):  # Ищем файлы с указанной базой имени
        try:
            file.unlink()
            print(f"Удален файл: {file}")
        except Exception as e:
            print(f"Не удалось удалить {file}: {e}")


async def search_youtube(query: str) -> dict | None:
    json_data["query"] = query
    print("Отправляю запрос")

    async with httpx.AsyncClient() as client:
        response = await client.post('https://www.youtube.com/youtubei/v1/search',
                                     params=params,
                                     cookies=cookies,
                                     headers=headers,
                                     json=json_data,
                                     )
    if response.status_code != 200:
        print("Неуспешный запрос")
        return
    else:
        print("Успешный запрос")
        return response.json()


def get_youtube_query(data: dict) -> list[tuple[str, str]]:
    t = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0][
        "itemSectionRenderer"]["contents"]
    result = []
    for i in t:
        data = i.get("videoRenderer")
        if data:
            title = data.get("title").get("runs")[0]["text"]
            video_id = data.get("videoId")
            if len(title) > 250:
                title = title[:250] + '...'
            result.append((title, video_id))
    return result
