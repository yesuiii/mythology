import streamlit as st
import google.generativeai as genai
from io import BytesIO
import os
import time
from fpdf import FPDF
import html2text
import json
import re
from urllib.parse import quote_plus 
GOOGLE_API_KEY = "AIzaSyBQgNFqOG01MHtZcCgPdvHZTtBoVjID2IY"  
model = genai.GenerativeModel('gemini-2.0-flash')
try:
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY":
        st.error("🚨 Please set your Google API Key in the GOOGLE_API_KEY variable.")
        st.warning("API Key missing or invalid. AI features will be disabled.")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("Google API Initialized Successfully.") 
except Exception as e:
    st.error(f"Failed to initialize Google API. Error: {e}")
    model = None
translations = {
    "app_title": {
        "en": "Mongolian Mythology Explorer",
        "mn": "Монголын Домог Судлаач"
    },
    "settings_header": {
        "en": "Settings",
        "mn": "Тохиргоо"
    },
    "language_select_label": {
        "en": "Select Language:",
        "mn": "Хэл сонгоно уу:"
    },
    "language_select_radio_label": { 
        "en": "Language / Хэл:",
        "mn": "Language / Хэл:" 
    },
    "lang_english": { 
        "en": "English",
        "mn": "Англи"
    },
    "lang_mongolian": { 
        "en": "Mongolian",
        "mn": "Монгол"
    },
    # --- Tab Names ---
    "tab_chatbot": {
        "en": "Chatbot",
        "mn": "Чатбот"
    },
    "tab_stories": {
        "en": "Stories",
        "mn": "Түүхүүд"
    },
    "tab_insights": {
        "en": "Insights",
        "mn": "Ойлголтууд"
    },
    # --- Other UI Elements ---
    "chatbot_header": {
        "en": "Chatbot",
        "mn": "Чатбот"
    },
    "chatbot_instruction": {
        "en": "Ask the ChatBot anything about Mongolian mythology!",
        "mn": "Чатботоос монгол домгийн зүйлээс хүссэнээ асуугаарай!" 
    },
    "chatbot_input_placeholder": {
        "en": "Your question:",
        "mn": "Таны асуулт:"
    },
    "chatbot_thinking": {
        "en": "Thinking...",
        "mn": "Бодож байна..."
    },
    "chatbot_initial_greeting": {
         "en": "Welcome! I'm here to chat about Mongolian mythology. Feel free to ask me anything about legends, heroes, or creatures. If things get personal, I might ask for your birth year to explore your Mongolian zodiac sign!",
         "mn": "Тавтай морил! Би Монголын домог зүйн талаар ярилцахад бэлэн байна. Домог, баатрууд, амьтдын талаар юу ч асуугаарай. Хэрэв хувийн зүйл яривал, би таны төрсөн оныг асууж, Монгол зурхайн ордны талаар ярилцаж магадгүй шүү!"
    },
    "chatbot_prompt_template": {
        "en": "Answer the user's question: {user_input}. **You MUST answer *only* from the perspective of Mongolian mythology.** Explain things as they are explained in traditional Mongolian myths and legends, even if the question isn't directly about mythology. **Respond in the same language the user used in their question.** If a direct mythological explanation isn't possible, state that Mongolian mythology doesn't specifically address this topic.",
        "mn": "Хэрэглэгчийн асуултад хариулна уу: {user_input}. **Та ЗӨВХӨН Монголын домог зүйн үүднээс хариулах ёстой.** Асуулт нь домог зүйн талаар шууд биш байсан ч гэсэн уламжлалт Монгол домог, үлгэрт тайлбарласны дагуу зүйлийг тайлбарлана уу. **Хэрэглэгчийн асуултад ашигласан хэлээр хариулна уу.** Хэрэв домог зүйн шууд тайлбар боломжгүй бол Монголын домог зүйд энэ сэдвийг тусгайлан авч үздэггүй гэж хэлнэ үү."
    },
    "stories_header": {
        "en": "Mythological Stories",
        "mn": "Домогт Түүхүүд"
    },
    "stories_subheader_selected": {
        "en": "Story: {title}",
        "mn": "Түүх: {title}"
    },
    "stories_narrating": {
        "en": "Narrating the story of '{title}'...",
        "mn": "'{title}' түүхийг өгүүлж байна..."
    },
    "stories_back_button": {
        "en": "⬅️ Back to Stories",
        "mn": "⬅️ Түүх рүү буцах"
    },
    "stories_subheader_choose": {
        "en": "Choose a Story to Read:",
        "mn": "Унших түүхээ сонгоно уу:"
    },
    "stories_fetch_error": {
        "en": "Could not fetch story titles. Please try again later.",
        "mn": "Түүхийн гарчгийг авч чадсангүй. Дараа дахин оролдоно уу."
    },
    "stories_divider_label": {
        "en": "Search a mythical story:",
        "mn": "Домогт түүх хайх:"
    },
    "stories_custom_input_label": {
        "en": "Enter a topic for a Mongolian mythological story:",
        "mn": "Монголын домогт түүхийн сэдвийг оруулна уу:"
    },
    "stories_tell_button": {
        "en": "Enter",
        "mn": "Оруулах" 
    },
    "stories_topic_warning": {
        "en": "Please enter a story topic.",
        "mn": "Түүхийн сэдвийг оруулна уу."
    },
    "insights_header": {
        "en": "Educational Insights",
        "mn": "Боловсролын ойлголтууд"
    },
    "insights_instruction": {
        "en": "Explore specific topics within Mongolian mythology.",
        "mn": "Монголын домгийн хүрээнд тодорхой сэдвүүдийг судлаарай."
    },
    "insights_input_label": {
        "en": "Enter a topic for educational insights:",
        "mn": "Боловсролын ойлголт авах сэдвээ оруулна уу:"
    },
    "insights_get_button": {
        "en": "Enter",
        "mn": "Авах"
    },
    "insights_gathering": {
        "en": "Gathering insights on '{topic}'...",
        "mn": "'{topic}' сэдвээр ойлголт цуглуулж байна..."
    },
    "insights_subheader": {
        "en": "Insights on: {topic}",
        "mn": "Ойлголт: {topic}"
    },
    "insights_topic_warning": {
        "en": "Please enter a topic for insights.",
        "mn": "Ойлголт авах сэдвээ оруулна уу."
    },
    # --- Prompts for Gemini API ---
    "prompt_narrate_story": {
        "en": "Tell the authentic Mongolian mythological story about '{story_topic}'. This MUST be a real, well-known story from Mongolian folklore (like Erkhii Mergen, Khukhuu Namjil, Tsartsaa Namjil etc.). **Start IMMEDIATELY with the story narrative. Do NOT include ANY introductory phrases, explanations, or context before the story begins.** Include accurate cultural details and historical context within the narrative itself. Make it rich in detail, clear, and preserve the authentic narrative style. Respond ONLY in English.",
        "mn": "'{story_topic}' сэдэвтэй холбоотой Монголын домгийн ЖИНХЭНЭ, АЛДАРТАЙ түүхийг ярьж өгнө үү (Жишээ нь: Эрхий Мэргэн, Хөхөө Намжил, Царцаа Намжил гэх мэт). **ТҮҮХИЙН ӨГҮҮЛЭМЖЭЭС ШУУД ЭХЭЛНЭ ҮҮ. Түүх эхлэхээс өмнө ЯМАР Ч ОРШИЛ ҮГ, ТАЙЛБАР, НӨХЦӨЛ БАЙДЛЫГ БҮҮ ОРУУЛ.** Өгүүллэг дотроо соёлын үнэн зөв дэлгэрэнгүй мэдээлэл, түүхэн нөхцөл байдлыг оруулна уу. Мэдээллийг дэлгэрэнгүй, ойлгомжтой, жинхэнэ өгүүлэх хэв маягийг хадгалсан байдлаар бичнэ үү. Зөвхөн Монголоор хариулна уу.",
    },
    "prompt_get_insights": {
        "en": "Provide educational insights about Mongolian mythology, specifically about '{topic}'. Structure the information clearly. Respond ONLY in English.",
        "mn": "Монголын домгийн талаар, ялангуяа '{topic}' сэдвийн хүрээнд боловсролын ойлголт өгнө үү. Мэдээллийг тодорхой бүтэцтэйгээр гаргана уу. Зөвхөн Монголоор хариулна уу.",
    },
    "prompt_get_story_titles": {
        "en": "Provide exactly 6 distinct titles of FAMOUS and AUTHENTIC Mongolian mythological stories (e.g., \'Erkhii Mergen\', \'Khukhuu Namjil\', \'Tsartsaa Namjil\', \'Geser Khan\'). These MUST be real, well-known stories from Mongolian folklore. For each title, provide ONE short, engaging sentence introducing it. Format each entry as 'Title: Engaging sentence', one per line. **ABSOLUTELY NO introduction/explanation before the list.** Just the 6 titles and sentences. Provide the output ONLY in English.",
        "mn": "Монголын АЛДАРТАЙ, ЖИНХЭНЭ домгийн бодит түүхүүдийн (Жишээ нь: \'Эрхий Мэргэн\', \'Хөхөө Намжил\', \'Царцаа Намжил\', \'Гэсэр\', \'Болдоггүй Бор Өвгөн\') яг 6 ялгаатай гарчиг болон тухайн түүхийг унших сонирхол төрүүлэхүйц НЭГ богино өгүүлбэрийг гаргаж өгнө үү. Эдгээр нь Монголын домог, аман зохиолын БОДИТ, ОЛОНД ТАНИГДСАН түүхүүд байх ёстой. Мэдээллийг мөр бүрт 'Гарчиг: Сонирхолтой өгүүлбэр' гэсэн хэлбэрээр жагсаана уу. **ЖАГСААЛТЫН ӨМНӨ ЯМАР Ч ОРШИЛ, ТАЙЛБАР ОРУУЛЖ БОЛОХГҮЙ.** Зөвхөн 6 гарчиг, 6 өгүүлбэр л байна. Зөвхөн Монголоор хариулна уу."
    },
    "prompt_translate_text": {
        "en": "Translate the following text from {source_language_name} to {target_language_name}. Only provide the translated text, without any introductory phrases:\n\n'{text}'",
        "mn": "Дараах текстийг {source_language_name} хэлнээс {target_language_name} хэл рүү орчуулна уу. Зөвхөн орчуулсан текстийг, ямар ч оршил үг хэллэггүйгээр оруулна уу:\n\n'{text}'"
    },
    "translate_button": {
        "en": "Translate to {lang_name}",
        "mn": "{lang_name} руу орчуулах"
    },
    "story_message_button": {
         "en": "📜 Get Message",
         "mn": "📜 Сургамж"
    },
    "prompt_get_story_analysis": {
         "en": "Analyze the Mongolian mythological story about '{story_topic}'. What is its main message or moral? Provide ONLY the message or moral, presented clearly as a short paragraph. Do not include anything else. Respond ONLY in English.",
         "mn": "Монголын домогт '{story_topic}' түүхэнд дүн шинжилгээ хийнэ үү. Үндсэн санаа, сургамж нь юу вэ? ЗӨВХӨН үндсэн санаа эсвэл сургамжийг богино догол мөрөөр тодорхой илэрхийлнэ үү. Өөр юу ч бүү оруул. Respond ONLY in Mongolian.", 
    },
    "story_message_loading": {
         "en": "Getting story message...",
         "mn": "Түүхийн сургамж уншиж байна..."
    },
    "story_message_header": {
         "en": "Message from the Story: {title}",
         "mn": "Түүхийн Зурвас: {title}"
    },
    "message_variability_warning": {
        "en": "💡 Please note: Messages derived from stories can vary, reflecting different interpretations and perspectives, much like people themselves!",
        "mn": "💡 Түүхээс авсан сургамж нь хүн болгонд өөр өөр тул харилцан адилгүй байж болохыг анхаарна уу!"
    },
    "error_tts_api": {
        "en": "Text-to-Speech Error: {error}",
        "mn": "Текстээс-Ярианы Алдаа: {error}"
    },
    "error_gemini_api": {
        "en": "AI Error: {error}",
        "mn": "AI Алдаа: {error}" 
    },
    "error_empty_response": {
        "en": "Received an empty response from the AI.",
        "mn": "Хиймэл оюун ухаанаас хоосон хариу ирлээ."
    },
    "error_unexpected_stop": {
        "en": "AI generation stopped unexpectedly. Details: {details}",
        "mn": "Хиймэл оюун ухааны үйлдэл гэнэт зогслоо. Дэлгэрэнгүй: {details}"
    },
    "error_model_not_initialized": {
        "en": "AI Model not initialized (check API key).",
        "mn": "Хиймэл оюуны загвар бэлтгэгдээгүй (API түлхүүрээ шалгана уу)."
    },
    # --- Sidebar Features ---
    "sidebar_favorites_header": {
        "en": "⭐ Favorites & Bookmarks",
        "mn": "⭐ Дуртай & Хадгалсан"
    },
    "favorites_subheader": {
        "en": "Favorite Stories",
        "mn": "Дуртай Түүхүүд"
    },
    "bookmarks_subheader": {
        "en": "Bookmarked Pages",
        "mn": "Хадгалсан Хуудсууд"
    },
    "no_favorites": {
        "en": "No favorite stories yet.",
        "mn": "Дуртай түүх алга байна."
    },
    "no_bookmarks": {
        "en": "No bookmarked pages yet.",
        "mn": "Хадгалсан хуудас алга байна."
    },
    "add_favorite_button": {
        "en": "❤️ Add to Favorites",
        "mn": "❤️ Дуртайд Нэмэх"
    },
    "remove_favorite_button": {
        "en": "💔 Remove Favorite",
        "mn": "💔 Дуртайгаас Хасах"
    },
    "bookmark_page_button": {
        "en": "🔖 Bookmark Page",
        "mn": "🔖 Хуудас Хадгалах"
    },
    "remove_bookmark_button": {
        "en": "❌ Remove",
        "mn": "❌ Устгах"
    },
    "go_to_story_button": {
        "en": "Read",
        "mn": "Унших"
    },
    "go_to_page_button": {
        "en": "Go to Page {page}",
        "mn": "{page}-р хуудас руу очих"
    },
    "sidebar_glossary_header": {
        "en": "📜 Mythology Glossary",
        "mn": "📜 Домгийн Нэр Томьёо"
    },
    "glossary_loading": {
        "en": "Loading glossary terms...",
        "mn": "Нэр томьёог ачааллаж байна..."
    },
    "no_glossary_terms": {
        "en": "No relevant terms identified for this story yet.",
        "mn": "Энэ түүхэнд холбогдох нэр томьёо одоогоор алга."
    },
    "glossary_fetch_error": {
        "en": "Could not fetch glossary terms.",
        "mn": "Нэр томьёог авч чадсангүй."
    },
    "prompt_get_glossary_terms": {
        "en": (
            "Analyze the following Mongolian mythological story text. Identify the key mythological names (deities, heroes, creatures), "
            "specific cultural concepts, places, or significant items mentioned. For each term identified, provide a concise definition "
            "relevant to Mongolian mythology and its context within the story. Avoid generic definitions. "
            "Format the output strictly as:\n"
            "TERM: DEFINITION\n"
            "TERM: DEFINITION\n"
            "Only include terms directly present in the text. If no specific mythological terms are found, return 'NONE'.\n"
            "Respond ONLY in English.\n\n"
            "Story Text:\n{story_content}"
        ),
        "mn": (
            "Дараах Монголын домогт түүхийн текстийг шинжилнэ үү. Текстэд дурдагдсан домгийн гол нэрс (тэнгэр, баатар, амьтан), "
            "соёлын онцлог ойлголт, газар нэр, эсвэл чухал эд зүйлсийг тодорхойлно уу. Тодорхойлсон нэр томъёо бүрд Монголын домгийн зүй болон "
            "түүхэн дэх утга санаанд нь нийцсэн товч тодорхойлолтыг өгнө үү. Ерөнхий тодорхойлолтоос зайлсхийнэ үү. "
            "Гаралтыг дараах хэлбэрээр яг таг форматлана уу:\n"
            "НЭР ТОМЬЁО: ТОДОРХОЙЛОЛТ\n"
            "НЭР ТОМЬЁО: ТОДОРХОЙЛОЛТ\n"
            "Зөвхөн текстэд шууд байгаа нэр томьёог оруулна уу. Хэрэв тодорхой домгийн нэр томьёо олдсонгүй бол 'NONE' гэж буцаана уу.\n"
            "Respond ONLY in Mongolian.\n\n"
            "Story Text:\n{story_content}"
        )
    }
}

# --- Helper Functions ---

def t(key, lang_code, **kwargs):
    """
    Retrieves a translated string for a given key and language code.
    Handles fallback to English and missing keys gracefully.
    """
    lang_code = lang_code[:2].lower()
    if lang_code not in ['en', 'mn']:
        lang_code = 'en'

    try:
        template = translations[key][lang_code]
        return template.format(**kwargs)
    except KeyError:
        try:
            template = translations[key]['en']
            if lang_code != 'en':
                print(f"Warning: Translation key '{key}' not found for language '{lang_code}', falling back to English.")
            return template.format(**kwargs)
        except KeyError:
            print(f"ERROR: Translation key '{key}' not found for any supported language.")
            return f"[MISSING_KEY: {key}]"
    except Exception as e:
        print(f"Error during translation formatting for key '{key}', lang '{lang_code}': {e}")
        return f"[TRANSLATION_ERROR: {key}]"
def query_brave(query: str) -> str:
    """
    Query Brave for information about a specific topic.

    Args:
        query (str): The topic to search Brave for

    Returns:
        str: A list of web results
    """
    brave = Brave(api_key="BSAP1ZmJl9wMXKDvGnGM78r9__i_VuG")
    num_results = 10
    search_results = brave.search(q=query, count=num_results, raw=True)
    return search_results['web']


def is_error_message(text):
    """Checks if the text likely contains one of our defined error messages or patterns."""
    if not isinstance(text, str):
        return False
    error_keys = [
        "error_gemini_api", "error_tts_api", "error_empty_response",
        "error_unexpected_stop", "[MISSING_KEY:", "[TRANSLATION_ERROR:",
        "AI Generation Error:", "Could not fetch", "Failed to initialize",
        "Received an empty response", "generation stopped unexpectedly",
        "Translation failed", "API Error", "Error generating",
        "Model not initialized", "check API key", "AI Алдаа", 
        "AI Error"
    ]
    text_lower = text.lower()
    return any(key.lower() in text_lower for key in error_keys)

def get_gemini_response(prompt_text, generation_config=None):
    """
    Generates a response from the Gemini API using a prompt string.
    Handles potential errors like missing API key or API call failures.
    Returns the generated text (str) or an error message string.
    """
    ui_lang_code = st.session_state.get('lang_code', 'en') 
    if model is None:
         return t("error_model_not_initialized", ui_lang_code)

    if not isinstance(prompt_text, str):
        print(f"Error: Invalid input type for get_gemini_response. Expected str, got {type(prompt_text)}")
        return t("error_gemini_api", ui_lang_code, error="Invalid prompt type")

    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        response = model.generate_content(
            prompt_text, 
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # --- Process the API Response ---
        full_text = ""
        finish_reason = "UNKNOWN"
        safety_ratings_str = "N/A" 

        try:
            if response.candidates:
                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                if candidate.safety_ratings:
                    safety_ratings_str = ", ".join([f"{r.category.name}: {r.probability.name}" for r in candidate.safety_ratings])

                if candidate.content and candidate.content.parts:
                    full_text = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text')).strip()
            if not full_text and hasattr(response, 'text') and response.text:
                 full_text = response.text.strip()
                 if finish_reason == "UNKNOWN" and response.candidates:
                      candidate = response.candidates[0]
                      finish_reason = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                      if candidate.safety_ratings:
                          safety_ratings_str = ", ".join([f"{r.category.name}: {r.probability.name}" for r in candidate.safety_ratings])


        except (IndexError, AttributeError, KeyError, StopIteration) as e:
            print(f"Error accessing candidate details: {e}. Response: {response}")
            if not full_text and hasattr(response, 'text') and response.text:
                 full_text = response.text.strip()
        if full_text:
            if finish_reason not in ["STOP", "MAX_TOKENS", "UNKNOWN"]:
                details = f"Reason: {finish_reason}, Safety: {safety_ratings_str}"
                print(f"Warning: Gemini generation stopped unexpectedly ({finish_reason}) but returned text. Details: {details}")
            return full_text

        else:
            details = f"Reason: {finish_reason}, Safety: {safety_ratings_str}"
            print(f"Gemini returned empty response or stopped. Details: {details}")
            if finish_reason not in ["STOP", "MAX_TOKENS", "UNKNOWN"]:
                st.warning(t("error_unexpected_stop", ui_lang_code, details=details))
                return t("error_unexpected_stop", ui_lang_code, details=details)
            else:
                st.warning(t("error_empty_response", ui_lang_code))
                return t("error_empty_response", ui_lang_code)
                
    except genai.types.generation_types.BlockedPromptException as bpe:
        st.error(f"AI Error: Prompt was blocked. Details: {bpe}")
        print(f"Gemini API Call Error: Prompt Blocked - {bpe}")
        return t("error_gemini_api", ui_lang_code, error="Prompt blocked by safety filters")
    except Exception as e:
        st.error(t("error_gemini_api", ui_lang_code, error=str(e)))
        print(f"Gemini API Call Error: {e}")
        import traceback
        traceback.print_exc()
        return t("error_gemini_api", ui_lang_code, error=str(e))


def translate_text(text, source_lang_code, target_lang_code):
    """Translates text using the Gemini API."""
    ui_lang_code = st.session_state.get('lang_code', 'en') 

    source_lang_key = "lang_english" if source_lang_code == "en" else "lang_mongolian"
    target_lang_key = "lang_english" if target_lang_code == "en" else "lang_mongolian"

    source_lang_name = t(source_lang_key, ui_lang_code)
    target_lang_name = t(target_lang_key, ui_lang_code)

    prompt = t("prompt_translate_text", ui_lang_code,
               source_language_name=source_lang_name,
               target_language_name=target_lang_name,
               text=text)

    translated = get_gemini_response(prompt)
    return translated

def narrate_story(story_topic, lang_code="en"):
    """Narrates a mythological story using a translated prompt and online search results."""
    search_results = search_story_online(story_topic, lang_code)
    
    context = ""
    if search_results:
        context = f"\n\nRelevant sources found:\n" + "\n".join(search_results[:3])

    prompt = t("prompt_narrate_story", lang_code, story_topic=story_topic)
    
    if context:
        prompt = f"{prompt}\n\nConsider these relevant sources for authenticity:{context}"
    return get_gemini_response(prompt)

def get_educational_insights(topic, lang_code="en"):
    """Provides educational insights using a translated prompt and online search results."""
    search_results = search_insight_online(topic, lang_code)
    context = ""
    if search_results:
        context = f"\n\nRelevant sources found:\n" + "\n".join(search_results[:3])
        print(f"Adding context to insights prompt from search results.")
    prompt = t("prompt_get_insights", lang_code, topic=topic)

    if context:
        prompt = f"{prompt}\n\nPlease use the following sources for reference if helpful:{context}"
    return get_gemini_response(prompt)

def get_story_analysis(story_topic, lang_code="en"):
    """
    Generates the story's message/moral using the Gemini API.
    Uses the prompt asking only for the message in the target language.
    """
    prompt = t("prompt_get_story_analysis", lang_code, story_topic=story_topic)
    return get_gemini_response(prompt)


@st.cache_data(ttl=3600) 
def get_story_titles(_lang_code="en"):
    """
    Generates 6 distinct story titles and intros using Gemini API without any context.
    The prompt asks Gemini to respond ONLY in the specified _lang_code.
    Includes robust parsing and error handling. Caches results based on _lang_code.
    """
    print(f"--- Calling get_story_titles for language: {_lang_code} ---")
    prompt = t("prompt_get_story_titles", _lang_code)
    story_data = []
    try:
        response_text = get_gemini_response(prompt)
        if not response_text or is_error_message(response_text):
             if not is_error_message(response_text):
                 st.warning(f"Received empty response when fetching story titles in {_lang_code}.")
             print(f"API Error or empty response when fetching story titles in {_lang_code}: {response_text}")
             return []
        lines = response_text.strip().split('\n')
        print(f"--- Parsing Story Titles Response ({_lang_code}) ---")
        for line in lines:
            line = line.strip()
            if not line: continue 
            print(f"Parsing line: {line}")
            cleaned_line = re.sub(r"^\s*[\d\.\-\*]+\s*", "", line).strip()
            if not cleaned_line: continue 
            parts = cleaned_line.split(':', 1)

            title = ""
            intro = ""

            if len(parts) == 2:
                potential_title = parts[0].strip()
                potential_intro = parts[1].strip()
                if potential_title and potential_intro:
                    title = potential_title
                    intro = potential_intro
                    print(f"  -> Parsed (Colon): Title='{title}', Intro='{intro}'")
                elif potential_title and not potential_intro:
                    title = potential_title
                    intro = ""
                    print(f"  -> Parsed (Colon, Intro Empty): Title='{title}', Intro=''")
                elif not potential_title and potential_intro:
                    title = potential_intro
                    intro = ""
                    print(f"  -> Warning (Colon, Title Empty): Assigning Intro to Title='{title}', Intro=''")
                else:
                     print(f"  -> Warning (Colon): Both parts empty after stripping line '{line}'")
                     continue
            else:
                title = cleaned_line
                intro = ""
                print(f"  -> Parsed (No Colon): Title='{title}', Intro=''")
            if title:
                 story_data.append({"title": title, "intro": intro})
            else:
                 print(f"  -> Skipping line as no valid title could be extracted: '{line}'")
        if not story_data:
            st.warning(f"Could not parse any valid titles/intros from AI response in {_lang_code}: '{response_text}'")
            return []   

        unique_stories = []
        seen_titles = set()
        for story in story_data:
            normalized_title = story['title'].lower()
            if normalized_title not in seen_titles:
                unique_stories.append(story)
                seen_titles.add(normalized_title)

        print(f"--- Successfully parsed {len(unique_stories)} unique story titles for {_lang_code} ---") 
        return unique_stories[:6]

    except Exception as e:
        st.error(f"Error processing story titles: {e}")
        print(f"Title Processing Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_pdf(story_title, story_pages):
    """Generates a PDF document from the story content using FPDF."""
    class PDF(FPDF):
        _story_title = "Story" 

        def set_story_title(self, title):
            replacements = {''': "'", ''': "'", '"': '"', '"': '"', '—': '--', '–': '-'}
            cleaned_title = title
            for char, replacement in replacements.items():
                cleaned_title = cleaned_title.replace(char, replacement)
            try:
                self._story_title = cleaned_title.encode('latin-1', 'replace').decode('latin-1')
            except Exception as enc_err:
                print(f"Warning: Could not encode title '{title}' to Latin-1 for PDF header. Using fallback. Error: {enc_err}")
                self._story_title = "Story"

        def header(self):
            try:
                 self.set_font('Arial', 'B', 15)
                 self.cell(0, 10, self._story_title, 0, 1, 'C')
                 self.ln(10)
            except Exception as e:
                 print(f"PDF Header Error: {e}. Title used: {self._story_title}")
                 try:
                     self.set_font('Arial', 'B', 15)
                     self.cell(0, 10, "Story", 0, 1, 'C') 
                     self.ln(10)
                 except Exception as fallback_e:
                     print(f"PDF Header Fallback Error: {fallback_e}")

        def footer(self):
            self.set_y(-15)
            try:
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'{self.page_no()}', 0, 0, 'C')
            except Exception as e:
                print(f"PDF Footer Error: {e}")

    FONT_PATH = "NotoSansMongolian-Regular.ttf" 
    FONT_FAMILY = 'NotoSansMongolian'
    FONT_LOADED = False

    pdf = PDF(orientation='P', unit='mm', format='A4')
    try:
        if os.path.exists(FONT_PATH):
            pdf.add_font(FONT_FAMILY, '', FONT_PATH, uni=True) 
            pdf.set_font(FONT_FAMILY, '', 12)
            FONT_LOADED = True
            print(f"Successfully loaded font: {FONT_PATH}")
        else:
            print(f"Warning: Font file not found at {FONT_PATH}. PDF may not display Mongolian characters correctly. Using Arial.")
            FONT_FAMILY = 'Arial' 
            pdf.set_font(FONT_FAMILY, '', 12)
    except Exception as e:
        print(f"Error loading font {FONT_PATH}: {e}. Using Arial fallback.")
        FONT_FAMILY = 'Arial'
        pdf.set_font(FONT_FAMILY, '', 12)

    pdf.set_story_title(story_title) 
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.body_width = 0 

    def clean_text_pdf_body(text):
        """Basic cleaning for PDF body text."""
        if not isinstance(text, str): return ""
        replacements = {
            '"': '"', '"': '"', ''': "'", ''': "'",
            '—': '--', '–': '-', '…': '...', '•': '*',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        text = re.sub(r'<[^>]+>', '', text)
        return text
        
    if not story_pages:
         pdf.multi_cell(0, 6, "No content available for PDF.") 
    else:
        full_story_content = "\n\n".join(story_pages)
        plain_text_raw = h.handle(full_story_content)
        plain_text_cleaned = clean_text_pdf_body(plain_text_raw)
        try:
            pdf.multi_cell(0, 6, plain_text_cleaned)
        except Exception as e:
            print(f"PDF Writing Error: {e}. Content might be truncated or incorrect if using fallback font.")
            if FONT_FAMILY == 'Arial':
                try:
                    pdf.multi_cell(0, 6, plain_text_cleaned.encode('latin-1', 'replace').decode('latin-1'))
                except Exception as fallback_e:
                     print(f"PDF Writing Error (Fallback Encoding Failed): {fallback_e}")
                     pdf.multi_cell(0, 6, "[Content could not be added due to encoding issues]")
            else:
                 pdf.multi_cell(0, 6, "[Content could not be added due to unexpected error]")
        if not plain_text_cleaned.strip().upper().endswith("THE END."):
            pdf.ln(10) 
            try:
                pdf.set_font(FONT_FAMILY, 'I' if FONT_LOADED else '', 12) 
            except RuntimeError:
                 pdf.set_font(FONT_FAMILY, '', 12)
            pdf.cell(0, 6, "THE END.", 0, 1, 'C')
            print("Appended 'THE END.' to the PDF content.")

    try:
        temp_file = os.path.join(os.getcwd(), f"temp_{int(time.time())}.pdf")
        pdf.output(temp_file)
        with open(temp_file, 'rb') as f:
            pdf_bytes = BytesIO(f.read())
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Could not delete temporary PDF file: {e}")
        
        return pdf_bytes
    except Exception as e:
        print(f"Error during final PDF output: {e}")
        pdf_error = FPDF()
        pdf_error.add_page()
        pdf_error.set_font('Arial', '', 12)
        pdf_error.cell(0, 10, f"Error generating PDF: {e}", 0, 1)
        
        temp_error_file = os.path.join(os.getcwd(), f"temp_error_{int(time.time())}.pdf")
        pdf_error.output(temp_error_file)
        
        with open(temp_error_file, 'rb') as f:
            error_bytes = BytesIO(f.read())
            
        try:
            os.remove(temp_error_file)
        except Exception as e:
            print(f"Warning: Could not delete temporary error PDF file: {e}")
            
        return error_bytes


@st.cache_data(ttl=3600)
def get_glossary_for_story(_story_content, _lang_code="en"):
    """
    Fetches and parses glossary terms for the given story content using Gemini.
    The prompt asks Gemini to respond ONLY in the specified _lang_code.
    Returns a dictionary {term: definition} or an empty dict if no terms/error.
    Uses caching to avoid repeated calls for the same story content and language.
    """
    if not _story_content or not isinstance(_story_content, str):
        print("Glossary fetch skipped: Empty or invalid story content.")
        return {}

    print(f"--- Calling get_glossary_for_story for language: {_lang_code} ---") 
    lang_name_key = "lang_english" if _lang_code == "en" else "lang_mongolian"
    lang_name = t(lang_name_key, _lang_code)
    prompt = t("prompt_get_glossary_terms", _lang_code,
               story_content=_story_content,
               language_name=lang_name)

    response_text = get_gemini_response(prompt)
    print(f"--- Glossary Raw Response ({_lang_code}) ---\n{response_text}\n--------------------------------------") # ADDED: Log raw response

    if not response_text or is_error_message(response_text) or response_text.strip().upper() == 'NONE':
        print(f"Glossary fetch: No terms found or error for lang '{_lang_code}'. Response: '{response_text}'")
        return {} 

    glossary = {}
    lines = response_text.strip().split('\n')
    print(f"--- Parsing Glossary Response ({_lang_code}) ---")
    for line in lines:
        parts = line.strip().split(':', 1)
        if len(parts) == 2:
            term = parts[0].strip()
            definition = parts[1].strip()
            if term and definition:
                print(f"  -> Parsed Term: {term}, Definition: {definition}") 
                glossary[term] = definition
        else:
            print(f"  -> Warning: Could not parse glossary line: '{line}'")

    if not glossary:
        print(f"--- Glossary Parsing Result ({_lang_code}): FAILED to parse any terms --- ") 
        return {}

    print(f"--- Glossary Parsing Result ({_lang_code}): Successfully parsed {len(glossary)} terms --- ")
    return glossary

# --- Streamlit App UI ---
def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(layout="wide", page_title="Mongolian Mythology Explorer")
    st.markdown("""
        <style>
        /* --- Book Page Styles (User Provided - Keep as is) --- */
        .book-page { width: 14.8cm; height: 21.0cm; margin: 20px auto; padding: 2cm; background: #F5ECD9; color: #140d07; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative; border: 1px solid #f5e6c8; background-image: linear-gradient(45deg, rgba(0,0,0,.015) 25%, transparent 25%), linear-gradient(-45deg, rgba(0,0,0,.015) 25%, transparent 25%), linear-gradient(45deg, transparent 75%, rgba(0,0,0,.015) 75%), linear-gradient(-45deg, transparent 75%, rgba(0,0,0,.015) 75%), url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise' x='0' y='0'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.1'/%3E%3C/svg%3E"); background-size: 20px 20px, 20px 20px, 20px 20px, 20px 20px, 100px 100px; background-position: 0 0, 0 10px, 10px -10px, -10px 0px, 0 0; overflow: hidden; }
        .book-page::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.95) 0%, transparent 50%), repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.01) 10px, rgba(0,0,0,0.01) 11px), url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise' x='0' y='0'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.05'/%3E%3C/svg%3E"); background-size: 100% 100%, 20px 20px, 100px 100px; pointer-events: none; }
        .book-page::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, transparent 48%, rgba(0,0,0,0.015) 50%, transparent 52%); background-size: 30px 30px; pointer-events: none; }
        .book-container { display: flex; flex-direction: column; align-items: center; padding: 0 20px; }
        .story-content { font-size: 16px; line-height: 1.6; text-align: justify; position: relative; z-index: 1; font-family: 'Georgia', serif; color: #140d07; }
        .story-content p, .story-content div, .story-content span { font-size: 16px; margin-bottom: 1em; color: #140d07; font-family: 'Georgia', serif; line-height: 1.6; text-align: justify; }
        .story-content h1, .story-content h2, .story-content h3, .story-content h4, .story-content h5, .story-content h6 { font-size: 1.2em; font-weight: bold; margin-bottom: 1em; color: #140d07; font-family: 'Georgia', serif; text-align: left; }
        .story-content strong, .story-content b { font-weight: bold; font-size: 16px; color: #140d07; }
        .story-content em, .story-content i { font-style: italic; font-size: 16px; color: #140d07; }
        .page-number { position: absolute; bottom: 1cm; right: 2cm; font-size: 14px; color: #140d07; z-index: 1; font-family: 'Georgia', serif; }
        .title-page { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; text-align: center; padding: 2cm; }
        .title-text { font-size: 32px; font-weight: bold; margin-bottom: 20px; color: #140d07; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); text-align: center; width: 100%; font-family: 'Georgia', serif; }
        .subtitle-text { font-size: 18px; color: #140d07; opacity: 0.8; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); text-align: center; width: 100%; font-family: 'Georgia', serif; }
        /* --- End Book Page Styles --- */

        /* Styling for Sidebar Buttons */
        .st-emotion-cache-1zhiv0 { /* Target sidebar button container */
             width: 100%; /* Make button container full width */
        }
        .st-emotion-cache-1zhiv0 button { /* Target button element */
            width: 100%; /* Make button itself full width */
            margin-bottom: 5px;
            text-align: left; /* Align text left */
            justify-content: flex-start; /* Align icon/text start */
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            border: 1px solid #ccc; /* Add subtle border */
            background-color: #f0f2f6; /* Light background */
        }
        .st-emotion-cache-1zhiv0 button:hover {
            background-color: #e6e8eb; /* Slightly darker on hover */
        }

        /* Style remove buttons (trash icon) in sidebar */
        /* Use a more specific selector if possible, otherwise rely on icon/text */
        .st-emotion-cache-1zhiv0 button:has(span[aria-label*="delete" i]), /* Check for delete icon */
        .st-emotion-cache-1zhiv0 button:has(span:contains("🗑️")) /* Check for trash emoji */
        {
             background-color: #ffcbcb !important; /* Lighter red */
             color: #a60000 !important; /* Darker red text */
             border: 1px solid #ffaaaa !important;
        }
         .st-emotion-cache-1zhiv0 button:has(span[aria-label*="delete" i]):hover,
         .st-emotion-cache-1zhiv0 button:has(span:contains("🗑️")):hover
         {
              background-color: #ffaaaa !important; /* Slightly darker red on hover */
              color: #a60000 !important;
         }
        </style>
    """, unsafe_allow_html=True)

    if "lang_code" not in st.session_state:
        st.session_state.lang_code = "en" 

    col1_title, col2_lang_selector = st.columns([0.8, 0.2])

    with col1_title:
        st.title(t("app_title", st.session_state.lang_code))

    with col2_lang_selector:
        selected_lang = st.radio(
            label=t("language_select_radio_label", st.session_state.lang_code),
            options=["en", "mn"],
            format_func=lambda x: t("lang_english" if x == "en" else "lang_mongolian", st.session_state.lang_code),
            key="language_selector_main", 
            horizontal=True, 
            index=0 if st.session_state.lang_code == "en" else 1,
            label_visibility="collapsed"
        )

        # --- Handle Language Change ---
        if selected_lang != st.session_state.lang_code:
            print(f"--- Language Change Detected: Translating in place ---")
            source_lang = st.session_state.lang_code
            target_lang = selected_lang
            print(f"Translating content from: {source_lang} -> To: {target_lang}")
            target_lang_key = "lang_english" if target_lang == "en" else "lang_mongolian"
            target_lang_name = t(target_lang_key, target_lang) 

            with st.spinner(f"Translating content to {target_lang_name}... Please wait."):
                def safe_translate(text, s_lang, t_lang, context=""):
                    if not text or not isinstance(text, str):
                        return text 
                    print(f"Translating {context}: '{text[:50]}...' from {s_lang} to {t_lang}")
                    translated = translate_text(text, s_lang, t_lang)
                    if translated and not is_error_message(translated):
                        print(f" -> Success: '{translated[:50]}...'")
                        return translated
                    else:
                        print(f" -> Warning: Failed to translate {context}. Error: {translated}. Keeping original.")
                        return text 

                # 1. Story Title
                st.session_state.selected_story_title = safe_translate(
                    st.session_state.selected_story_title, source_lang, target_lang, "Story Title"
                )

                # 2. Story Content (Pages)
                if st.session_state.story_pages:
                    print("Translating story pages...")
                    translated_pages = [
                        safe_translate(page, source_lang, target_lang, f"Story Page {i+1}")
                        for i, page in enumerate(st.session_state.story_pages)
                    ]
                    st.session_state.story_pages = translated_pages
                    st.session_state.story_content = "\\n\\n".join(translated_pages)
                    st.session_state.story_language = target_lang 
                    st.session_state.story_glossary_data = None
                    st.session_state.glossary_terms_for_display = {}
                    st.session_state.glossary_loading_error = False
                    print("Story content translation complete.")

                # 3. Story Analysis
                st.session_state.story_analysis_content = safe_translate(
                    st.session_state.story_analysis_content, source_lang, target_lang, "Story Analysis"
                )

                # 4. Insight Topic
                st.session_state.current_insight_topic = safe_translate(
                    st.session_state.current_insight_topic, source_lang, target_lang, "Insight Topic"
                )

                # 5. Insight Content
                if st.session_state.insight_content:
                    st.session_state.insight_content = safe_translate(
                         st.session_state.insight_content, source_lang, target_lang, "Insight Content"
                    )
                    st.session_state.insight_language = target_lang 

                # 6. Favorites (Titles)
                if st.session_state.favorites:
                    print("Translating favorites...")
                    st.session_state.favorites = [
                        safe_translate(title, source_lang, target_lang, f"Favorite Title '{title[:20]}...'")
                        for title in st.session_state.favorites
                    ]

                # 7. Bookmarks (Titles)
                if st.session_state.bookmarks:
                     print("Translating bookmarks...")
                     translated_bookmarks = []
                     for bm in st.session_state.bookmarks:
                         title = bm.get('title')
                         page = bm.get('page')
                         translated_title = safe_translate(title, source_lang, target_lang, f"Bookmark Title '{title[:20]}...'")
                         translated_bookmarks.append({'title': translated_title, 'page': page})
                     st.session_state.bookmarks = translated_bookmarks

                # 8. Glossary Definitions
                if st.session_state.glossary_terms_for_display:
                     print("Translating glossary definitions...")
                     translated_glossary = {
                         term: safe_translate(definition, source_lang, target_lang, f"Glossary Definition for '{term}'")
                         for term, definition in st.session_state.glossary_terms_for_display.items()
                     }
                     st.session_state.glossary_terms_for_display = translated_glossary

                # 9. Chat History
                if st.session_state.chat_history:
                    print("Skipping.")
            st.session_state.lang_code = target_lang 

    lang_code = st.session_state.lang_code
    default_states = {
        'selected_story_title': None,
        'story_content': "", 
        'story_language': lang_code, 
        'current_page': 0, 
        'story_pages': [], 
        'story_analysis_content': "", 
        'show_story_analysis': False, 
        'chat_history': [], 
        'insight_content': "", 
        'insight_language': lang_code,
        'current_insight_topic': None, 
        'insight_image_url': None, 
        'show_share_options': False, 
        'favorites': [], 
        'bookmarks': [], 
        'story_glossary_data': None, 
        'glossary_terms_for_display': {}, 
        'glossary_loading_error': False 
    }
    for key, default_value in default_states.items():
        st.session_state.setdefault(key, default_value)
    if not model:
        st.error("Gemini model could not be initialized. Please check your API key configuration at the top.")
        st.stop() 
    with st.sidebar:
        st.header(t("sidebar_favorites_header", lang_code)) 

        # Display Favorite Stories
        st.subheader(t("favorites_subheader", lang_code))
        if not st.session_state.favorites:
            st.caption(t("no_favorites", lang_code))
        else:
            favorites_copy = st.session_state.favorites[:]
            for i, fav_title in enumerate(favorites_copy):
                fav_key_base = f"fav_{i}_{fav_title[:10]}"
                cols_fav = st.columns([0.8, 0.2])
                with cols_fav[0]:
                     if st.button(f"{fav_title}", key=f"{fav_key_base}_read", help=t("go_to_story_button", lang_code), use_container_width=True):
                         print(f"Navigating to favorite story: {fav_title}")
                         st.session_state.story_glossary_data = None
                         st.session_state.glossary_terms_for_display = {}
                         st.session_state.glossary_loading_error = False
                         st.session_state.current_page = 0
                         st.session_state.story_content = "" 
                         st.session_state.story_pages = []
                         st.session_state.story_analysis_content = ""
                         st.session_state.show_story_analysis = False
                         st.session_state.selected_story_title = fav_title
                         st.session_state.story_language = lang_code
                         st.rerun()
                with cols_fav[1]:
                     if st.button("🗑️", key=f"{fav_key_base}_remove", help=t("remove_favorite_button", lang_code), use_container_width=True):
                         print(f"Removing favorite: {fav_title}")
                         try: st.session_state.favorites.remove(fav_title)
                         except ValueError: print(f"Error removing favorite: '{fav_title}' not found.")
                         st.rerun()

        # Display Bookmarked Pages
        st.subheader(t("bookmarks_subheader", lang_code))
        if not st.session_state.bookmarks:
            st.caption(t("no_bookmarks", lang_code))
        else:
            bookmarks_copy = st.session_state.bookmarks[:] 
            for i, bookmark in enumerate(bookmarks_copy):
                bm_title = bookmark.get('title', 'Unknown Title')
                bm_page = bookmark.get('page', 0) 
                bm_key_base = f"bm_{i}_{bm_title[:10]}_{bm_page}"
                cols_bm = st.columns([0.8, 0.2])
                with cols_bm[0]:
                     button_label = f"{bm_title[:25]}... (P.{bm_page + 1})" 
                     if st.button(button_label, key=f"{bm_key_base}_goto", help=t("go_to_page_button", lang_code, page=bm_page + 1), use_container_width=True):
                         print(f"Navigating to bookmark: {bm_title}, Page: {bm_page + 1}")
                         if st.session_state.selected_story_title != bm_title:
                             print("Switching stories via bookmark, resetting content...")
                             st.session_state.story_glossary_data = None
                             st.session_state.glossary_terms_for_display = {}
                             st.session_state.glossary_loading_error = False
                             st.session_state.story_content = "" 
                             st.session_state.story_pages = []
                             st.session_state.story_analysis_content = ""
                             st.session_state.show_story_analysis = False
                             st.session_state.story_language = lang_code
                         st.session_state.selected_story_title = bm_title
                         st.session_state.current_page = bm_page
                         st.rerun()
                with cols_bm[1]:
                     if st.button("🗑️", key=f"{bm_key_base}_remove", help=t("remove_bookmark_button", lang_code), use_container_width=True):
                         print(f"Removing bookmark: {bookmark}")
                         try: st.session_state.bookmarks.remove(bookmark)
                         except ValueError: print(f"Error removing bookmark: {bookmark} not found.")
                         st.rerun()

        # --- Mythology Glossary Section ---
        st.divider()
        st.header(t("sidebar_glossary_header", lang_code))
        if st.session_state.selected_story_title:
            if st.session_state.story_glossary_data is None and not st.session_state.glossary_loading_error:
                 st.caption(t("glossary_loading", lang_code))
            elif st.session_state.glossary_loading_error:
                 st.error(t("glossary_fetch_error", lang_code))
            elif not st.session_state.glossary_terms_for_display:
                st.caption(t("no_glossary_terms", lang_code))
            else:
                sorted_terms = sorted(st.session_state.glossary_terms_for_display.items())
                if sorted_terms:
                    with st.expander(t("sidebar_glossary_header", lang_code), expanded=True):
                        for term, definition in sorted_terms:
                            st.markdown(f"**{term}:** {definition}")
                else:
                     st.caption(t("no_glossary_terms", lang_code))
        else:
            st.caption("Select a story to see relevant terms.")
    tab_keys = ["tab_chatbot", "tab_stories", "tab_insights"]
    tab_labels = [t(key, lang_code) for key in tab_keys]

    try:
        tab1, tab2, tab3 = st.tabs(tab_labels)
    except Exception as e:
        st.error(f"Error creating tabs: {e}. Labels: {tab_labels}")
        st.stop()


    # --- Tab 1: Chatbot ---
    with tab1:
        st.header(t("chatbot_header", lang_code))
        st.write(t("chatbot_instruction", lang_code))
        if not st.session_state.chat_history:
            initial_greeting = t("chatbot_initial_greeting", lang_code)
            st.session_state.chat_history.append({"role": "assistant", "content": initial_greeting})
            print("Added initial chatbot greeting.")

        chat_container = st.container(height=400, border=True)
        with chat_container:
            for message in st.session_state.chat_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                if not isinstance(content, str): content = str(content)
                with st.chat_message(role):
                    st.markdown(content)

        user_input = st.chat_input(t("chatbot_input_placeholder", lang_code))

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            print(f"User input appended to chat history: {user_input}")
            chatbot_prompt = t("chatbot_prompt_template", lang_code, user_input=user_input)
            system_instruction = (
                f"You are an expert assistant specializing *exclusively* in Mongolian Mythology. "
                f"Your primary function is to answer questions only through the lens of Mongolian myths, legends, and folklore. "
                f"You are a helpful and polite assistant, you are simple and easy to understand. Do not overshare.  "
                f"**Strictly adhere to the instruction in the user prompt to respond in the user's language and provide answers based *solely* on Mongolian mythology.** " 
                f"The overall UI language is currently set to {t('lang_english' if lang_code == 'en' else 'lang_mongolian', lang_code)}."
            )
            
            formatted_history_for_api = [
                 {"role": "user", "parts": [{"text": system_instruction}]},
                 {"role": "model", "parts": [{"text": "Okay, I understand the context."}]} 
            ]
            
            history_to_include = st.session_state.chat_history[:-1] 
            for msg in history_to_include:
                role = "model" if msg.get("role") == "assistant" else "user"
                content = msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    formatted_history_for_api.append({"role": role, "parts": [{"text": content}]})
                else:
                     print(f"Skipping invalid message in chat history: {msg}")

            formatted_history_for_api.append({"role": "user", "parts": [{"text": chatbot_prompt}]})


            with st.spinner(t("chatbot_thinking", lang_code)):
                if model:
                    try:
                        print("\\n--- Sending Request to Gemini API ---")
                        response = model.generate_content(
                            formatted_history_for_api, 
                            safety_settings=[
                                {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"} for c in [
                                    "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                                    "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"
                                ]
                            ]
                        )
                      
                        assistant_response = ""
                        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                            assistant_response = "".join(part.text for part in response.candidates[0].content.parts).strip()
                        elif hasattr(response, 'text') and response.text:
                            assistant_response = response.text.strip()
                            
                        if not assistant_response:
                             assistant_response = t("error_empty_response", lang_code)
                             
                    except Exception as e:
                        print(f"Error calling Gemini for chat: {e}")
                        assistant_response = t("error_gemini_api", lang_code, error=str(e))
                else:
                    assistant_response = t("error_model_not_initialized", lang_code)

            if assistant_response and isinstance(assistant_response, str) and not is_error_message(assistant_response):
                 st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                 print(f"Assistant response appended: {assistant_response[:100]}...")
            else:
                 error_content = assistant_response if is_error_message(assistant_response) else t("error_gemini_api", lang_code, error="Unknown error")
                 st.session_state.chat_history.append({"role": "assistant", "content": f"*[System: {error_content}]*"})
                 print(f"Appended error message to chat: {error_content}")

            st.rerun()


    # --- Tab 2: Stories ---
    with tab2:
        st.header(t("stories_header", lang_code))
        if st.session_state.selected_story_title:
            current_title = st.session_state.selected_story_title
            print(f"--- Entering Story View ---")
            print(f"Selected Title: {current_title}")
            print(f"Current UI Lang Code: {lang_code}")
            print(f"Expected Story Lang (from state): {st.session_state.story_language}")
            print(f"Story Content Exists: {bool(st.session_state.story_content)}")

            needs_loading = (
                not st.session_state.story_content or
                st.session_state.story_language != lang_code 
            )
            if needs_loading:
                 print(f"--- Loading Required ---")
                 print(f"Reason: Content Empty? {not st.session_state.story_content}, Lang Mismatch? {st.session_state.story_language != lang_code}")

            if needs_loading:
                with st.spinner(t("stories_narrating", lang_code, title=current_title)):
                    print(f"Narrating '{current_title}' in language: {lang_code}")
                    st.session_state.story_language = lang_code 
                    narrated_content = narrate_story(current_title, lang_code)

                    if narrated_content and not is_error_message(narrated_content):
                        print(f"Narration successful for '{current_title}' in {lang_code}.")
                        st.session_state.story_content = narrated_content
                        st.session_state.story_pages = [] 
                        st.session_state.current_page = 0 
                        st.session_state.glossary_terms_for_display = {}
                        st.session_state.glossary_loading_error = False
                        st.session_state.story_analysis_content = ""
                        st.session_state.show_story_analysis = False
                        
                        print(f"Fetching glossary for '{current_title}' in {lang_code}...")
                        glossary_data = get_glossary_for_story(narrated_content, lang_code)
                        if glossary_data is None:
                            st.session_state.story_glossary_data = {}
                            st.session_state.glossary_loading_error = True
                            st.warning(t("glossary_fetch_error", lang_code))
                            print(f"Error fetching glossary for '{current_title}'.")
                        else:
                             st.session_state.story_glossary_data = glossary_data
                             st.session_state.glossary_loading_error = False
                             print(f"Loaded {len(glossary_data)} glossary terms for '{current_title}'.")
                        print("Paginating story content...")
                        paragraphs = narrated_content.split('\n\n')
                        current_page_text_list = []
                        current_length = 0
                        CHARS_PER_PAGE = 1200
                        MIN_CHARS_PER_PAGE = 800
                        for i, paragraph in enumerate(paragraphs):
                            para_len = len(paragraph)
                            is_last_paragraph = (i == len(paragraphs) - 1)
                            if current_length > 0 and current_length + para_len > CHARS_PER_PAGE:
                                if current_length >= MIN_CHARS_PER_PAGE or para_len > CHARS_PER_PAGE:
                                    st.session_state.story_pages.append("\n\n".join(current_page_text_list))
                                    current_page_text_list = [paragraph]
                                    current_length = para_len
                                else:
                                    current_page_text_list.append(paragraph)
                                    current_length += para_len
                            else:
                                current_page_text_list.append(paragraph)
                                current_length += para_len
                            if is_last_paragraph and current_page_text_list:
                                st.session_state.story_pages.append("\n\n".join(current_page_text_list))
                        if st.session_state.story_pages and not st.session_state.story_pages[-1].strip().upper().endswith("THE END."):
                             st.session_state.story_pages[-1] += "\n\nTHE END."
                             print("Appended 'THE END.' to the last page of the story.")
                             
                        print(f"Paginated story into {len(st.session_state.story_pages)} pages.")
                        st.session_state.current_page = 0
                        print("--- Rerunning after successful story load ---")
                        st.rerun()

                    else: 
                        print(f"Narration failed for '{current_title}' in {lang_code}.")
                        st.session_state.story_content = ""
                        st.session_state.story_pages = []
                        st.session_state.current_page = 0
                        st.session_state.story_glossary_data = {}
                        st.session_state.glossary_terms_for_display = {}
                        error_msg = narrated_content if is_error_message(narrated_content) else "Unknown narration error."
                        st.error(f"Failed to narrate story '{current_title}': {error_msg}")
                        if st.button(t("stories_back_button", lang_code), key="back_to_home_narrate_error"):
                            st.session_state.selected_story_title = None
                            st.rerun()

            # --- Display Story Book ---
            if st.session_state.story_content and st.session_state.story_pages is not None:
                total_content_pages = len(st.session_state.story_pages)
                total_book_pages = total_content_pages + 1
                st.subheader(t("stories_subheader_selected", lang_code, title=current_title))

                # --- Update Sidebar Glossary ---
                if st.session_state.current_page > 0:
                    current_page_index = st.session_state.current_page - 1
                    if 0 <= current_page_index < total_content_pages:
                        page_text = st.session_state.story_pages[current_page_index]
                        if st.session_state.story_glossary_data:
                            terms_added = False
                            for term, definition in st.session_state.story_glossary_data.items():
                                if term in page_text and term not in st.session_state.glossary_terms_for_display:
                                    st.session_state.glossary_terms_for_display[term] = definition
                                    terms_added = True
                            if terms_added:
                                print("Glossary terms updated, rerunning sidebar...")
                                st.rerun()

                # --- Book Display ---
                st.markdown('<div class="book-container">', unsafe_allow_html=True)
                if st.session_state.current_page == 0: # Title Page
                    st.markdown(f'''
                        <div class="book-page">
                            <div class="title-page"> <div class="title-text">{current_title}</div> <div class="subtitle-text">Mongolian Mythology</div> </div>
                            <div class="page-number">1/{total_book_pages}</div>
                        </div>''', unsafe_allow_html=True)
                else: # Content Page
                    current_page_index = st.session_state.current_page - 1
                    if 0 <= current_page_index < total_content_pages:
                         content_html = st.session_state.story_pages[current_page_index].replace('\n', '<br>')
                         st.markdown(f'''
                            <div class="book-page">
                                <div class="story-content">{content_html}</div>
                                <div class="page-number">{st.session_state.current_page + 1}/{total_book_pages}</div>
                            </div>''', unsafe_allow_html=True)
                    else: st.error(f"Error: Invalid page index {current_page_index}.")
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                nav_cols = st.columns([1, 3, 1])
                with nav_cols[0]: 
                    if st.button("⬅️ Previous", key="prev_page", use_container_width=True, disabled=(st.session_state.current_page == 0)):
                        st.session_state.current_page -= 1; st.rerun()
                with nav_cols[1]:
                    page_opts = list(range(total_book_pages))
                    def fmt_page(idx): return "Title Page" if idx == 0 else f"Page {idx + 1}"
                    sel_page = st.selectbox("Jump:", page_opts, format_func=fmt_page, index=st.session_state.current_page, key="page_selector", label_visibility="collapsed")
                    if sel_page != st.session_state.current_page: st.session_state.current_page = sel_page; st.rerun()
                with nav_cols[2]: # Next
                    if st.button("Next ➡️", key="next_page", use_container_width=True, disabled=(st.session_state.current_page == total_content_pages)):
                        st.session_state.current_page += 1; st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

                # --- Action Buttons Row 1 ---
                action_cols1 = st.columns(5)
                with action_cols1[0]: # Home
                    if st.button(t("stories_back_button", lang_code), key="back_to_home", use_container_width=True):
                        st.session_state.selected_story_title = None; st.session_state.story_content = ""; st.session_state.story_pages = []; st.session_state.current_page = 0; st.session_state.story_analysis_content = ""; st.session_state.show_story_analysis = False; st.session_state.story_glossary_data = None; st.session_state.glossary_terms_for_display = {}; st.session_state.glossary_loading_error = False; st.rerun()
                with action_cols1[1]: # Favorite
                    is_fav = current_title in st.session_state.favorites
                    fav_lbl = t("remove_favorite_button", lang_code) if is_fav else t("add_favorite_button", lang_code)
                    if st.button(fav_lbl, key="toggle_favorite", use_container_width=True):
                        if is_fav: st.session_state.favorites.remove(current_title)
                        else: st.session_state.favorites.append(current_title)
                        st.rerun()
                with action_cols1[2]: # Bookmark
                    can_bm = st.session_state.current_page > 0
                    bm_lbl = t("bookmark_page_button", lang_code)
                    if can_bm:
                        page_idx = st.session_state.current_page 
                        bm_exists = any(b.get('title') == current_title and b.get('page') == page_idx for b in st.session_state.bookmarks)
                        bm_disabled = bm_exists
                        bm_help = "Page already bookmarked" if bm_disabled else "Bookmark this page"
                        if st.button(bm_lbl, key="add_bookmark", use_container_width=True, disabled=bm_disabled, help=bm_help):
                            st.session_state.bookmarks.append({'title': current_title, 'page': page_idx}); st.rerun()
                    else: st.button(bm_lbl, key="add_bookmark_disabled_title", use_container_width=True, disabled=True, help="Cannot bookmark title page")
                with action_cols1[4]: # Share
                    if st.button("📤 Share", key="share_story", use_container_width=True):
                        st.session_state.show_share_options = not st.session_state.show_share_options; st.rerun()

                # --- Action Buttons Row 2 & Panels ---
                action_cols2 = st.columns(2)
                with action_cols2[0]: # Get Message
                    if st.button(t("story_message_button", lang_code), key="story_message", use_container_width=True):
                        st.session_state.show_story_analysis = not st.session_state.show_story_analysis
                        if st.session_state.show_story_analysis and not st.session_state.story_analysis_content:
                            with st.spinner(t("story_message_loading", lang_code)):
                                msg_res = get_story_analysis(current_title, st.session_state.story_language) 
                                if msg_res and not is_error_message(msg_res): st.session_state.story_analysis_content = msg_res
                                else: st.warning(msg_res or "Could not get message."); st.session_state.story_analysis_content = ""; st.session_state.show_story_analysis = False
                        st.rerun()
                with action_cols2[1]: # PDF
                    try:
                        pdf_bytes = generate_pdf(current_title, st.session_state.story_pages)
                        safe_fn = re.sub(r'[^\w\.-]+', '_', current_title) + ".pdf"
                        st.download_button("📥 PDF", pdf_bytes, safe_fn, "application/pdf", key="download_pdf", use_container_width=True)
                    except Exception as e: st.button("📥 PDF", key="download_pdf_disabled", use_container_width=True, disabled=True, help=f"PDF Error: {e}"); st.error(f"PDF Error: {e}")

                # --- Conditional Panels ---
                if st.session_state.show_share_options: # Share
                    st.markdown("---"); st.markdown("#### Share Options")
                    base_url = "https://your-streamlit-app-url.com"; # Placeholder
                    try: enc_title = quote_plus(current_title)
                    except NameError: enc_title = re.sub(r'\s+', '+', current_title)
                    share_url = f"{base_url}/?story={enc_title}"; share_text = f"Check out: {current_title}"
                    scols = st.columns(3)
                    scols[0].link_button("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={share_url}&quote={share_text}", use_container_width=True)
                    scols[1].link_button("Twitter / X", f"https://twitter.com/intent/tweet?url={share_url}&text={share_text}", use_container_width=True)
                    scols[2].link_button("LinkedIn", f"https://www.linkedin.com/shareArticle?mini=true&url={share_url}&title={current_title}&summary={share_text}", use_container_width=True)
                    st.text_input("Copy Link:", share_url, key="share_link_text", disabled=True)
                if st.session_state.show_story_analysis and st.session_state.story_analysis_content: # Message
                    st.markdown("---"); expander_lbl = t("story_message_header", lang_code, title=current_title)
                    with st.expander(expander_lbl, expanded=True):
                        st.markdown(st.session_state.story_analysis_content); st.info(t("message_variability_warning", lang_code))

            # --- Handle loading failure ---
            elif st.session_state.selected_story_title and not st.session_state.story_content and needs_loading:
                 st.warning("Story content could not be loaded.");
                 if st.button(t("stories_back_button", lang_code), key="back_to_home_load_error"): st.session_state.selected_story_title = None; st.rerun()

        # === Story Selection View ===
        else:
            print("--- Entering Story Selection View ---")
            if st.session_state.story_glossary_data is not None or st.session_state.glossary_terms_for_display:
                st.session_state.story_glossary_data = None; st.session_state.glossary_terms_for_display = {}; st.session_state.glossary_loading_error = False

            # --- Custom Story Input ---
            st.subheader(t("stories_divider_label", lang_code))
            with st.form(key="custom_story_form"):
                custom_topic = st.text_input(t("stories_custom_input_label", lang_code), key="custom_story_input")
                submitted = st.form_submit_button(t("stories_tell_button", lang_code))
                if submitted:
                    clean_topic = custom_topic.strip()
                    if clean_topic:
                        st.session_state.selected_story_title = clean_topic
                        st.session_state.story_content = ""; st.session_state.story_pages = []; st.session_state.current_page = 0; st.session_state.story_analysis_content = ""; st.session_state.show_story_analysis = False; st.session_state.story_language = lang_code; st.session_state.story_glossary_data = None; st.session_state.glossary_terms_for_display = {}; st.session_state.glossary_loading_error = False; st.rerun()
                    else: st.warning(t("stories_topic_warning", lang_code))
            st.divider()

            # --- Recommended Stories ---
            st.subheader(t("stories_subheader_choose", lang_code))
            print(f"Fetching recommended story titles for language: {lang_code}")
            recommended_stories = get_story_titles(lang_code) 
            if not recommended_stories: st.warning(t("stories_fetch_error", lang_code))
            else:
                cols = st.columns(3)
                for i, story in enumerate(recommended_stories):
                    with cols[i % 3]:
                        with st.container(border=True):
                            title = story.get('title', 'Untitled')
                            intro = story.get('intro', 'Read story') 
                            btn_key = f"story_rec_{lang_code}_{i}_{title[:20]}"
                            if st.button(f"**{title}**", key=btn_key, use_container_width=True, help=intro):
                                st.session_state.selected_story_title = title
                                st.session_state.story_content = ""; st.session_state.story_pages = []; st.session_state.current_page = 0; st.session_state.story_analysis_content = ""; st.session_state.show_story_analysis = False; st.session_state.story_language = lang_code; st.session_state.story_glossary_data = None; st.session_state.glossary_terms_for_display = {}; st.session_state.glossary_loading_error = False; st.rerun()
                            st.caption(intro)

    # --- Tab 3: Insights ---
    with tab3:
        st.header(t("insights_header", lang_code))
        st.write(t("insights_instruction", lang_code))
        with st.form(key="insight_form"):
            insight_topic = st.text_input(t("insights_input_label", lang_code), key="insight_topic_input", value=st.session_state.get("current_insight_topic", ""))
            submitted = st.form_submit_button(t("insights_get_button", lang_code))
            if submitted:
                clean_topic = insight_topic.strip()
                if clean_topic:
                    topic_changed = st.session_state.current_insight_topic != clean_topic
                    lang_changed = st.session_state.insight_language != lang_code
                    if topic_changed or lang_changed or not st.session_state.insight_content:
                        st.session_state.current_insight_topic = clean_topic
                        st.session_state.insight_language = lang_code 
                        st.session_state.insight_content = ""
                        st.session_state.insight_image_url = None 
                        with st.spinner(t("insights_gathering", lang_code, topic=clean_topic)):
                            fetched_insight = get_educational_insights(clean_topic, lang_code)
                            fetched_image_url = search_image_online(clean_topic, lang_code)
                            
                        if fetched_insight and not is_error_message(fetched_insight):
                             st.session_state.insight_content = fetched_insight
                        else: 
                            st.warning(fetched_insight or "Could not get insights.")
                            st.session_state.insight_content = ""
                            
                        if fetched_image_url:
                            st.session_state.insight_image_url = fetched_image_url
                        else:
                            print("No image found for insight topic.")
                            st.session_state.insight_image_url = None 
                            
                        st.rerun() 
                else: 
                    st.session_state.current_insight_topic = None
                    st.session_state.insight_content = ""
                    st.session_state.insight_image_url = None
                    st.warning(t("insights_topic_warning", lang_code))
                    st.rerun()

        if st.session_state.current_insight_topic and st.session_state.insight_content:
            st.subheader(t("insights_subheader", lang_code, topic=st.session_state.current_insight_topic))
            
            if st.session_state.insight_image_url:
                try:
                    image_caption = f"Image related to {st.session_state.current_insight_topic}"
                    st.image(st.session_state.insight_image_url, caption=image_caption, use_column_width=True)
                except Exception as img_err:
                    st.warning(f"Could not load image: {img_err}")
                    print(f"Error loading image URL {st.session_state.insight_image_url}: {img_err}")
            insight_area = st.container(border=True)
            insight_area.markdown(st.session_state.insight_content)

from googlesearch import search

def search_story_online(story_title, lang_code="en"):
    """
    Search for a story online using Google Search.
    Returns a list of relevant search results (URLs).
    """
    print(f"Searching online for story: {story_title}")
    search_query = f"mongolian mythology folklore story {story_title}"
    if lang_code == "mn":
        search_query = f"монгол домог үлгэр {story_title}"
    
    try:
        search_results = list(search(
            search_query,
            num_results=5,
            lang=lang_code[:2],
            sleep_interval=2 
        ))
        print(f"Found {len(search_results)} URLs for story search")
        return search_results
    except Exception as e:
        print(f"Error searching for story: {e}")
        return []

def search_insight_online(insight_topic, lang_code="en"):
    """
    Search for general info online using Google Search.
    Returns a list of relevant search results (URLs).
    """
    print(f"Searching online for insight topic: {insight_topic}")
    search_query = f"mongolian mythology {insight_topic} explanation significance"
    if lang_code == "mn":
        search_query = f"монгол домог {insight_topic} тайлбар утга учир"
    
    try:

        search_results = list(search(
            search_query,
            num_results=5,
            lang=lang_code[:2],
            sleep_interval=2 
        ))
        print(f"Found {len(search_results)} URLs for insight search")
        return search_results
    except Exception as e:
        print(f"Error searching for insight topic: {e}")
        return []

def search_image_online(topic, lang_code="en"):
    """
    Search for a relevant image URL online using Google Search.
    Returns the first potential image URL found or None.
    """
    print(f"Searching online for image related to: {topic}")
    search_query = f"mongolian mythology {topic} image illustration art"
    if lang_code == "mn":
        search_query = f"монгол домог {topic} зураг дүрслэл урлаг"

    try:
        tld = "mn" if lang_code == "mn" else "com"
        potential_urls = list(search(
            search_query,
            num_results=5,
            lang=lang_code[:2],
            tld=tld,
            sleep_interval=2
        ))

        for url in potential_urls:
            if isinstance(url, str) and any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
                print(f"Found potential image URL: {url}")
                return url
        if potential_urls:
             print(f"No direct image link found, returning first result page: {potential_urls[0]}")        
        print("No suitable image URL found.")
        return None
    except Exception as e:
        print(f"Error searching for image: {e}")
        return None

def get_educational_insights(topic, lang_code="en"):
    """Provides educational insights using a translated prompt and online search results."""
    search_results = search_insight_online(topic, lang_code)
    context = ""
    if search_results:
        context = f"\n\nRelevant sources found:\n" + "\n".join(search_results[:3])
        print(f"Adding context to insights prompt from search results.")
    prompt = t("prompt_get_insights", lang_code, topic=topic)
    if context:
        prompt = f"{prompt}\n\nPlease use the following sources for reference if helpful:{context}"
    return get_gemini_response(prompt)

if __name__ == "__main__":
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY":
       st.error("🚨 CRITICAL: Google API Key is missing or is a placeholder. Please set the GOOGLE_API_KEY variable in the script.")
       st.info("You can get an API key from Google AI Studio: https://aistudio.google.com/app/apikey")
       st.stop() 
    if model:
        print("Starting Streamlit App...")
        main()
    else:
        print("Streamlit App not starting because Gemini model failed to initialize.")
