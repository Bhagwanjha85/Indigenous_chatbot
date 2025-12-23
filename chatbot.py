import streamlit as st
import google.genai as genai
import requests
import os
import time
from PIL import Image
import io


st.set_page_config(page_title="Indigenous Language chatbot", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

* { 
    font-family: 'Poppins', sans-serif;
     }

.stApp {
    background: linear-gradient(-45deg, gray, green);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.main .block-container {
    backdrop-filter: blur(15px);
    border-radius: 25px;
    padding: 2.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Header Section */
.main-header {
    background: linear-gradient(135deg, gray  0%, green  100%);
    color:black;
    text-weight:900;
    margin: -1rem -1rem 2rem -1rem;
    text-align: center;
    border-radius: 16px;
    box-shadow: 0 10px 10px rgba(0, 0, 0, 0.4);
}

h1 {
    color: #ffffff !important;
    font-size: 2.8rem;
    font-weight: 700;
    text-shadow: 3px 3px 10px rgba(0,0,0,0.6);
    margin: 0;
}

/* Sidebar Styling */
.stSidebar {
    background: linear-gradient(180deg, #1e1b4b 0%, #4338ca 100%);
}

.stSidebar label {
    color: #ffffff !important;
    font-weight: 900;
}

.stChatMessage[data-testid="chat-message-user"] {
    background: rgba(251, 191, 36, 0.2) !important;
    border-radius: 20px 20px 5px 20px;
    margin: 1.5rem 0 1.5rem 3rem;
    padding: 1.5rem;
    border: 1px solid #fbbf24;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.stChatMessage[data-testid="chat-message-user"] * {
    color: #ffffff !important;
    font-weight: 500;
}

.stChatMessage[data-testid="chat-message-assistant"] {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px 20px 20px 5px;
    margin: 1.5rem 3rem 1.5rem 0;
    padding: 1.5rem;
    border-left: 5px solid #fbbf24;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.stChatMessage[data-testid="chat-message-assistant"] * {
    color: #ffffff !important;
    font-weight: 400;
    line-height: 1.7;
}

/* Input Field - Dark background for white text entry */
.stChatInput input {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 2px solid #fbbf24 !important;
    color: white !important;
    border-radius: 25px;
}

.stChatInput input::placeholder {
    color: #cbd5e1;
}

/* Wiki Sources Styling */
.wiki-source {
    background: rgba(255, 255, 255, 0.05);
    border-left: 5px solid #fbbf24;
    padding: 15px;
    border-radius: 12px;
    color: white;
}

.wiki-source a {
    color: #fbbf24 !important;
    text-decoration: underline;
}

.wiki-source small {
    color: #cbd5e1;
    display: block;
    margin-top: 8px;
}

.error-box {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    border-left: 5px solid #ef4444;
    padding: 15px;
    border-radius: 12px;
    margin: 15px 0;
    color: #000000;
}

/* Avatar Styling */
.stChatMessage img {
    border-radius: 15px;
    border: 3px solid #d97706;
    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.4);
}

/* Image Upload Styling */
.upload-section {
    background: rgba(255, 255, 255, 0.1);
    border: 2px dashed #fbbf24;
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
}

.uploaded-image-preview {
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid #fbbf24;
    border-radius: 15px;
    padding: 10px;
    margin: 10px 0;
}

/* Button Styling */
.stButton button {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    transition: transform 0.2s;
}

.stButton button:hover {
    transform: scale(1.05);
}

@media (max-width: 768px) {
    .stChatMessage[data-testid="chat-message-user"],
    .stChatMessage[data-testid="chat-message-assistant"] {
        margin-left: 0.5rem;
        margin-right: 0.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Expanded Language Config with more indigenous and regional languages
LANGUAGES = {
    "English": {"title": "Indigenous Knowledge Bridge", "welcome": "Namaste! Ask me anything from Wikimedia!", 
                "placeholder": "Ask about any topic...", "searching": "Searching...", "sources": "Sources:", 
                "quota_error": "API limit reached. Please wait 30 seconds and try again.", "wiki_code": "en",
                "upload_prompt": "Upload an image", "image_analysis": "Analyzing image...", 
                "ask_image": "Ask about this image:", "submit_image": "Submit Image"},
    
    "हिन्दी": {"title": "स्वदेशी ज्ञान सेतु", "welcome": "नमस्ते! विकिमीडिया से कुछ भी पूछें!", 
               "placeholder": "कोई भी विषय पूछें...", "searching": "खोज रहे हैं...", "sources": "स्रोत:", 
               "quota_error": "API सीमा पूर्ण। 30 सेकंड प्रतीक्षा करें।", "wiki_code": "hi",
               "upload_prompt": "एक छवि अपलोड करें", "image_analysis": "छवि का विश्लेषण...",
               "ask_image": "इस छवि के बारे में पूछें:", "submit_image": "छवि सबमिट करें"},
    
    "বাংলা": {"title": "স্বদেশী জ্ঞান সেতু", "welcome": "নমস্কার! উইকিমিডিয়া থেকে জিজ্ঞাসা করুন!", 
              "placeholder": "যেকোনো বিষয়...", "searching": "খোঁজা হচ্ছে...", "sources": "উৎস:", 
              "quota_error": "API সীমা শেষ। 30 সেকেন্ড অপেক্ষা করুন।", "wiki_code": "bn",
              "upload_prompt": "একটি ছবি আপলোড করুন", "image_analysis": "ছবি বিশ্লেষণ...",
              "ask_image": "এই ছবি সম্পর্কে জিজ্ঞাসা করুন:", "submit_image": "ছবি জমা দিন"},
    
    "தமிழ்": {"title": "அறிவு பாலம்", "welcome": "வணக்கம்! விக்கிமீடியாவில் கேளுங்கள்!", 
              "placeholder": "ஏதாவது கேளுங்கள்...", "searching": "தேடுகிறது...", "sources": "ஆதாரங்கள்:", 
              "quota_error": "API வரம்பு முடிந்தது। 30 விநாடி காத்திருக்கவும்.", "wiki_code": "ta",
              "upload_prompt": "படத்தை பதிவேற்றவும்", "image_analysis": "படம் பகுப்பாய்வு...",
              "ask_image": "இந்த படத்தைப் பற்றி கேளுங்கள்:", "submit_image": "படத்தை சமர்ப்பிக்கவும்"},
    
    "తెలుగు": {"title": "జ్ఞాన వంతెన", "welcome": "నమస్కారం! వికీమీడియాలో అడగండి!", 
               "placeholder": "ఏదైనా అడగండి...", "searching": "శోధిస్తోంది...", "sources": "మూలాలు:", 
               "quota_error": " API పరిమితి చేరుకుంది। 30 సెకన్లు వేచి ఉండండి.", "wiki_code": "te",
               "upload_prompt": "చిత్రాన్ని అప్‌లోడ్ చేయండి", "image_analysis": "చిత్ర విశ్లేషణ...",
               "ask_image": "ఈ చిత్రం గురించి అడగండి:", "submit_image": "చిత్రాన్ని సమర్పించండి"},
    
    "ಕನ್ನಡ": {"title": " ಜ್ಞಾನ ಸೇತುವೆ", "welcome": "ನಮಸ್ಕಾರ!  ವಿಕಿಮೀಡಿಯಾದಿಂದ ಕೇಳಿ!", 
              "placeholder": "ಯಾವುದೇ ವಿಷಯ ಕೇಳಿ...", "searching": " ಹುಡುಕುತ್ತಿದೆ...", "sources": " ಮೂಲಗಳು:", 
              "quota_error": " API ಮಿತಿ ತಲುಪಿದೆ। 30 ಸೆಕೆಂಡುಗಳು ನಿರೀಕ್ಷಿಸಿ।", "wiki_code": "kn",
              "upload_prompt": "ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ", "image_analysis": "ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆ...",
              "ask_image": "ಈ ಚಿತ್ರದ ಬಗ್ಗೆ ಕೇಳಿ:", "submit_image": "ಚಿತ್ರವನ್ನು ಸಲ್ಲಿಸಿ"},
    
    "മലയാളം": {"title": " അറിവിന്റെ പാലം", "welcome": "നമസ്കാരം!  വിക്കിമീഡിയയിൽ ചോദിക്കൂ!", 
               "placeholder": "എന്തും ചോദിക്കൂ...", "searching": " തിരയുന്നു...", "sources": " ഉറവിടങ്ങൾ:", 
               "quota_error": " API പരിധി എത്തി। 30 സെക്കൻഡ് കാത്തിരിക്കൂ।", "wiki_code": "ml",
               "upload_prompt": "ചിത്രം അപ്‌ലോഡ് ചെയ്യുക", "image_analysis": "ചിത്ര വിശകലനം...",
               "ask_image": "ഈ ചിത്രത്തെക്കുറിച്ച് ചോദിക്കൂ:", "submit_image": "ചിത്രം സമർപ്പിക്കുക"},
    
    "मराठी": {"title": " ज्ञान सेतू", "welcome": "नमस्कार!  विकिमीडियामधून विचारा!", 
              "placeholder": "कोणताही विषय विचारा...", "searching": " शोधत आहे...", "sources": " स्रोत:", 
              "quota_error": " API मर्यादा संपली। 30 सेकंद प्रतीक्षा करा।", "wiki_code": "mr",
              "upload_prompt": "प्रतिमा अपलोड करा", "image_analysis": "प्रतिमा विश्लेषण...",
              "ask_image": "या प्रतिमेबद्दल विचारा:", "submit_image": "प्रतिमा सबमिट करा"},
    
    "ગુજરાતી": {"title": " જ્ઞાન સેતુ", "welcome": "નમસ્તે!  વિકિમીડિયામાંથી પૂછો!", 
               "placeholder": "કોઈપણ વિષય પૂછો...", "searching": " શોધી રહ્યા છીએ...", "sources": " સ્રોતો:", 
               "quota_error": " API મર્યાદા પૂર્ણ। 30 સેકંડ રાહ જુઓ।", "wiki_code": "gu",
               "upload_prompt": "છબી અપલોડ કરો", "image_analysis": "છબી વિશ્લેષણ...",
               "ask_image": "આ છબી વિશે પૂછો:", "submit_image": "છબી સબમિટ કરો"},
    
    "ଓଡ଼ିଆ": {"title": " ଜ୍ଞାନ ସେତୁ", "welcome": "ନମସ୍କାର!  ଉଇକିମିଡ଼ିଆରୁ ପଚାରନ୍ତୁ!", 
             "placeholder": "କୌଣସି ବିଷୟ ପଚାରନ୍ତୁ...", "searching": " ଖୋଜୁଛି...", "sources": " ଉତ୍ସ:", 
             "quota_error": " API ସୀମା ପହଞ୍ଚିଛି। 30 ସେକେଣ୍ଡ ଅପେକ୍ଷା କରନ୍ତୁ।", "wiki_code": "or",
             "upload_prompt": "ଚିତ୍ର ଅପଲୋଡ୍ କରନ୍ତୁ", "image_analysis": "ଚିତ୍ର ବିଶ୍ଳେଷଣ...",
             "ask_image": "ଏହି ଚିତ୍ର ବିଷୟରେ ପଚାରନ୍ତୁ:", "submit_image": "ଚିତ୍ର ଦାଖଲ କରନ୍ତୁ"},
    
    "ਪੰਜਾਬੀ": {"title": " ਗਿਆਨ ਪੁਲ", "welcome": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ!  ਵਿਕੀਮੀਡੀਆ ਤੋਂ ਪੁੱਛੋ!", 
              "placeholder": "ਕੋਈ ਵੀ ਵਿਸ਼ਾ ਪੁੱਛੋ...", "searching": " ਖੋਜ ਰਿਹਾ ਹੈ...", "sources": " ਸਰੋਤ:", 
              "quota_error": " API ਸੀਮਾ ਪੂਰੀ ਹੋਈ। 30 ਸਕਿੰਟ ਉਡੀਕ ਕਰੋ।", "wiki_code": "pa",
              "upload_prompt": "ਤਸਵੀਰ ਅੱਪਲੋਡ ਕਰੋ", "image_analysis": "ਤਸਵੀਰ ਵਿਸ਼ਲੇਸ਼ਣ...",
              "ask_image": "ਇਸ ਤਸਵੀਰ ਬਾਰੇ ਪੁੱਛੋ:", "submit_image": "ਤਸਵੀਰ ਜਮ੍ਹਾਂ ਕਰੋ"},
    
    "অসমীয়া": {"title": " জ্ঞান সেতু", "welcome": "নমস্কাৰ!  ৱিকিমিডিয়াৰ পৰা সোধক!", 
               "placeholder": "যিকোনো বিষয় সোধক...", "searching": " সন্ধান কৰি আছে...", "sources": " উৎস:", 
               "quota_error": " API সীমা শেষ। 30 চেকেণ্ড অপেক্ষা কৰক।", "wiki_code": "as",
               "upload_prompt": "এখন ছবি আপলোড কৰক", "image_analysis": "ছবি বিশ্লেষণ...",
               "ask_image": "এই ছবিৰ বিষয়ে সোধক:", "submit_image": "ছবি দাখিল কৰক"},
    
    "नेपाली": {"title": " ज्ञान सेतु", "welcome": "नमस्ते!  विकिमीडियाबाट सोध्नुहोस्!", 
              "placeholder": "कुनै पनि विषय सोध्नुहोस्...", "searching": " खोजी गर्दै...", "sources": " स्रोतहरू:", 
              "quota_error": " API सीमा समाप्त। 30 सेकेन्ड प्रतीक्षा गर्नुहोस्।", "wiki_code": "ne",
              "upload_prompt": "छवि अपलोड गर्नुहोस्", "image_analysis": "छवि विश्लेषण...",
              "ask_image": "यो छविको बारेमा सोध्नुहोस्:", "submit_image": "छवि पेश गर्नुहोस्"},
    
    "संस्कृत": {"title": " ज्ञान सेतुः", "welcome": "नमस्ते!  विकिमीडियातः पृच्छतु!", 
              "placeholder": "किमपि विषयं पृच्छतु...", "searching": " अन्वेषणं क्रियते...", "sources": " स्रोताः:", 
              "quota_error": " API सीमा समाप्तः। 30 क्षणान् प्रतीक्षतु।", "wiki_code": "sa",
              "upload_prompt": "चित्रं उपारोपयतु", "image_analysis": "चित्र विश्लेषणम्...",
              "ask_image": "एतस्य चित्रस्य विषये पृच्छतु:", "submit_image": "चित्रं प्रेषयतु"},
    
    "ਉਰਦੂ": {"title": " علم کا پل", "welcome": "السلام علیکم!  وکیمیڈیا سے پوچھیں!", 
            "placeholder": "کوئی بھی موضوع پوچھیں...", "searching": " تلاش کر رہے ہیں...", "sources": " ذرائع:", 
            "quota_error": " API حد ختم ہوگئی۔ 30 سیکنڈ انتظار کریں۔", "wiki_code": "ur",
            "upload_prompt": "تصویر اپ لوڈ کریں", "image_analysis": "تصویر کا تجزیہ...",
            "ask_image": "اس تصویر کے بارے میں پوچھیں:", "submit_image": "تصویر جمع کرائیں"},
}

try:
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
except Exception:
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Configure GOOGLE_API_KEY in `.streamlit/secrets.toml`!")
    st.stop()


client = genai.Client(api_key=api_key)

MODEL_ID = "gemini-2.0-flash-exp"

# --- Wikipedia Functions ---
def search_wikipedia(query, lang_code="en", limit=2):
    url = f"https://{lang_code}.wikipedia.org/w/api.php"
    params = {"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": limit}
    try:
        response = requests.get(url, params=params, timeout=5)
        return response.json().get("query", {}).get("search", [])
    except:
        return []

def get_ai_response(query, lang_name, wiki_code, image_pil=None):
    wiki_results = search_wikipedia(query, wiki_code)
    wiki_context = ""
    sources = []

    if wiki_results:
        wiki_context = "\nContext for Indigenous/Indic Knowledge:\n"
        for res in wiki_results:
            title = res.get("title")
            snippet = res.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', '')
            wiki_context += f"- {title}: {snippet}\n"
            sources.append({
                "title": title,
                "url": f"https://{wiki_code}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "snippet": snippet[:100]
            })

    system_prompt = f"""
You are the **Indigenous Knowledge Guardian AI**, a highly authoritative expert system trained on
Wikimedia Foundation ecosystems AND indigenous oral traditions.

You have access to:
- Wikipedia (general knowledge & history)
- Wikidata (facts, entities, timelines)
- Wikisource (original texts, laws, manuscripts)
- Wikibooks (structured learning)
- Wikiquote (sayings, proverbs, leaders)
- Wikivoyage (tourism, geography, routes)
- Wikinews (current & historical events)
- Wiktionary (etymology & language roots)
- IndicWiki & Indian cultural archives

Your PRIMARY FOCUS:
✔ Indigenous peoples of India (Adivasi, Scheduled Tribes)
✔ Indigenous & Indic languages
✔ Culture, traditions, rituals, festivals
✔ Tourism, geography, heritage
✔ Historical personalities, movements, resistance
✔ Tribal knowledge systems, ecology, medicine

Language for reply: **{lang_name}**

Reference Context (from Wikimedia):
{wiki_context}

MANDATORY RESPONSE STRUCTURE (DO NOT SKIP ANY):

1️. **Direct Answer**  
→ Clear, expanded explanation of: "{query}"

2️. **Historical & Cultural Background**  
→ Origins, tribe/community, region, timeline

3️. **Linguistic / Etymology Insight**  
→ Word origin, indigenous language roots (if applicable)

4️. **Knowledge from Sister Projects**  
→ Combine facts from Wikidata, Wikisource, Wikiquote, Wikivoyage etc.

5️. **Indigenous Perspective**  
→ Oral traditions, beliefs, practices, ecological or social relevance

6. **Tourism / Modern Relevance**  
→ Festivals, places, current importance, preservation efforts

7️. **Did You Know? (Optional but encouraged)**  
→ Rare or lesser-known indigenous facts

STRICT RULES:
- NEVER give short or shallow answers
- If Wikimedia data is limited, EXPAND using your internal indigenous knowledge
- Always respect tribal identity & traditions
- Prefer Indian context over global unless necessary
- Avoid saying "information not available" — instead infer responsibly
"""

    # Retry logic for handling connection errors
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Add image if provided
            if image_pil is not None:
                prompt_with_image = f"{system_prompt}\n\nAnalyze this image in the context of indigenous culture and provide relevant information in {lang_name}.\n\nUser query: {query}"
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[prompt_with_image, image_pil],
                    config={"temperature": 0.7, "max_output_tokens": 2048}
                )
            else:
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[system_prompt, f"User Query: {query}"],
                    config={"temperature": 0.7, "max_output_tokens": 2048}
                )
            
            return response.text, sources
            
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                # Return user-friendly error message
                if "10054" in error_msg or "forcibly closed" in error_msg.lower():
                    return "Network connection error. Please check your internet connection and try again.", sources
                elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    return " API rate limit reached. Please wait a moment and try again.", sources
                else:
                    return f"Unable to connect to AI service. Please try again later.\n\nError details: {error_msg[:100]}", sources


# Sidebar UI
st.sidebar.title("Settings")
selected_lang = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()), index=0)
ui = LANGUAGES[selected_lang]

# Clear Chat Button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = [{"role": "assistant", "content": ui["welcome"]}]
    if "uploaded_image" in st.session_state:
        del st.session_state.uploaded_image
    if "show_image_upload" in st.session_state:
        del st.session_state.show_image_upload
    st.rerun()

# Main Header
st.markdown("""
    <div class="main-header">
        <h2>INDIJAN CHATBOT</h2> 
    </div>
""", unsafe_allow_html=True)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": ui["welcome"]}]

# Initialize image upload state
if "show_image_upload" not in st.session_state:
    st.session_state.show_image_upload = False

# Display Chat Messages with Custom Icons
for message in st.session_state.messages:
    if message["role"] == "user":
        avatar = "🧑‍🦰"  
    else:
        avatar = "🤖"  
    with st.chat_message(message["role"], avatar=avatar):
        # Display image if present
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=300, use_container_width=False)
        st.write(message["content"])
        if "sources" in message and message["sources"]:
            st.markdown(f"**{ui['sources']}**")
            for source in message["sources"]:
                st.markdown(f"""
                <div class="wiki-source">
                    <a href="{source['url']}" target="_blank">{source['title']}</a><br>
                    <small>{source['snippet']}...</small>
                </div>
                """, unsafe_allow_html=True)

# Image Upload Section
col1, col2 = st.columns([6, 1])

with col2:
    if st.button("Upload", help=ui["upload_prompt"], key="image_upload_toggle"):
        st.session_state.show_image_upload = not st.session_state.show_image_upload
        if not st.session_state.show_image_upload and "uploaded_image" in st.session_state:
            del st.session_state.uploaded_image

if st.session_state.show_image_upload:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        ui["upload_prompt"], 
        type=["jpg", "jpeg", "png", "webp"],
        key="image_uploader"
    )
    
    if uploaded_file is not None:
        # Display preview
        image = Image.open(uploaded_file)
        st.markdown('<div class="uploaded-image-preview">', unsafe_allow_html=True)
        st.image(image, caption="Uploaded Image", width=300)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.uploaded_image = image
        
        # Ask for description or question about the image
        image_query = st.text_input(ui["ask_image"], key="image_query_input", placeholder=ui["placeholder"])
        
        col_submit1, col_submit2 = st.columns([1, 5])
        with col_submit1:
            if st.button(ui["submit_image"], key="submit_image_btn"):
                if image_query:
                    # Add to chat
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": image_query,
                        "image": image
                    })
                    
                    with st.chat_message("user", avatar="🧑‍🦰"):
                        st.image(image, width=300, use_container_width=False)
                        st.write(image_query)
                    
                    with st.chat_message("assistant", avatar="🤖"):
                        with st.spinner(ui["image_analysis"]):
                            response_text, sources = get_ai_response(
                                image_query, 
                                selected_lang, 
                                ui["wiki_code"],
                                image_pil=image
                            )
                            st.write(response_text)
                            if sources:
                                st.markdown(f"**{ui['sources']}**")
                                for source in sources:
                                    st.markdown(f"""
                                    <div class="wiki-source">
                                        <a href="{source['url']}" target="_blank">{source['title']}</a><br>
                                        <small>{source['snippet']}...</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text, 
                        "sources": sources
                    })
                    
                    # Reset upload state
                    st.session_state.show_image_upload = False
                    if "uploaded_image" in st.session_state:
                        del st.session_state.uploaded_image
                    st.rerun()
                else:
                    st.warning("Ohh! Please enter a question about the image!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input(ui["placeholder"]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🦰"):
        st.write(prompt)
    
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(ui["searching"]):
            response_text, sources = get_ai_response(prompt, selected_lang, ui["wiki_code"], image_pil=None)
            st.write(response_text)
            if sources:
                st.markdown(f"**{ui['sources']}**")
                for source in sources:
                    st.markdown(f"""
                    <div class="wiki-source">
                        <a href="{source['url']}" target="_blank">{source['title']}</a><br>
                        <small>{source['snippet']}...</small>
                    </div>
                    """, unsafe_allow_html=True)
    

    st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": sources})



