from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp
import uvicorn
from typing import List, Optional
import tempfile
import os

app = FastAPI(title="YouTube Downloader API")

# Sample Netscape format cookies (you should replace with your actual cookies)
DEFAULT_COOKIES = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1798057200	PREF	tz=Asia.Karachi
.youtube.com	TRUE	/	FALSE	1798057190	HSID	AAGzFQZFZh0mRhQfq
.youtube.com	TRUE	/	TRUE	1798057190	SSID	A1C7Tpw1sWucqV59s
.youtube.com	TRUE	/	FALSE	1798057190	APISID	Qmp0EW2MOhpf7-za/A0_eVFHjgTsA8mh9N
.youtube.com	TRUE	/	TRUE	1798057190	SAPISID	F2Hj0POJBd04NaM3/AlVcsmqHXy1c09neD
.youtube.com	TRUE	/	TRUE	1798057190	__Secure-1PAPISID	F2Hj0POJBd04NaM3/AlVcsmqHXy1c09neD
.youtube.com	TRUE	/	TRUE	1798057190	__Secure-3PAPISID	F2Hj0POJBd04NaM3/AlVcsmqHXy1c09neD
.youtube.com	TRUE	/	FALSE	1798057190	SID	g.a0003ggENmUAUEcaWOhTsvLTk1g-NQgBAeTD_lPuptcwpFIzdOuQbrKs-W5WbPTY5UA4weh-QAACgYKAWkSARISFQHGX2Mix8AD_VUHezKmFayi1EC9JxoVAUF8yKrOmhtVIRujkRDIRtYN4LO00076
.youtube.com	TRUE	/	TRUE	1798057190	__Secure-1PSID	g.a0003ggENmUAUEcaWOhTsvLTk1g-NQgBAeTD_lPuptcwpFIzdOuQ8G_OKBwW3R794LtQ8-btFwACgYKAQ8SARISFQHGX2MifvC-uN3JRrHRCwc3wzsGLBoVAUF8yKqhmloAUf4mwXDPfDGUxMzB0076
.youtube.com	TRUE	/	TRUE	1798057190	__Secure-3PSID	g.a0003ggENmUAUEcaWOhTsvLTk1g-NQgBAeTD_lPuptcwpFIzdOuQpDQiY5KomN-qm2nNzQIdLAACgYKAbsSARISFQHGX2Mifsq7WMHEsHOlHygtVgQDAhoVAUF8yKoEYlvTvNcTz1Gh9IrdMUMv0076
.youtube.com	TRUE	/	TRUE	1798057192	LOGIN_INFO	AFmmF2swRQIgLQ91ycOD99qAw-D-tfv6MaaZyyvd1hZWDqs7J1hmgjgCIQDVAmyyTmN-ZEpX67uarZGT5YPnrv-eHiFgsO7AIpb8iA:QUQ3MjNmeUZsTi1pVTJWWUtuUlE0cThvT2p6V1RTNF9WY29yQUpnZE96SkRtd1NaUkNsZW4zY1B4VnhqQU9ka3UxejNBY3FoWGJQVTdERDdfdWZDZUNBdzlQLUloVDFENUdOS0ZBam1sSVFrSmlRamM4SmRoc3RrQ3prbGt6UlF6dzNtLTMtMHMtUlgxNWVKRVBULU5XOHBXbl94NEtNZkFn
.youtube.com	TRUE	/	TRUE	1795036818	__Secure-1PSIDTS	sidts-CjUBwQ9iI4GmhOGjrbUe5R5Krj3dlQhIXLMhTms9tudpv4FvHwXSPKZa4PW5C3FZcZ5ZJ4u4-BAA
.youtube.com	TRUE	/	TRUE	1795036818	__Secure-3PSIDTS	sidts-CjUBwQ9iI4GmhOGjrbUe5R5Krj3dlQhIXLMhTms9tudpv4FvHwXSPKZa4PW5C3FZcZ5ZJ4u4-BAA
.youtube.com	TRUE	/	TRUE	0	YSC	pzEH1nwGkT8
.youtube.com	TRUE	/	FALSE	1795042768	SIDCC	AKEyXzX1oO-QkhJomQ1zDsr-5dRxy7PpekGAqPtdvBq6mnuBA1tBBV5uU3BgGigtCUDjGIMLdw
.youtube.com	TRUE	/	TRUE	1795042768	__Secure-1PSIDCC	AKEyXzX-chEqFyYfzCrc5wfLFcE_UZiZNcjmwg9SPy7mzZcZjZInlsC0cfAIueeO25kNyMbZ
.youtube.com	TRUE	/	TRUE	1795042768	__Secure-3PSIDCC	AKEyXzW9xObbvB589LJm7R0_ELiu_M_dxyrjGzWt8XcR0vHHd_YZlVsXZnRBNSRPDJIAEKOg
.youtube.com	TRUE	/	TRUE	1779058768	VISITOR_INFO1_LIVE	eSO8Bb-X6Ss
.youtube.com	TRUE	/	TRUE	1779058768	VISITOR_PRIVACY_METADATA	CgJQSxIEGgAgWw%3D%3D
.youtube.com	TRUE	/	TRUE	1779049138	__Secure-ROLLOUT_TOKEN	COiTlKGc2oiXeBCH3q_gwvyQAxiwgv3iwvyQAw%3D%3D
"""

def get_cookies_file():
    """Create temporary cookies file from DEFAULT_COOKIES"""
    if DEFAULT_COOKIES.strip():
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            temp_file.write(DEFAULT_COOKIES)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"Error creating cookies file: {e}")
    return None

def extract_info(url: str):
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }
    
    # Add cookies if available
    cookies_path = get_cookies_file()
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path
        print("Using cookies for extraction")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Clean up cookies file
        if cookies_path and os.path.exists(cookies_path):
            os.unlink(cookies_path)
            
        return info


@app.get("/api/info")
def get_info(url: str = Query(...)):
    try:
        info = extract_info(url)

        formats = []

        for f in info.get("formats", []):
            formats.append({
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution") or f"{f.get('height', 'N/A')}p",
                "filesize": f.get("filesize"),
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "audio": f.get("acodec") != "none",
                "video": f.get("vcodec") != "none",
                "audio_codec": f.get("acodec"),
                "video_codec": f.get("vcodec"),
                "fps": f.get("fps"),
                "audio_bitrate": f.get("abr"),
                "url": f.get("url"),
                "format_note": f.get("format_note", ""),
                "quality": f.get("quality"),
            })

        return {
            "status": True,
            "id": info.get("id"),
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "duration_string": info.get("duration_string"),
            "uploader": info.get("uploader"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "categories": info.get("categories", []),
            "tags": info.get("tags", []),
            "description": info.get("description"),
            "formats": formats,
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/mp3")
def get_mp3(url: str = Query(...), quality: Optional[str] = Query("best")):
    try:
        info = extract_info(url)
        audio_formats = [
            f for f in info["formats"] 
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ]

        if quality == "best":
            best_audio = sorted(audio_formats, key=lambda x: x.get("abr", 0) or 0, reverse=True)[0]
        elif quality == "worst":
            best_audio = sorted(audio_formats, key=lambda x: x.get("abr", 0) or 0)[0]
        else:
            # Try to find specific quality
            quality_audio = [f for f in audio_formats if f.get("format_note", "").lower() == quality.lower()]
            if quality_audio:
                best_audio = quality_audio[0]
            else:
                best_audio = sorted(audio_formats, key=lambda x: x.get("abr", 0) or 0, reverse=True)[0]

        return {
            "status": True,
            "format": "audio",
            "ext": best_audio["ext"],
            "bitrate": best_audio.get("abr"),
            "filesize_mb": round(best_audio.get("filesize", 0) / (1024 * 1024), 2) if best_audio.get("filesize") else None,
            "audio_codec": best_audio.get("acodec"),
            "url": best_audio["url"],
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/mp4")
def get_mp4(url: str = Query(...), quality: Optional[str] = Query("best")):
    try:
        info = extract_info(url)
        video_formats = [
            f for f in info["formats"] 
            if f.get("vcodec") != "none" and f.get("acodec") != "none"
        ]

        if quality == "best":
            best_video = sorted(video_formats, key=lambda x: (x.get("height") or 0, x.get("fps") or 0), reverse=True)[0]
        elif quality == "worst":
            best_video = sorted(video_formats, key=lambda x: (x.get("height") or 0, x.get("fps") or 0))[0]
        else:
            # Try to find specific resolution
            quality_videos = [f for f in video_formats if f.get("format_note", "").lower() == quality.lower()]
            if quality_videos:
                best_video = quality_videos[0]
            else:
                best_video = sorted(video_formats, key=lambda x: (x.get("height") or 0, x.get("fps") or 0), reverse=True)[0]

        return {
            "status": True,
            "format": "video",
            "resolution": best_video.get("resolution"),
            "height": best_video.get("height"),
            "ext": best_video["ext"],
            "filesize_mb": round(best_video.get("filesize", 0) / (1024 * 1024), 2) if best_video.get("filesize") else None,
            "fps": best_video.get("fps"),
            "audio_codec": best_video.get("acodec"),
            "video_codec": best_video.get("vcodec"),
            "url": best_video["url"],
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/all-formats")
def get_all_formats(url: str = Query(...)):
    try:
        info = extract_info(url)
        
        # Categorize formats
        audio_only = []
        video_only = []
        video_audio = []
        
        for f in info.get("formats", []):
            format_info = {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution") or f"{f.get('height', 'N/A')}p",
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "audio_codec": f.get("acodec"),
                "video_codec": f.get("vcodec"),
                "fps": f.get("fps"),
                "audio_bitrate": f.get("abr"),
                "format_note": f.get("format_note", ""),
                "url": f.get("url"),
            }
            
            has_audio = f.get("acodec") != "none"
            has_video = f.get("vcodec") != "none"
            
            if has_audio and not has_video:
                audio_only.append(format_info)
            elif has_video and not has_audio:
                video_only.append(format_info)
            elif has_video and has_audio:
                video_audio.append(format_info)

        return {
            "status": True,
            "title": info.get("title"),
            "audio_only_formats": sorted(audio_only, key=lambda x: x.get("audio_bitrate", 0) or 0, reverse=True),
            "video_only_formats": sorted(video_only, key=lambda x: x.get("height", 0) or 0, reverse=True),
            "video_audio_formats": sorted(video_audio, key=lambda x: x.get("height", 0) or 0, reverse=True),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/download")
def download_format(url: str = Query(...), format_id: str = Query(...)):
    try:
        info = extract_info(url)
        
        # Find the specific format
        selected_format = None
        for f in info.get("formats", []):
            if f.get("format_id") == format_id:
                selected_format = f
                break
        
        if not selected_format:
            return JSONResponse({"status": False, "error": "Format not found"}, status_code=404)

        return {
            "status": True,
            "title": info.get("title"),
            "format_id": selected_format.get("format_id"),
            "ext": selected_format.get("ext"),
            "resolution": selected_format.get("resolution"),
            "filesize_mb": round(selected_format.get("filesize", 0) / (1024 * 1024), 2) if selected_format.get("filesize") else None,
            "audio_codec": selected_format.get("acodec"),
            "video_codec": selected_format.get("vcodec"),
            "url": selected_format.get("url"),
            "direct_download_url": selected_format.get("url"),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/audio-formats")
def get_audio_formats(url: str = Query(...)):
    try:
        info = extract_info(url)
        audio_formats = [
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "bitrate": f.get("abr"),
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "audio_codec": f.get("acodec"),
                "format_note": f.get("format_note", ""),
                "url": f.get("url"),
            }
            for f in info["formats"] 
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ]

        return {
            "status": True,
            "title": info.get("title"),
            "audio_formats": sorted(audio_formats, key=lambda x: x.get("bitrate", 0) or 0, reverse=True),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/video-formats")
def get_video_formats(url: str = Query(...)):
    try:
        info = extract_info(url)
        video_formats = [
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution") or f"{f.get('height', 'N/A')}p",
                "height": f.get("height"),
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "fps": f.get("fps"),
                "video_codec": f.get("vcodec"),
                "audio_codec": f.get("acodec"),
                "format_note": f.get("format_note", ""),
                "url": f.get("url"),
            }
            for f in info["formats"] 
            if f.get("vcodec") != "none"
        ]

        return {
            "status": True,
            "title": info.get("title"),
            "video_formats": sorted(video_formats, key=lambda x: x.get("height", 0) or 0, reverse=True),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


# --------------------------------------------------------
# 🚀 Run server via: python main.py
# --------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


