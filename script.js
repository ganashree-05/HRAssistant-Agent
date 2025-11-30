let analytics = {
    totalChats: 0,
    categoryStats: { Leave:0, Benefits:0, IT:0, Payroll:0, Policies:0 },
    feedbackStats: { yes:0, no:0 },
    topQuestions: {}
};

function updateAnalyticsPanel() {
    let panel = document.getElementById("analytics-panel");
    panel.textContent = `Total Chats: ${analytics.totalChats}

Category Stats:
  Leave: ${analytics.categoryStats.Leave}
  Benefits: ${analytics.categoryStats.Benefits}
  IT: ${analytics.categoryStats.IT}
  Payroll: ${analytics.categoryStats.Payroll}
  Policies: ${analytics.categoryStats.Policies}

Feedback Stats:
  👍 Helpful: ${analytics.feedbackStats.yes}
  👎 Not Helpful: ${analytics.feedbackStats.no}

Top Questions:
${Object.entries(analytics.topQuestions).map(([q,c]) => `  ${q}: ${c}`).join("\n")}`;
}

document.getElementById("send-msg").addEventListener("click", function() {
    let msg = document.getElementById("user-msg").value.trim();
    let empId = document.getElementById("employee-id").value || "GUEST";
    if(!msg) return;

    // Update chat window
    let chatWindow = document.getElementById("chat-window");
    let userDiv = document.createElement("div");
    userDiv.textContent = `[${empId}] ${msg}`;
    userDiv.style.fontWeight = "bold";
    chatWindow.appendChild(userDiv);

    // Simulate backend response
    let botAnswer = "This is a placeholder answer.";
    let botDiv = document.createElement("div");
    botDiv.textContent = botAnswer;
    chatWindow.appendChild(botDiv);

    // Update analytics
    analytics.totalChats += 1;
    // Example: random category assignment
    let categories = ["Leave","Benefits","IT","Payroll","Policies"];
    let cat = categories[Math.floor(Math.random()*categories.length)];
    analytics.categoryStats[cat] += 1;

    // Top questions
    analytics.topQuestions[msg] = (analytics.topQuestions[msg]||0)+1;

    updateAnalyticsPanel();

    chatWindow.scrollTop = chatWindow.scrollHeight;
    document.getElementById("user-msg").value = "";
});
