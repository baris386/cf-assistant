const TOPICS = [
    "Greedy", "DP", "Binary Search", "Graphs", "Data Structures", "Math",
    "Strings", "Two Pointers", "Bitmasks", "Constructive", "Sortings", "Brute Force",
    "Implementation", "Combinatorics", "Number Theory", "Geometry", "DFS and Similar",
    "Trees", "Divide and Conquer", "Probabilities", "Games", "Shortest Paths",
    "Ternary Search", "Dsu", "Flows", "Matching", "String Suffix-structures",
    "Expression Parsing", "Graph Matchings", "Interactive", "Matrices",
    "Meet-in-the-middle", "Hashing", "2-sat", "Schedules", "Chinese Remainder Theorem"
];

let state = {
    cfHandle: null,
    solvedProblems: [],
    currentProblemContext: null,
    hintCount: 0,
    selectedTags: new Set(["Greedy"]),
    chatHistory: []
};

// UI Elements
const tagsContainer = document.getElementById('tags-container');
const chatContainer = document.getElementById('chat-container');
const emptyChatMsg = document.getElementById('empty-chat-msg');
const chatInput = document.getElementById('chat-input');

// Initialize Topics
function initTopics() {
    TOPICS.forEach(topic => {
        const pill = document.createElement('div');
        pill.className = `tag-pill ${state.selectedTags.has(topic) ? 'active' : ''}`;
        pill.textContent = topic;
        pill.onclick = () => {
            if (state.selectedTags.has(topic)) {
                state.selectedTags.delete(topic);
                pill.classList.remove('active');
            } else {
                state.selectedTags.add(topic);
                pill.classList.add('active');
            }
        };
        tagsContainer.appendChild(pill);
    });
}
initTopics();

// Notice System
function showNotice(containerId, kind, message) {
    const container = document.getElementById(containerId);
    const icons = { success: "OK", error: "!!", warning: "!", info: "i" };
    
    const div = document.createElement('div');
    div.className = `cyber-notice cyber-notice-${kind}`;
    
    div.innerHTML = `
        <span class="cyber-notice-icon">${icons[kind] || 'i'}</span>
        <div class="cyber-notice-body">${message}</div>
    `;
    
    container.innerHTML = '';
    container.appendChild(div);
}

function clearNotice(containerId) {
    document.getElementById(containerId).innerHTML = '';
}

// Chat System
function addChatMessage(role, contentHTML) {
    if (emptyChatMsg) emptyChatMsg.style.display = 'none';
    
    const row = document.createElement('div');
    row.className = `chat-row ${role}-row`;
    
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}-bubble`;
    
    const avatar = document.createElement('span');
    avatar.className = 'chat-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'chat-message-content';
    contentDiv.innerHTML = contentHTML;
    
    if (role === 'user') {
        bubble.appendChild(contentDiv);
        bubble.appendChild(avatar);
    } else {
        bubble.appendChild(avatar);
        bubble.appendChild(contentDiv);
    }
    
    row.appendChild(bubble);
    chatContainer.appendChild(row);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// API Calls
async function apiCall(endpoint, data) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) {
        let msg = 'API Error';
        if (typeof result.detail === 'string') {
            msg = result.detail;
        } else if (Array.isArray(result.detail)) {
            msg = result.detail.map(d => d.msg || JSON.stringify(d)).join(', ');
        } else if (result.detail) {
            msg = JSON.stringify(result.detail);
        }
        throw new Error(msg);
    }
    return result;
}

async function sendChatRequest(action, message = null, prompt = null) {
    // Show loading
    const loaderId = 'loader-' + Date.now();
    addChatMessage('assistant', `<div id="${loaderId}" class="loader"></div> Thinking...`);
    
    try {
        const payload = {
            action: action,
            message: message,
            problem_context: state.currentProblemContext,
            hint_count: state.hintCount,
            history: state.chatHistory,
            recommendation_prompt: prompt
        };
        
        const res = await apiCall('/api/chat', payload);
        
        // Remove loader
        const loader = document.getElementById(loaderId);
        if (loader) loader.parentElement.innerHTML = res.html;
        
        state.chatHistory.push({role: "assistant", content: res.response});
    } catch (err) {
        const loader = document.getElementById(loaderId);
        if (loader) loader.parentElement.innerHTML = `<span style="color:red">Error: ${err.message}</span>`;
    }
}

// Event Listeners
document.getElementById('sync-profile-btn').onclick = async () => {
    const handle = document.getElementById('cf-handle-input').value.trim();
    if (!handle) return;
    
    showNotice('profile-status', 'info', '<div class="loader"></div> Syncing...', true);
    try {
        const res = await apiCall('/api/sync-profile', { handle });
        state.solvedProblems = res.solved_problems;
        state.cfHandle = handle;
        showNotice('profile-status', 'success', `Profile synced — <strong style="color:#00f3ff">${res.solved_problems.length}</strong> problems solved`, true);
    } catch (err) {
        showNotice('profile-status', 'error', err.message);
    }
};

document.getElementById('load-problem-btn').onclick = async () => {
    const probId = document.getElementById('problem-id-input').value.trim().toUpperCase();
    if (!probId) return;
    
    if (state.solvedProblems.includes(probId)) {
        showNotice('problem-status', 'warning', 'You have already solved this problem on Codeforces.');
    } else {
        showNotice('problem-status', 'info', '<div class="loader"></div> Loading problem...', true);
    }
    
    document.getElementById('solver-actions').classList.add('hidden');
    
    try {
        const res = await apiCall('/api/load-problem', { problem_id: probId });
        state.currentProblemContext = res.problem_text;
        state.hintCount = 0;
        
        showNotice('problem-status', 'success', `Problem loaded — <a href="${res.url}" target="_blank">Open on Codeforces ↗</a>`, true);
        document.getElementById('solver-actions').classList.remove('hidden');
    } catch (err) {
        state.currentProblemContext = null;
        showNotice('problem-status', 'error', err.message);
    }
};

document.getElementById('hint-btn').onclick = () => {
    if (state.hintCount >= 5) {
        addChatMessage('user', 'Requested another hint.');
        addChatMessage('assistant', '⚠️ I\'ve already provided 5 hints for this problem. You have all the information needed to solve it! Try to implement the logic now.');
        return;
    }
    state.hintCount++;
    addChatMessage('user', `Requested problem hint #${state.hintCount}.`);
    sendChatRequest('hint');
};

document.getElementById('editorial-btn').onclick = () => {
    addChatMessage('user', 'Requested problem editorial.');
    sendChatRequest('editorial');
};

document.getElementById('recommend-btn').onclick = async () => {
    if (!state.cfHandle) {
        showNotice('recommend-status', 'error', 'Please enter a Codeforces handle first.');
        return;
    }
    if (state.selectedTags.size === 0) {
        showNotice('recommend-status', 'warning', 'Please select at least one topic tag.');
        return;
    }
    
    const minRating = parseInt(document.getElementById('min-rating').value);
    const maxRating = parseInt(document.getElementById('max-rating').value);
    const tags = Array.from(state.selectedTags);
    
    showNotice('recommend-status', 'info', '<div class="loader"></div> Finding recommendations...', true);
    
    try {
        const res = await apiCall('/api/recommend', {
            handle: state.cfHandle,
            tags: tags,
            min_rating: minRating,
            max_rating: maxRating
        });
        
        clearNotice('recommend-status');
        const topicsLabel = tags.join(', ');
        addChatMessage('user', `Recommending problems for tags: ${topicsLabel}.`);
        
        if (res.problems.length === 0) {
            addChatMessage('assistant', `⚠️ ${res.message}`);
            return;
        }
        
        let problemDataStr = "";
        res.problems.forEach((p, idx) => {
            problemDataStr += `Problem ${idx + 1}: ID=${p.contestId}${p.index}, Name=${p.name}, Rating=${p.rating}, ContestID=${p.contestId}, Index=${p.index}\n`;
        });
        
        const prompt = `Build exactly 3 custom HTML blocks for these Codeforces problems. Follow Kryphos dark UI guidelines.
        
${problemDataStr}
STRICT HTML TEMPLATE REQUIREMENT (Do not wrap in markdown code blocks):
<div style="background-color: #0f172a; border: 1px solid #1e293b; border-left: 4px solid #00ffc4; border-radius: 8px; padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
    <h3 style="color: #00ffc4; margin-top: 0; font-family: sans-serif; font-size: 1.15rem;">🎯 RECOMMENDATION {NUMBER}</h3>
    <p style="margin: 10px 0;">
        <a href="https://codeforces.com/problemset/problem/{CONTEST_ID}/{INDEX}" target="_blank" style="text-decoration: none; color: #ffffff; font-weight: bold; border: 1px solid #00f2fe; padding: 6px 14px; border-radius: 6px; background-color: #14233c; display: inline-block; font-size: 0.95rem;">
            ⭐ {CONTEST_ID}{INDEX} - {PROBLEM_NAME} [Rating: {RATING}] ⭐
        </a>
    </p>
    <p style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;">
        <strong style="color: #00f2fe;">Why it fits:</strong> {EXPLANATION}
    </p>
</div>`;

        sendChatRequest('recommend', null, prompt);
    } catch (err) {
        showNotice('recommend-status', 'error', err.message);
    }
};

document.getElementById('send-chat-btn').onclick = () => {
    const msg = chatInput.value.trim();
    if (!msg) return;
    
    chatInput.value = '';
    addChatMessage('user', msg);
    state.chatHistory.push({role: "user", content: msg});
    sendChatRequest('chat', msg);
};

chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        document.getElementById('send-chat-btn').click();
    }
});

// Interactive Particle Background
const canvas = document.getElementById('bg-canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouse = { x: null, y: null };

    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.x;
        mouse.y = e.y;
    });
    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initParticles();
    }

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 1;
            this.speedX = (Math.random() * 1) - 0.5;
            this.speedY = (Math.random() * 1) - 0.5;
            this.color = `rgba(0, 255, 102, ${Math.random() * 0.5 + 0.1})`; // Neon green
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x > canvas.width || this.x < 0) this.speedX *= -1;
            if (this.y > canvas.height || this.y < 0) this.speedY *= -1;

            // Interactive effect: move away from mouse
            if (mouse.x != null && mouse.y != null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 100) {
                    let forceDirectionX = dx / distance;
                    let forceDirectionY = dy / distance;
                    let force = (100 - distance) / 100;
                    this.speedX -= forceDirectionX * force * 0.5;
                    this.speedY -= forceDirectionY * force * 0.5;
                }
            }
            
            // max speed cap
            if (this.speedX > 1.5) this.speedX = 1.5;
            if (this.speedX < -1.5) this.speedX = -1.5;
            if (this.speedY > 1.5) this.speedY = 1.5;
            if (this.speedY < -1.5) this.speedY = -1.5;
        }
        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        let numParticles = Math.min((canvas.width * canvas.height) / 10000, 150); // density
        for (let i = 0; i < numParticles; i++) {
            particles.push(new Particle());
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
            
            // Connect close particles with a line
            for (let j = i; j < particles.length; j++) {
                let dx = particles[i].x - particles[j].x;
                let dy = particles[i].y - particles[j].y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 80) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(0, 255, 102, ${0.2 - distance/400})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animateParticles);
    }

    resizeCanvas();
    animateParticles();
}
