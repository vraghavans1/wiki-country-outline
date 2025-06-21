from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_country_outline(country: str = Query(...)):
    country_name = country.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{country_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Wikipedia page not found.")
    soup = BeautifulSoup(response.text, "lxml")
    headings = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = tag.get_text().strip()
        if text and not text.lower().startswith("navigation") and not text.lower().startswith("search"):
            headings.append((tag.name, text))
    markdown_lines = ["## Contents", ""]
    for tag, text in headings:
        if tag == "h1": markdown_lines.append(f"# {text}\n")
        elif tag == "h2": markdown_lines.append(f"## {text}\n")
        elif tag == "h3": markdown_lines.append(f"### {text}\n")
        elif tag == "h4": markdown_lines.append(f"#### {text}\n")
        elif tag == "h5": markdown_lines.append(f"##### {text}\n")
        elif tag == "h6": markdown_lines.append(f"###### {text}\n")
    outline = "\n".join(markdown_lines)
    print("Country processed:", country_name)
    return {"outline": outline}


