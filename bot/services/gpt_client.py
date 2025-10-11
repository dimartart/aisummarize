from openai import AsyncOpenAI
from bot.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

PROMPTS = {
    "short": """You are an AI assistant that creates concise summaries.
Create a SHORT summary of the following text:
- Focus on main ideas only
- Keep it brief (2-3 paragraphs maximum)
- Preserve key facts, numbers, names, and dates
- Write in clear, simple language

Text:
{text}""",
    
    "medium": """You are an AI assistant that creates balanced summaries.
Create a MEDIUM-length summary of the following text:
- Cover main ideas and important details
- Include key facts, numbers, names, and dates
- Organize by main topics or sections
- Keep it comprehensive but concise (4-6 paragraphs)

Text:
{text}""",
    
    "details": """You are an analytical assistant that creates detailed summaries.
Create a DETAILED summary of the following text:
- Preserve all important information and nuances
- Include all key facts, numbers, names, dates, and terms
- Organize by sections or topics
- Remove only redundancy and unnecessary repetitions
- Maintain the structure and flow of the original

Text:
{text}"""
}

async def summarize_text(text: str, level: str = "medium") -> str:
    prompt_template = PROMPTS.get(level, PROMPTS["medium"])
    prompt = prompt_template.format(text=text)
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()
