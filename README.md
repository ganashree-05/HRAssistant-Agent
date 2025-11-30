# 🏢 HR Assistant Agent

A smart HR Assistant Agent built with Python and Gradio. This project provides a chatbot interface to answer HR-related queries, manage PDF-based knowledge bases, track analytics, and collect feedback.

---

## Overview of the Agent

The HR Assistant Agent helps employees quickly access HR policies, payroll information, leave management, IT support, and reimbursement guidelines. Users can:

- Ask questions directly in the chatbot.
- Upload HR PDFs to extend the knowledge base.
- Filter questions by category (Leave, Benefits, IT, Payroll, Policies).
- Track analytics such as total chats, feedbacks, and popular question topics.
- Export chat history as PDF or TXT.

---

## Features & Limitations

### Features
- Interactive chatbot interface using Gradio.
- Upload and parse PDF documents to expand the knowledge base.
- Quick suggestion buttons for common questions.
- Feedback system (👍 Helpful / 👎 Not Helpful).
- Export chat history in PDF or TXT format.
- Analytics dashboard to track usage and query trends.

### Limitations
- Knowledge is limited to FAQs and uploaded PDF content.
- Complex or ambiguous queries may not return accurate answers.
- Real-time collaboration or multi-user concurrency is limited.
- Currently runs locally; public deployment requires Gradio sharing or hosting.

---

## Tech Stack & APIs Used

- **Language:** Python 3.10+
- **Libraries & Frameworks:**
  - Gradio (UI)
  - PyPDF2 (PDF processing)
  - FPDF (PDF export)
  - Difflib (close-match suggestions)
- **Data Storage:** In-memory sessions (Python `defaultdict`)
- **APIs & Tools:** None external; fully local
- **UI/UX:** Gradio with custom CSS for dark/light theme support

---

## Setup & Run Instructions

### Prerequisites
- Python 3.10+ installed
- Pip package manager

### Steps to Run Locally
1. **Clone the repository**
   ```bash
   git clone <your-github-repo-link>
   cd <your-project-folder>

2.Create a virtual environment (recommended)
python -m venv .venv

3.Activate the virtual environment
# Windows
.\.venv\Scripts\activate
# Linux/MacOS
source .venv/bin/activate

4.Install dependencies
pip install -r requirements.txt

5.Run the application
python hr_assistant.py

6.Access the web app
Open the URL displayed in your terminal (e.g., http://127.0.0.1:7860)
Interact with the chatbot, upload PDFs, and test analytics

🔧 Potential Improvements

Integrate with OpenAI GPT or other LLMs for advanced question answering.

Use a Vector Database (Pinecone, FAISS) for semantic search over PDFs.

Implement user authentication for multi-employee use.

Connect to real HR databases (Firebase, Supabase, Google Sheets) for persistent storage.

Enhance UI/UX with custom HTML/CSS themes or a full React/Next.js front-end.

Add multi-language support for diverse employees.

Create automated notifications for unanswered queries or pending approvals.
