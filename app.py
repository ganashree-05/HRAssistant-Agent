import gradio as gr
import PyPDF2
from fpdf import FPDF
import datetime, re
from difflib import get_close_matches
from collections import defaultdict

# -----------------------------
# Backend (same as before)
# -----------------------------
hr_faqs = [
    {"question": "What is the leave policy?", "answer": "- 20 paid leaves per year\n- Casual Leave: 10 days\n- Sick Leave: 10 days\n- Carry forward up to 5 days", "category": "Leave"},
    {"question": "How to apply for leave?", "answer": "Apply via HR portal or email your manager with date range and reason.", "category": "Leave"},
    {"question": "What are company holidays?", "answer": "Company holidays are listed in the HR portal. Typically 12 public holidays per year.", "category": "Leave"},
    {"question": "Can I work from home?", "answer": "Employees can work from home up to 2 days a week with manager approval.", "category": "Leave"},
    {"question": "How to claim reimbursement?", "answer": "Submit scanned bills to the finance portal. Use proper expense codes.", "category": "Benefits"},
    {"question": "What is the reimbursement limit?", "answer": "The monthly reimbursement limit is $500 per employee.", "category": "Benefits"},
    {"question": "What is PF?", "answer": "Provident Fund (PF) is a retirement benefit scheme with employer and employee contribution.", "category": "Benefits"},
    {"question": "Does the company provide health insurance?", "answer": "Yes, health insurance is provided for employees and dependents.", "category": "Benefits"},
    {"question": "How to reset my password?", "answer": "Use the IT password reset tool or contact IT support at it-support@company.com.", "category": "IT"},
    {"question": "Who to contact for IT issues?", "answer": "Contact IT support at it-support@company.com or call 123-456-789.", "category": "IT"},
    {"question": "How to set up email on mobile?", "answer": "Follow the IT guide on the portal for iOS or Android devices.", "category": "IT"},
    {"question": "When is salary credited?", "answer": "Salary is credited on the last working day of every month.", "category": "Payroll"},
    {"question": "How to access payslip?", "answer": "Payslips are available on the HR portal under Payroll section.", "category": "Payroll"},
    {"question": "What are the tax deductions?", "answer": "Income tax is deducted as per government norms. Check payslip for details.", "category": "Payroll"},
    {"question": "Who to contact for payroll discrepancies?", "answer": "Contact Payroll team at payroll@company.com.", "category": "Payroll"},
    {"question": "How to get a salary certificate?", "answer": "Request a salary certificate via HR portal or email HR.", "category": "Payroll"},
    {"question": "How to request training?", "answer": "Submit a training request through the Learning & Development portal.", "category": "Policies"},
    {"question": "What is the probation period?", "answer": "The standard probation period is 6 months.", "category": "Policies"},
    {"question": "How to apply for internal job transfer?", "answer": "Submit transfer request via HR portal and discuss with your manager.", "category": "Policies"},
    {"question": "What is the dress code?", "answer": "Business casual is the standard dress code, formal attire on client meetings.", "category": "Policies"},
]


sessions = defaultdict(lambda: {"history": [], "feedback": []})
kb_sections = []
quick_suggestions = [f["question"] for f in hr_faqs[:5]]

# -----------------------------
# Functions (PDF, QA, Sessions)
# -----------------------------
def split_into_sections(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    sections, current_block, current_title = [], [], None
    for p in paragraphs:
        first_line = p.split('\n', 1)[0].strip()
        m = re.match(r'^\d+\.\s*(.+)', first_line)
        if m:
            if current_block: sections.append((current_title or "General", "\n\n".join(current_block).strip()))
            current_title = m.group(1).strip()
            rest = p.split('\n', 1)
            block = rest[1].strip() if len(rest) > 1 else ""
            current_block = [block] if block else []
        elif first_line.isupper() and len(first_line) > 3:
            if current_block: sections.append((current_title or "General", "\n\n".join(current_block).strip()))
            current_title = first_line.title()
            current_block = [p]
        else:
            current_block.append(p)
    if current_block: sections.append((current_title or "General", "\n\n".join(current_block).strip()))
    if not sections: return [("Document", text.strip())]
    return sections

def safe_filename(path): return path.replace("\\", "/").split("/")[-1]

def upload_pdf(file):
    if file is None: return "No file uploaded."
    try:
        reader = PyPDF2.PdfReader(file.name)
        full_text = "".join((pg.extract_text() or "") + "\n\n" for pg in reader.pages)
        sections = split_into_sections(full_text)
        file_name = safe_filename(file.name)
        for title, block in sections:
            kb_sections.append({"title": title or "General", "text": block, "source": file_name})
        return f"Uploaded {file_name} — {len(sections)} sections parsed."
    except Exception as e:
        return f"Upload failed: {e}"

def search_kb_for_answer(question):
    if not kb_sections: return None
    question_lower = question.lower()
    for sec in kb_sections:
        sentences = re.split(r'(?<=[.!?])\s+', sec["text"])
        for i, s in enumerate(sentences):
            if all(word in s.lower() for word in question_lower.split() if len(word) > 3):
                prev = sentences[i-1] if i>0 else ""
                nxt = sentences[i+1] if i+1 < len(sentences) else ""
                context = " ".join([prev, s, nxt]).strip()
                return f"**Answer from PDF KB ({sec['source']} - {sec['title']})**:\n{context[:1000]}"
    return None

def generate_answer(user_message, category_filter="All"):
    q = user_message.strip()
    if not q: return "Please type a question."
    filtered = hr_faqs if category_filter=="All" else [f for f in hr_faqs if f["category"]==category_filter]
    for f in filtered:
        if f["question"].strip().lower() == q.lower(): return f["answer"]
    kb_res = search_kb_for_answer(q)
    if kb_res: return kb_res
    suggestions = get_close_matches(q, [f["question"] for f in hr_faqs], n=4, cutoff=0.4)
    if suggestions:
        return "Sorry, I don't have a direct answer. Try these suggestions:\n" + "\n".join(f"- {s}" for s in suggestions)
    return "Sorry, no answer found."

def update_session(employee_id, user_text, bot_text):
    sess = sessions[employee_id]
    sess["history"].append([f"[{employee_id}] {user_text}", bot_text])

def export_chat_pdf(employee_id):
    sess = sessions.get(employee_id)
    if not sess or not sess["history"]: return None
    filename = f"chat_{employee_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "HRAssistant Chat Export", ln=True, align="C"); pdf.set_font("Arial", size=11); pdf.ln(4)
    for user, bot in sess["history"]:
        pdf.multi_cell(0, 8, f"User: {user}")
        pdf.multi_cell(0, 8, f"Bot: {bot}")
        pdf.ln(2)
    pdf.output(filename); return filename

def export_chat_txt(employee_id):
    sess = sessions.get(employee_id)
    if not sess or not sess["history"]: return None
    filename = f"chat_{employee_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for user, bot in sess["history"]:
            f.write(f"User: {user}\nBot: {bot}\n\n")
    return filename

def handle_user_query(employee_id, user_message, chat_history, category_filter):
    if chat_history is None: chat_history=[]
    employee_id = employee_id.strip() if employee_id else "GUEST"
    answer = generate_answer(user_message, category_filter)
    update_session(employee_id, user_message, answer)
    chat_history.append([f"[{employee_id}] {user_message}", answer])
    return chat_history

def handle_feedback_yes(employee_id, chat_history):
    employee_id = employee_id.strip() if employee_id else "GUEST"
    sessions[employee_id]["feedback"].append("Yes 👍")
    chat_history.append([f"[{employee_id}] Feedback", "👍 Recorded"])
    return chat_history

def handle_feedback_no(employee_id, chat_history):
    employee_id = employee_id.strip() if employee_id else "GUEST"
    sessions[employee_id]["feedback"].append("No 👎")
    chat_history.append([f"[{employee_id}] Feedback", "👎 Recorded"])
    return chat_history

def get_analytics():
    total_chats = sum(len(sess["history"]) for sess in sessions.values())
    total_feedback = sum(len(sess["feedback"]) for sess in sessions.values())
    leave_questions = sum(1 for sess in sessions.values() for u,b in sess["history"] if "leave" in u.lower())
    reimbursement_questions = sum(1 for sess in sessions.values() for u,b in sess["history"] if "reimbursement" in u.lower())
    return f"📊 Total chats: {total_chats}\n👍 Feedbacks: {total_feedback}\n💼 Leave questions: {leave_questions}\n💵 Reimbursement questions: {reimbursement_questions}"

# -----------------------------
# Gradio UI with CSS layout
# -----------------------------
custom_css = """
body {background-color:#f5f7fa;}
.gr-block {margin:10px;}
.gr-box {border-radius:12px; padding:15px; box-shadow:0 4px 6px rgba(0,0,0,0.1);}
h1 {text-align:center; color:#1F4E79;}
h3 {color:#1F4E79;}
.gr-row {gap:20px;}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("<h1>🏢 HR Assistant Agent</h1>")

    with gr.Row():
        # Left Panel: Chat + Feedback + Analytics
        with gr.Column(scale=2):
            with gr.Box():
                gr.Markdown("### 💬 Chatbot")
                employee_id = gr.Textbox(label="Employee ID", placeholder="EMP001", value="")
                chatbot = gr.Chatbot()
                msg = gr.Textbox(placeholder="Type your question here...")

            with gr.Box():
                gr.Markdown("### ⚡ Quick Suggestions")
                with gr.Row():
                    for s in quick_suggestions:
                        btn = gr.Button(s)
                        btn.click(fn=handle_user_query, inputs=[employee_id, gr.State(s), chatbot, gr.State("All")], outputs=[chatbot])

            with gr.Box():
                gr.Markdown("### 📝 Feedback & Export")
                with gr.Row():
                    feedback_yes_btn = gr.Button("👍 Helpful")
                    feedback_no_btn = gr.Button("👎 Not Helpful")
                with gr.Row():
                    export_pdf_btn = gr.Button("Export PDF")
                    export_txt_btn = gr.Button("Export TXT")
                    download_pdf_file = gr.File(label="Download PDF")
                    download_txt_file = gr.File(label="Download TXT")

            with gr.Box():
                gr.Markdown("### 📈 Analytics")
                analytics_box = gr.Textbox(label="Analytics", interactive=False)
                analytics_btn = gr.Button("Refresh Analytics")
                analytics_btn.click(fn=get_analytics, inputs=[], outputs=[analytics_box])

        # Right Panel: KB + Upload + Category
        with gr.Column(scale=1):
            with gr.Box():
                gr.Markdown("### 📁 Knowledge Base")
                upload_file = gr.File(file_types=[".pdf"], label="Upload HR PDF document")
                upload_status = gr.Textbox(label="Upload status", interactive=False)
                category = gr.Dropdown(choices=["All","Leave","Benefits","Policies","IT","Payroll"], value="All", label="Category filter")

    # Event bindings
    msg.submit(fn=handle_user_query, inputs=[employee_id, msg, chatbot, category], outputs=[chatbot])
    feedback_yes_btn.click(fn=handle_feedback_yes, inputs=[employee_id, chatbot], outputs=[chatbot])
    feedback_no_btn.click(fn=handle_feedback_no, inputs=[employee_id, chatbot], outputs=[chatbot])
    upload_file.upload(fn=upload_pdf, inputs=[upload_file], outputs=[upload_status])
    export_pdf_btn.click(fn=lambda eid: export_chat_pdf(eid.strip() if eid else "GUEST"), inputs=[employee_id], outputs=[download_pdf_file])
    export_txt_btn.click(fn=lambda eid: export_chat_txt(eid.strip() if eid else "GUEST"), inputs=[employee_id], outputs=[download_txt_file])

demo.launch(share=True)
