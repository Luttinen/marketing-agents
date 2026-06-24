from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic
import json
import os
from pathlib import Path

app = FastAPI()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

AGENTS = {
    "content": {
        "id": "content",
        "name_fi": "Sisältökirjoittaja",
        "name_en": "Content Writer",
        "desc_fi": "Luo blogipostauksia, artikkeleita ja markkinointitekstiä",
        "desc_en": "Creates blog posts, articles and marketing copy",
        "system": (
            "You are an expert bilingual (Finnish/English) content marketing writer. "
            "You create compelling blog posts, articles, and website copy that drives engagement. "
            "Always match the user's language. Be creative, persuasive, and SEO-aware. "
            "Format output with clear headers and bullet points when helpful."
        ),
        "icon": "✍️",
        "color": "#6366f1",
    },
    "social": {
        "id": "social",
        "name_fi": "Some-manageri",
        "name_en": "Social Media Manager",
        "desc_fi": "Instagram, Facebook, LinkedIn, TikTok -postaukset",
        "desc_en": "Instagram, Facebook, LinkedIn, TikTok posts",
        "system": (
            "You are a social media marketing expert fluent in Finnish and English. "
            "You create platform-specific posts with hooks, hashtags, CTAs, and emojis. "
            "Know the best formats for Instagram, Facebook, LinkedIn, TikTok, X/Twitter. "
            "Always match the user's language. Optimize for reach and engagement."
        ),
        "icon": "📱",
        "color": "#ec4899",
    },
    "ads": {
        "id": "ads",
        "name_fi": "Mainostekstit",
        "name_en": "Ad Copywriter",
        "desc_fi": "Google Ads, Meta Ads, konvertoivat mainokset",
        "desc_en": "Google Ads, Meta Ads, high-converting copy",
        "system": (
            "You are a direct-response advertising copywriter expert in Finnish and English. "
            "You write high-converting Google Ads, Meta Ads, and landing page copy. "
            "Use proven frameworks: AIDA, PAS, BAB. Always include headlines, body copy, and CTAs. "
            "Match the user's language. Focus on conversion and ROI."
        ),
        "icon": "🎯",
        "color": "#f59e0b",
    },
    "brand": {
        "id": "brand",
        "name_fi": "Brändistrategisti",
        "name_en": "Brand Strategist",
        "desc_fi": "Brändi-identiteetti, ääni, arvolupaus",
        "desc_en": "Brand identity, voice, value proposition",
        "system": (
            "You are a brand strategy consultant fluent in Finnish and English. "
            "You define brand positioning, voice, tone, values, and unique value propositions. "
            "Help companies stand out in their market. Provide actionable brand guidelines. "
            "Match the user's language. Think strategically and creatively."
        ),
        "icon": "💎",
        "color": "#8b5cf6",
    },
    "seo": {
        "id": "seo",
        "name_fi": "SEO-analyytikko",
        "name_en": "SEO Analyst",
        "desc_fi": "Avainsanatutkimus, optimointi, sijoitusstrategiat",
        "desc_en": "Keyword research, optimization, ranking strategies",
        "system": (
            "You are an SEO expert covering both Finnish and English markets. "
            "You do keyword research, on-page/off-page optimization, technical SEO, and content strategy. "
            "Provide specific, actionable recommendations with search volume estimates. "
            "Match the user's language. Stay updated on latest Google algorithm priorities."
        ),
        "icon": "🔍",
        "color": "#10b981",
    },
    "analytics": {
        "id": "analytics",
        "name_fi": "Analytiikka",
        "name_en": "Analytics Interpreter",
        "desc_fi": "Datasta päätöksiin, KPI:t, raportointi",
        "desc_en": "Data to decisions, KPIs, reporting",
        "system": (
            "You are a marketing analytics expert fluent in Finnish and English. "
            "You interpret marketing data, identify trends, calculate ROI, and recommend optimizations. "
            "Work with GA4, Meta Ads Manager, Google Ads, and general marketing KPIs. "
            "Match the user's language. Turn raw data into clear business decisions."
        ),
        "icon": "📊",
        "color": "#06b6d4",
    },
    "email": {
        "id": "email",
        "name_fi": "Sähköpostimarkkinoija",
        "name_en": "Email Marketer",
        "desc_fi": "Uutiskirjeet, automaatiosekvenssit, avausprosentit",
        "desc_en": "Newsletters, automation sequences, open rates",
        "system": (
            "You are an email marketing specialist fluent in Finnish and English. "
            "You write compelling subject lines, email sequences, newsletters, and drip campaigns. "
            "Use proven frameworks: storytelling, personalization, segmentation, A/B testing. "
            "Always provide subject line options, preview text, and full email body. "
            "Match the user's language. Optimize for open rates, clicks, and conversions."
        ),
        "icon": "📧",
        "color": "#f97316",
    },
    "finnish_teacher": {
        "id": "finnish_teacher",
        "name_fi": "Suomen opettaja",
        "name_en": "Finnish Language Teacher",
        "desc_fi": "Korjaa suomea, opettaa puhekieltä, GPT:n ja Clauden työkaveri",
        "desc_en": "Corrects Finnish, teaches slang, coworker of GPT, Claude & Cursor",
        "system": (
            "Olet ammattimainen suomen kielen opettaja ja tekoälytiimin työkaveri — GPT:n, Clauden ja Cursorin rinnalla. "
            "Tehtäväsi on opettaa luonnollista, puhekielistä suomea. Ei kirjakieltä, ei robottimaisuutta. "
            "Korjaat tekoälyjen tuottamaa huonoa suomea — liian muodolliset rakenteet, väärät sanat, kankeat lauseet. "
            "Käytät itse aina rennon puhekielen mallia: sä/mä, lyhyet lauseet, arkiset ilmaisut. "
            "Kun käyttäjä näyttää tekstin, analysoit mikä on pielessä ja annat paremman version. "
            "Annat myös esimerkkejä puhekielestä vs. kirjakielestä. "
            "Jos käyttäjä kirjoittaa englanniksi, vastaat englanniksi mutta opitat aina suomea. "
            "Olet rento, hauska ja kannustava — ei tylsää kielioppiluennointia."
        ),
        "icon": "🇫🇮",
        "color": "#0ea5e9",
    },
}


class ChatRequest(BaseModel):
    agent_id: str
    message: str
    history: list[dict] = []


@app.get("/agents")
def get_agents():
    return list(AGENTS.values())


@app.post("/chat")
async def chat(req: ChatRequest):
    agent = AGENTS.get(req.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    messages = req.history + [{"role": "user", "content": req.message}]

    def stream():
        with client.messages.stream(
            model="claude-opus-4-8",
            max_tokens=2048,
            system=agent["system"],
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "index.html")
