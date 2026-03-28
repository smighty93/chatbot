import streamlit as st
import requests
import os
@st.cache_data(show_spinner=False)
def cached_llm(prompt):
    from llm import ask_llm
    return ask_llm(prompt)

# =================================================
# PAGE CONFIG
import base64

def set_bg(image_file):

    if not os.path.exists(image_file):
        return

    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# 🔥 CALL FUNCTION

# =================================================
st.set_page_config(page_title="Consumer Legal Chat Assistant", layout="wide")


def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """

    st.markdown(bg_css, unsafe_allow_html=True)


# =================================================
# APPLY BACKGROUND (IMMEDIATELY AFTER FUNCTION)
# =================================================
set_bg("background.png")


# =================================================
# CUSTOM PROFESSIONAL THEME (Add this after set_page_config)
# =================================================
# =================================================
# MODERN SLEEK WHITE THEME
# =================================================
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #18181B !important; border-right: 1px solid #27272A; }
    [data-testid="stChatMessage"] { background-color: #18181B; border-radius: 12px; border: 1px solid #27272A; }
    [data-testid="stChatMessage"]:nth-child(even) { background-color: #27272A; border: 1px solid #3F3F46; }
    .stButton>button { background-color: #FFFFFF !important; color: #000000 !important; font-weight: 600 !important; border-radius: 6px !important; }
    .stButton>button:hover { background-color: #E4E4E7 !important; transform: scale(1.02); }
    [data-testid="stChatInput"] { background-color: #18181B !important; border: 1px solid #3F3F46 !important; }
    </style>
    """, unsafe_allow_html=True)



# =================================================
# SESSION STATE
# =================================================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "issue_type" not in st.session_state:
    st.session_state.issue_type = None

if "user_story" not in st.session_state:
    st.session_state.user_story = ""

if "awaiting_complaint" not in st.session_state:
    st.session_state.awaiting_complaint = False
# 🔥 NEW (ADD BELOW EXISTING SESSION STATE)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "page" not in st.session_state:
    st.session_state.page = "Chat"
if "asked_questions" not in st.session_state:
    st.session_state.asked_questions = set()

# =================================================
# LEGAL MAP
# =================================================
LEGAL_MAP = {

    "Refund Not Given": {
        "violation": "Unfair Trade Practice",
        "act": "Consumer Protection Act, 2019",
        "sections": ["Section 2(47)", "Section 35"],
        "forum": "District Consumer Commission",
        "steps": [
            "Request refund from the platform",
            "Ask for written confirmation",
            "Escalate if no response within 3–5 days"
        ]
    },

    "Delivery Issue": {
        "violation": "Deficiency in Service",
        "act": "Consumer Protection Act, 2019",
        "sections": ["Section 2(11)", "Section 35"],
        "forum": "District Consumer Commission",
        "steps": [
            "Report delivery issue on platform",
            "Ask for proof of delivery",
            "Escalate to grievance officer"
        ]
    },

    "Defective Product": {
        "violation": "Defect in Goods",
        "act": "Consumer Protection Act, 2019",
        "sections": ["Section 2(10)", "Section 35"],
        "forum": "District Consumer Commission",
        "steps": [
            "Request replacement or repair",
            "Submit proof (photos/videos)",
            "Escalate if denied"
        ]
    },

    "Wrong Delivery": {
        "violation": "Deficiency in Service",
        "act": "Consumer Protection Act, 2019",
        "sections": ["Section 2(11)", "Section 35"],
        "forum": "District Consumer Commission",
        "steps": [
            "Report wrong item received",
            "Upload proof of incorrect product",
            "Request replacement"
        ]
    },

    "Service Deficiency": {
        "violation": "Deficiency in Service",
        "act": "Consumer Protection Act, 2019",
        "sections": ["Section 2(11)", "Section 35"],
        "forum": "District Consumer Commission",
        "steps": [
            "Report service issue",
            "Request correction or compensation",
            "Escalate if unresolved"
        ]
    },

    "Misleading Advertisement": {
        "violation": "Misleading Advertisement",
        "act": "Consumer Protection Act, 2019",
        "sections": ["Section 21"],
        "forum": "Central Consumer Protection Authority (CCPA)",
        "steps": [
            "Collect proof of advertisement",
            "Compare with actual product/service",
            "File complaint with CCPA"
        ]
    },

    "Warranty Issue": {
        "violation": "Deficiency in Service",
        "act": "Consumer Protection Act, 2019",
        "sections": ["Section 2(11)", "Section 35"],
        "forum": "District Consumer Commission",
        "steps": [
            "Check warranty terms",
            "Request service/repair",
            "Escalate if denied"
        ]
    },

    "E-Commerce Issue": {
        "violation": "Violation of E-Commerce Rules",
        "act": "Consumer Protection (E-Commerce) Rules, 2020",
        "sections": ["Rule-based compliance"],
        "forum": "District Consumer Commission",
        "steps": [
            "Raise complaint on platform",
            "Request escalation to grievance officer",
            "File complaint if unresolved"
        ]
    }
}

# =================================================
# ISSUE CLASSIFICATION
# =================================================
def classify_issue(text):
    t = text.lower()

    if any(k in t for k in ["refund", "money back", "not returned"]):
        return "Refund Not Given"

    if any(k in t for k in ["not delivered", "delivery", "delay"]):
        return "Delivery Issue"

    if any(k in t for k in ["defective", "broken", "damaged"]):
        return "Defective Product"

    if any(k in t for k in ["wrong item", "different product"]):
        return "Wrong Delivery"

    if any(k in t for k in ["service", "installation", "technician"]):
        return "Service Deficiency"

    if any(k in t for k in ["advertisement", "fake", "misleading"]):
        return "Misleading Advertisement"

    if any(k in t for k in ["warranty", "guarantee"]):
        return "Warranty Issue"

    if any(k in t for k in ["online", "app", "platform", "flipkart", "amazon"]):
        return "E-Commerce Issue"

    return "Service Deficiency"  # fallback
from difflib import SequenceMatcher

def hybrid_classify(text):
    text = text.lower()

    scores = {}

    for key in LEGAL_MAP.keys():
        score = SequenceMatcher(None, text, key.lower()).ratio()
        scores[key] = score

    best = max(scores, key=scores.get)

    # fallback safeguard
    if scores[best] < 0.2:
        return classify_issue(text)

    return best
# =================================================
# ENTITY DETECTION
# =================================================
def detect_entity_type(text):
    t = text.lower()

    if any(k in t for k in ["amazon", "flipkart", "meesho"]):
        return "ecommerce_platform"

    if any(k in t for k in ["shop", "store", "local seller"]):
        return "local_seller"

    if any(k in t for k in ["service", "technician", "installation"]):
        return "service_provider"

    return "general_company"

# =================================================
# DYNAMIC STEP GENERATOR
# =================================================
def get_dynamic_steps(entity_type, law_steps):

    if entity_type == "ecommerce_platform":
        return [
            "Raise complaint on the platform",
            "Escalate to grievance officer",
            "File complaint on consumer helpline",
        ] + law_steps

    elif entity_type == "local_seller":
        return [
            "Visit or contact the seller directly",
            "Send a written complaint (WhatsApp/email)",
            "Keep proof of communication",
            "Escalate to consumer forum if unresolved",
        ]

    elif entity_type == "service_provider":
        return [
            "Request service correction",
            "Document poor service",
            "Send formal complaint",
            "Escalate legally if ignored",
        ]

    else:
        return law_steps
# =================================================
# INTENT DETECTION  ← ADD IT HERE
# =================================================
from llm import ask_llm

def detect_intent(text):
    prompt = f"""
    Classify the intent:

    Options:
    - generate_complaint
    - filing_guidance
    - evidence_help
    - cost_info
    - general

    Input: {text}

    Return ONLY the intent.
    """

    try:
        return ask_llm(prompt).strip()
    except:
        return "general"

# =================================================
# DYNAMIC ESTIMATION
# =================================================
ESTIMATION = {

    "Refund Not Given": {
        "low": ("3–7 days", "₹0–₹200"),
        "medium": ("1–3 weeks", "₹200–₹1000"),
        "high": ("1–6 months", "₹1000–₹5000+")
    },

    "Delivery Issue": {
        "low": ("2–5 days", "₹0–₹200"),
        "medium": ("1–2 weeks", "₹200–₹800"),
        "high": ("1–4 months", "₹800–₹4000+")
    },

    "Defective Product": {
        "low": ("3–7 days", "₹0–₹300"),
        "medium": ("1–3 weeks", "₹300–₹1200"),
        "high": ("1–6 months", "₹1200–₹6000+")
    },

    "Wrong Delivery": {
        "low": ("2–5 days", "₹0–₹200"),
        "medium": ("1–2 weeks", "₹200–₹800"),
        "high": ("1–4 months", "₹800–₹4000+")
    },

    "Service Deficiency": {
        "low": ("3–10 days", "₹0–₹300"),
        "medium": ("2–4 weeks", "₹300–₹1500"),
        "high": ("1–6 months", "₹1500–₹7000+")
    },

    "Misleading Advertisement": {
        "low": ("1–2 weeks", "₹0–₹300"),
        "medium": ("3–6 weeks", "₹300–₹1500"),
        "high": ("2–6 months", "₹1500–₹8000+")
    },

    "Warranty Issue": {
        "low": ("5–10 days", "₹0–₹300"),
        "medium": ("2–4 weeks", "₹300–₹1200"),
        "high": ("1–6 months", "₹1200–₹6000+")
    },

    "E-Commerce Issue": {
        "low": ("3–7 days", "₹0–₹200"),
        "medium": ("1–3 weeks", "₹200–₹1000"),
        "high": ("1–6 months", "₹1000–₹5000+")
    }
}

def detect_severity(text):
    t = text.lower()

    if "fraud" in t or "legal" in t:
        return "high"
    if "not responding" in t or "ignored" in t:
        return "medium"
    return "low"

def get_estimation(issue, text):
    severity = detect_severity(text)

    if issue in ESTIMATION:
        data = ESTIMATION[issue]
    else:
        data = {
            "low": ("3–7 days", "₹0–₹300"),
            "medium": ("1–3 weeks", "₹300–₹1500"),
            "high": ("1–6 months", "₹1500–₹6000+")
        }

    return data[severity], severity

# =================================================
# COMPLAINT GENERATOR (LLM)
# =================================================
def generate_complaint(story, issue):
    from llm import ask_llm

    prompt = f"""
You are a legal assistant.

Write a professional consumer complaint email.

Details:
- Issue: {issue}
- Problem: {story}

STRICT FORMAT:

Subject: Complaint regarding [issue]

To: [Company / Seller Name]

Respected Sir/Madam,

[Clear explanation of issue]

[Mention delay/problem]

[State legal rights briefly]

I request:
- Refund / Replacement / Compensation

Please resolve this within 7 days.

Sincerely,
[Your Name]
[Contact Details]
"""

    reply = cached_llm(prompt)

    reply += """

---

### 📤 How to use this complaint:

1. Copy the above email  
2. Send it to:
   - Company support email  
   - Grievance officer  

3. Attach:
   • Invoice  
   • Screenshots  
   • Payment proof  

4. Wait 3–5 days before escalation
"""

    return reply
# =================================================
# SMART RESPONSE (LLM)
# =================================================
def generate_smart_response(issue, law, story):
    from llm import ask_llm
    from rag import retrieve_context

    # ✅ FIX 1: Get RAG context
    rag_context = retrieve_context(story)

    (time_est, cost_est), severity = get_estimation(issue, story)

    # urgency detection
    if "10 days" in story or "not responding" in story:
        urgency_note = "The delay is already beyond normal processing time."
    else:
        urgency_note = ""

    entity_type = detect_entity_type(story)
    steps = get_dynamic_steps(entity_type, law["steps"])
    evidence_list = get_evidence_checklist(issue)
    evidence_text = "\n".join([f"- {e}" for e in evidence_list])

    has_strong_evidence = all([
    "invoice" in story.lower(),
    "payment" in story.lower(),
    "tracking" in story.lower()
])


    # ✅ CLEAN STRUCTURED PROMPT
    prompt = f"""
You are a friendly but knowledgeable legal assistant helping Indian consumers.

Your tone should be:
- Conversational
- Supportive
- Clear and confident
- NOT robotic or overly formal

--- CONTEXT ---
{rag_context}

--- USER ISSUE ---
{story}

--- LEGAL CLASSIFICATION ---
{law['violation']} under {law['act']}

--- ADDITIONAL INFO ---
Estimated Time: {time_est}
Estimated Cost: {cost_est}
Severity: {severity}
{urgency_note}

Write the response in this style:

Start with empathy:
- Acknowledge the user's frustration naturally

Then explain simply:
- What is happening
- Why it is legally wrong (in plain English first)
- THEN mention law/section (if relevant, don’t lead with it)

Then guide clearly:

### What you should do now:
- Step-by-step actionable guidance (practical, not generic)

### If they still don’t respond:
- Escalation path (platform → grievance → legal)

### What you should keep ready:
- Evidence list (context-based)

### Time & effort:
- Realistic expectation (time + cost)
User already has strong evidence: {has_strong_evidence}

--- RULES ---
- If delay already exceeds normal time, acknowledge it clearly
- Explain WHY this is a legal violation in detail
- Include relevant sections (if applicable)
- Focus on what uses should do
- Provide a clear escalation path (platform → grievance → legal)
- Adapt based on entity (Flipkart, shop, service, etc.)
- Be slightly assertive when user rights are violated
- Avoid generic steps
- Do not repeat the same basic advice
- Do NOT sound like a lawyer writing a document
- Do NOT start with legal sections
- Explain like you're helping a friend who doesn’t understand law
- Keep it detailed but easy to read
- Use simple formatting (headings, spacing)
- If user already has evidence, DO NOT ask them to collect it again
- Move directly to action and escalation steps

Include:
- Legal reasoning
- Actionable next steps
- Realistic timeline

Keep it conversational but authoritative.
Recommended Evidence:
{evidence_text}
"""
    reply = cached_llm(prompt)
    reply += "\n\n### 🔍 Evidence Status:\n"

    if has_strong_evidence: 
        reply += "✅ You already have strong evidence:\n"

    for e in evidence_list[:3]:
        reply += f"- {e}\n"

        reply += "\n👉 Your case is strong. You can move to escalation.\n"

    else:
        reply += "⚠️ You may still need:\n"

    for e in evidence_list[:3]:
        reply += f"- {e}\n"

    reply += "\n👉 Tell me what you already have — I’ll guide you further.\n"
    

    return reply
# =================================================
# RESPONSE GENERATOR
# =================================================
def generate_response(issue, law, story):
    (time_est, cost_est), severity = get_estimation(issue, story)

    # 👇 Dynamic tone
    if severity == "high":
        intro = f"Hey — this is actually serious. {story}\n\nThis shouldn't be happening."
    else:
        intro = f"I get what you're dealing with — {story}\n\nLet’s sort this out step by step."

    # 👇 Simple explanation first (not legal-heavy)
    explanation = f"""
From what you've described, this falls under **{law['violation']}**.

In simple terms: the company hasn't fulfilled its responsibility properly.
"""

    # 👇 Legal mention (secondary, not dominant)
    legal_note = f"""
Under the **{law['act']}**, this gives you the right to take action if they don’t resolve it.
"""

    # 👇 Smart steps
    steps = "\n".join([f"{i+1}. {s}" for i, s in enumerate(law["steps"])])

    guidance = f"""
### ✅ What you should do now:

{steps}
"""

    # 👇 Escalation clarity
    escalation = """
### 🚨 If they still don’t respond:

1. Ask for the **Grievance Officer**
2. Wait 3–5 days max  
3. File complaint on **consumerhelpline.gov.in**
4. Then approach **Consumer Commission** if needed
"""

    # 👇 Evidence system (NEW)
    evidence = """
### 📂 Let’s check your evidence:

Do you already have:
- Invoice / bill  
- Payment proof  
- Screenshots of order or issue  
- Chat/email with the company  

👉 If you're missing anything, tell me — I’ll guide you how to get it.
"""

    # 👇 Estimate (cleaner)
    estimate = f"""
### ⏱ What to expect:

- Time: {time_est}  
- Cost: {cost_est}

This depends on how quickly the company responds and how strong your proof is.
"""

    # 👇 Action CTA (important UX)
    closing = """
### 👍 I can help you next:

• Draft a strong complaint  
• Tell you exactly what to say to the company  
• Help you prepare documents  

Just tell me what you want to do.
"""

    return (
        f"{intro}\n\n"
        f"{explanation}\n"
        f"{legal_note}\n"
        f"{guidance}\n"
        f"{escalation}\n"
        f"{evidence}\n"
        f"{estimate}\n"
        f"{closing}"
    )
# =================================================
# FOLLOW-UP QUESTION ENGINE
# =================================================
def generate_followup_questions(story, issue):
    story = story.lower()
    questions = []

    # 🔥 Priority-based questioning
    if issue == "Refund Not Given" and "refund" in story:
        if not any(k in story for k in ["date", "day", "when"]):
            questions.append("When exactly did you request the refund?")

        if not any(k in story for k in ["amount", "rs", "₹"]):
            questions.append("What is the refund amount involved?")

        if "refund" in story and "response" not in story:
            questions.append("Did the company respond to your refund request?")

    elif issue == "Defective Product":
        if not any(k in story for k in ["photo", "video", "image"]):
            questions.append("Do you have photos or videos showing the defect clearly?")

        if "received" not in story:
            questions.append("When did you receive the product?")

    elif issue == "Delivery Issue":
        if not any(k in story for k in ["tracking", "awb", "status"]):
            questions.append("Do you have tracking details or order status?")

        if "date" not in story:
            questions.append("When was the expected delivery date?")

    elif issue == "Wrong Delivery":
        if "photo" not in story:
            questions.append("Did you take a photo of the wrong item received?")

    # 🔥 Universal evidence check (smarter)
    if not any(k in story for k in ["invoice", "bill", "receipt"]):
        questions.append("Do you have the invoice or bill for this order?")

    if not any(k in story for k in ["payment", "upi", "bank", "card"]):
        questions.append("Do you have payment proof (UPI / bank / card)?")

    # 🔥 Limit questions (avoid overwhelming user)
    return questions[:3]
def get_evidence_checklist(issue):
    base = [
        
        "Invoice or order receipt (download from order page)",
        "Payment proof (UPI / bank / card screenshot)"
    ]

    issue_specific = {
        "Refund Not Given": [
            "Screenshot of refund request",
            "Chat/email showing delay or refusal"
        ],
        "Defective Product": [
            "Clear photos/videos of the defect",
            "Unboxing video (if available)"
        ],
        "Delivery Issue": [
            "Order tracking screenshot",
            "Delivery status page showing delay"
        ],
        "Wrong Delivery": [
            "Photo of wrong item received",
            "Packaging label with order details"
        ]
    }

    return base + issue_specific.get(issue, [])
# =================================================
# NAVIGATION HEADER
# =================================================
st.markdown("<h1>⚖️ Consumer Legal Chat Assistant</h1>", unsafe_allow_html=True)
st.session_state.page = st.radio(
    "Navigation",
    ["Chat", "Insights"],
    horizontal=True
)
def save_complaint(issue):
    import json

    try:
        with open("complaints.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(issue)

    with open("complaints.json", "w") as f:
        json.dump(data, f)

# =================================================
# CHAT PAGE
# =================================================
if st.session_state.page == "Chat":
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    # =========================
    # SIDEBAR (CHAT HISTORY)
    # =========================
    with st.sidebar:
        st.title("💬 Chats")

        if st.button("➕ New Chat"):
            if st.session_state.chat:
                st.session_state.chat_history.append(st.session_state.chat)
            st.session_state.chat = []

        for i, chat in enumerate(st.session_state.chat_history):
            preview = chat[0]["content"][:30] if chat else "New Chat"
            if st.button(f"{preview}..."):
                st.session_state.chat = chat

        if st.session_state.issue_type:
             st.success(f"Issue Detected: {st.session_state.issue_type}")

    # =========================
    # CHAT DISPLAY
    # =========================
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.divider()

    # =========================
    # ACTION BUTTONS
    # =========================
    if not st.session_state.issue_type:
        st.warning("Describe your issue first to enable actions.")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📄 Generate Complaint"):
            if st.session_state.issue_type:
                reply = generate_complaint(
                    st.session_state.user_story,
                    st.session_state.issue_type
                )
                st.session_state.chat.append({"role": "assistant", "content": reply})
                st.rerun()

    with col2:
        if st.button("📍 Filing Help"):
            reply = "You can file via platform → grievance officer → consumerhelpline.gov.in"
            st.session_state.chat.append({"role": "assistant", "content": reply})
            st.rerun()

    with col3:
        if st.button("📊 Estimate Cost"):
            issue = st.session_state.issue_type
            if issue:
                (time_est, cost_est), severity = get_estimation(issue, st.session_state.user_story)
                reply = f"⏱ Time: {time_est}\n💰 Cost: {cost_est}\nSeverity: {severity}"
                st.session_state.chat.append({"role": "assistant", "content": reply})
                st.rerun()

    # =================================================
    # DISCLAIMER
    # =================================================
    
    st.markdown("""
    <hr style="margin-top:40px;">

    <p style="font-size:12px; color:#71717A; text-align:center;">
    ⚠️ This assistant provides legal information under Indian consumer law and does not replace a licensed advocate.
    </p>
    """, unsafe_allow_html=True)

    # =========================
    # USER INPUT
    # =========================
    user_input = st.chat_input("Type your issue...")

    if user_input:
        st.session_state.chat.append({"role": "user", "content": user_input})

        if len(user_input) < 8:
            intent = "general"
        else:
            intent = detect_intent(user_input)

        # =========================
        # INTENT ROUTING
        # =========================
        if intent == "generate_complaint" and st.session_state.issue_type:
            reply = generate_complaint(
                st.session_state.user_story,
                st.session_state.issue_type
            )

        elif intent == "filing_guidance":
            issue = st.session_state.issue_type or classify_issue(user_input)
            law = LEGAL_MAP[issue]

            base_reply = generate_smart_response(issue, law, user_input)

            filing_steps = """

---

### 📌 How to file your complaint (exact steps):

#### 1. Platform (First step)
- Go to your order page
- Click **"Need Help" / "Report Issue"**
- Select issue: *Delivery delay / Not delivered*
- Clearly request:
  - Immediate delivery OR refund

---

#### 2. Grievance Officer
- If no resolution in 3–5 days:
- Find "Grievance Officer" contact on website/app
- Send email with:
  - Order ID
  - Timeline
  - Your demand (refund/delivery)

---

#### 3. Consumer Helpline
- Go to: https://consumerhelpline.gov.in
- Register complaint
- Upload:
  - Invoice
  - Payment proof
  - Screenshots

---

#### 4. Consumer Commission (Final step)
- File case in District Consumer Commission
- Use your complaint + evidence
"""

            reply = base_reply + filing_steps

        elif intent == "evidence_help":
            reply = """
You should collect:

• Invoice  
• Payment proof  
• Screenshots  
• Chat/email records  
"""

        elif intent == "cost_info":
            issue = st.session_state.issue_type or classify_issue(user_input)
            (time_est, cost_est), severity = get_estimation(issue, user_input)

            reply = f"""
⏱ Time: {time_est}  
💰 Cost: {cost_est}  
Severity: {severity}
"""

        else:
            issue = hybrid_classify(user_input)
            st.session_state.issue_type = issue
            st.session_state.user_story = user_input

            # 🔥 SAVE TO INSIGHTS
            save_complaint(issue)
            st.toast("Complaint added to insights dashboard ✅")
            law = LEGAL_MAP[issue]

            reply = generate_smart_response(issue, law, user_input)

            # FOLLOW-UP QUESTIONS
            followups = generate_followup_questions(user_input, issue)
            evidence_list = get_evidence_checklist(issue)

            if followups and len(user_input.split()) < 15:
                reply += "\n\n### ❓ I need a bit more info:\n"
            for q in followups:
                reply += f"- {q}\n"

            pass
        # =========================
        # PREVENT DUPLICATES
        # =========================
        if not st.session_state.chat or st.session_state.chat[-1]["content"] != reply:
            st.session_state.chat.append({"role": "assistant", "content": reply})

        st.rerun()


# =================================================
# INSIGHTS DASHBOARD
# =================================================
elif st.session_state.page == "Insights":
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.title("📊 Complaint Insights Dashboard")

    import json
    from collections import Counter
    import pandas as pd

    DEMO_DATA = [
        "Defective Product", "Refund Not Given", "Delivery Issue",
        "Defective Product", "Wrong Delivery", "Service Deficiency"
    ]

    def load_data():
        try:
            with open("complaints.json", "r") as f:
                return json.load(f)
        except:
            return []

    data = DEMO_DATA + load_data()

    if data:
        stats = Counter(data)
        df = pd.DataFrame.from_dict(stats, orient='index', columns=['Count'])

        # TOP ISSUE
        top_issue = df["Count"].idxmax()
        top_count = df["Count"].max()

        st.success(f"🥇 Most Common Issue: {top_issue} ({top_count} cases)")

        st.divider()

        # DISTRIBUTION
        st.subheader("Issue Distribution")
        st.bar_chart(df)

        st.divider()

        # SUCCESS RATE
        SUCCESS_RATE = {
            "Defective Product": 85,
            "Refund Not Given": 70,
            "Delivery Issue": 60,
            "Wrong Delivery": 65,
            "Service Deficiency": 68
        }

        st.subheader("Resolution Success Rate")

        for issue in df.index:
            rate = SUCCESS_RATE.get(issue, 65)
            st.write(issue)
            st.progress(rate)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
<div class='footer'>
⚠️ This assistant provides legal information under Indian consumer law. It does not replace a licensed advocate.
</div>
""", unsafe_allow_html=True)