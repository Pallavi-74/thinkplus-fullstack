const API = "http://127.0.0.1:5001/api";
const USER_ID = localStorage.getItem('thinkplus_user_id');

let currentQuestions = [];
let qIdx = 0;
let score = 0;

window.onload = loadDashboard;

async function loadDashboard() {
    // Switch views back to dashboard
    document.getElementById('quiz-area').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');

    try {
        const res = await fetch(`${API}/dashboard/${USER_ID}`);
        const data = await res.json();

        // Fix: Render the Performance Stats cards
        const grid = document.getElementById('stats-grid');
        grid.innerHTML = `
            <div class="stat-card">Average: ${Math.round(data.stats.avg)}%</div>
            <div class="stat-card">Total Quizzes: ${data.stats.count}</div>
        `;

        // Fix: Access .topic_name from the nested object
        document.getElementById('rec-text').innerHTML = `
            Level: <strong>${data.current_level}</strong> | 
            Suggestion: <strong>${data.recommended_topic.topic_name}</strong> | 
            Adjustment: <strong>${data.difficulty_adjustment}</strong>
        `;

        // Link the recommendation button
        document.getElementById('rec-btn').onclick = () => startQuiz(data.recommended_topic.topic_name);

        // Update username
        const savedName = localStorage.getItem('thinkplus_username');
        const nameDisplay = document.getElementById('user-display-name');
        if (nameDisplay) nameDisplay.innerText = savedName || "Student";

    } catch (err) {
        console.error("Dashboard failed:", err);
    }
}

// FIX: This function must be OUTSIDE of submitResults
async function startQuiz(subject) {
    try {
        const res = await fetch(`${API}/get_questions/${subject}`);
        currentQuestions = await res.json();

        if (currentQuestions.length === 0) {
            alert("No questions found!");
            return;
        }

        qIdx = 0;
        score = 0;

        document.getElementById('dashboard').classList.add('hidden');
        document.getElementById('quiz-area').classList.remove('hidden');
        
        showQuestion(); 
    } catch (err) {
        console.error("Failed to start quiz:", err);
    }
}

function showQuestion() {
    const q = currentQuestions[qIdx];
    document.getElementById('q-text').innerText = q.question_text;
    
    const optDiv = document.getElementById('options');
    optDiv.innerHTML = ''; 

    q.options.forEach((opt, i) => {
        const btn = document.createElement('button');
        btn.innerText = opt;
        btn.className = "opt-btn";
        btn.onclick = () => handleAnswer(i);
        optDiv.appendChild(btn);
    });
}

async function handleAnswer(selectedIdx) {
    if (selectedIdx === currentQuestions[qIdx].correct_idx) {
        score += (100 / currentQuestions.length);
    }
    qIdx++;
    if (qIdx < currentQuestions.length) {
        showQuestion();
    } else {
        await submitResults();
    }
}

async function submitResults() {
    try {
        await fetch(`${API}/submit_quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: USER_ID,
                topic_id: currentQuestions[0].topic_id,
                score: Math.round(score)
            })
        });
        alert("Quiz Submitted!");
        loadDashboard(); 
    } catch (err) {
        console.error("Error submitting:", err);
    }
}