try:
    from ytmusicapi import YTMusic
except ImportError:
    YTMusic = None

try:
    ytmusic = YTMusic() if YTMusic else None
except Exception as e:
    ytmusic = None
    print("Failed to initialize YTMusic:", e)

def get_yt_ids(query: str, link: str):
    video_ids = []
    if ytmusic:
        try:
            search_query = query + " audio"
            results = ytmusic.search(search_query, filter="videos", limit=4)
            for r in results:
                video_ids.append(r['videoId'])
        except Exception as e:
            print("YTMusic Search Error:", e)

    if "watch?v=" in link:
        vid = link.split("watch?v=")[1].split("&")[0]
        if vid not in video_ids:
            video_ids.insert(0, vid)
            
    return video_ids
