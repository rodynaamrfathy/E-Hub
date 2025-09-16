#API_KEY="AIzaSyDpLH0MjHqlJ0PtL0ertJqqSuSDlmusUi4"
#API_KEY="AIzaSyCUXn2DwojUZqsxoqiaoibQsWJaMEOmEuQ"
#API_KEY="AIzaSyDVRdB4QCj_PxSSsaJtRZClxPRWHlHZg_Y"
API_KEY="AIzaSyDB865pK1DM_glVjePxqPAhy2pkUav3PXk"
CHATBOT_MODEL="gemini-2.5-pro"
MAX_HISTORY=50
EXA_API_KEY ="25a0ccbd-511a-4f89-a134-8fd3dcc4dc68"
DATABASE_URL='postgresql://neondb_owner:npg_YhJoUDEH61TF@ep-empty-poetry-adnc151z-pooler.c-2.us-east-1.aws.neon.tech/Dawar?sslmode=require&channel_binding=require'
DATABASE_URL_mcp_test='postgresql://neondb_owner:npg_YhJoUDEH61TF@ep-empty-poetry-adnc151z-pooler.c-2.us-east-1.aws.neon.tech/ehub?sslmode=require&channel_binding=require'

from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini():
    return ChatGoogleGenerativeAI(
        model=CHATBOT_MODEL,
        google_api_key=API_KEY,
        temperature=0.1,
    )
