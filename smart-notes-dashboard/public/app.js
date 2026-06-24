/* =========================================================================
   Tomatrix App Logic - Task 14 UI JS
   ========================================================================= */

// Sample Data Sets for Ingestion
const SAMPLES = {
    mitosis: `Okay, so let's start the lecture on cell biology today... Mitosis is what we are focusing on. Mitosis is super critical because it's cell division that makes two identical daughter cells, literally clones of each other with the same DNA. Students, make sure you write down the stages. The easy way to remember the sequence is PMAT. P is Prophase where DNA condenses. M is Metaphase, this is where the chromosomes align right in the middle of the cell. Then Anaphase, chromosomes are pulled apart, and Telophase where new nuclei form. And don't forget cytokinesis, which splits the cytoplasm at the very end to separate them. I'll ask about spindle fibers next time - they pull them to opposite poles. Make sure to draw a diagram of this.`,
    quantum: `Alright, let's look at quantum mechanics. The core concepts are quite mind-bending. First is superposition. In the quantum world, particles don't have to be just 0 or 1, they exist in multiple states at the same time, until they are observed, then they collapse into one state. Next is entanglement. This is where two particles are linked. If you change or measure one, the other changes instantly, even if they are light-years apart! Einstein called it spooky action at a distance. These concepts are used to build quantum computers. Instead of normal bits, they use qubits. But it's hard because of decoherence. Any noise from the environment ruins the quantum state and causes errors, which is a major engineering hurdle.`
};

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const rawNotesInput = document.getElementById('raw-notes');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.getElementById('connection-status');
    
    // Sample buttons
    const sampleMitosisBtn = document.getElementById('sample-mitosis');
    const sampleQuantumBtn = document.getElementById('sample-quantum');
    
    // Accordion elements
    const togglePromptBtn = document.getElementById('toggle-prompt-config');
    const promptConfigContent = document.getElementById('prompt-config-content');
    const jsonConfigCode = document.getElementById('json-config-code');
    const copyPromptBtn = document.getElementById('copy-prompt-btn');
    
    // Output Section Elements
    const summarySection = document.getElementById('summary-section');
    const summaryEmpty = document.getElementById('summary-empty');
    const summaryContent = document.getElementById('summary-content');
    const takeawaysListUl = document.getElementById('takeaways-list-ul');
    
    const checklistSection = document.getElementById('checklist-section');
    const checklistEmpty = document.getElementById('checklist-empty');
    const checklistContent = document.getElementById('checklist-content');
    const checklistItemsContainer = document.getElementById('checklist-items-container');
    const checklistProgressContainer = document.getElementById('checklist-progress-container');
    const progressText = document.getElementById('progress-text');
    const progressBarFill = document.getElementById('progress-bar-fill');
    
    let loadedPromptConfigText = "";

    // 1. Fetch LLM Prompt Configuration & Set Indicator Status
    async function initApp() {
        try {
            const res = await fetch('/api/prompt_config');
            if (res.ok) {
                const config = await res.json();
                loadedPromptConfigText = JSON.stringify(config, null, 2);
                jsonConfigCode.textContent = loadedPromptConfigText;
            } else {
                jsonConfigCode.textContent = "Failed to load system prompt instructions.";
            }
        } catch (e) {
            console.error("Failed to load prompt config:", e);
            jsonConfigCode.textContent = "Failed to load system prompt instructions.";
        }
        
        // Initial dry check of analyze endpoint to determine mock vs real API mode
        try {
            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes: '' })
            });
            if (res.ok) {
                const data = await res.json();
                updateStatusBadge(data.mode);
            }
        } catch (e) {
            updateStatusBadge('simulated');
        }
    }

    function updateStatusBadge(mode) {
        statusIndicator.className = 'status-indicator';
        if (mode === 'api') {
            statusIndicator.classList.add('live');
            statusText.textContent = 'Live API Mode';
        } else {
            statusIndicator.classList.add('simulated');
            statusText.textContent = 'Simulated Mode';
        }
    }

    // 2. Event Listeners for Accordion
    togglePromptBtn.addEventListener('click', () => {
        togglePromptBtn.classList.toggle('active');
        promptConfigContent.classList.toggle('hidden');
    });

    copyPromptBtn.addEventListener('click', () => {
        if (loadedPromptConfigText) {
            navigator.clipboard.writeText(loadedPromptConfigText).then(() => {
                copyPromptBtn.textContent = "Copied!";
                setTimeout(() => { copyPromptBtn.textContent = "Copy"; }, 2000);
            }).catch(err => {
                console.error("Copy failed", err);
            });
        }
    });

    // 3. Loading Samples
    sampleMitosisBtn.addEventListener('click', () => {
        rawNotesInput.value = SAMPLES.mitosis;
        rawNotesInput.focus();
    });

    sampleQuantumBtn.addEventListener('click', () => {
        rawNotesInput.value = SAMPLES.quantum;
        rawNotesInput.focus();
    });

    // 4. Form Submission and Analysis Call
    analyzeBtn.addEventListener('click', async () => {
        const text = rawNotesInput.value.trim();
        if (!text) {
            alert("Please paste or load some notes to analyze!");
            return;
        }

        // Toggle Loading UI State
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        analyzeBtn.disabled = true;
        rawNotesInput.disabled = true;

        try {
            const startTime = Date.now();
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes: text })
            });

            // Ensure a minimum visual transition delay of 1.2s for simulated feel if fast
            const elapsed = Date.now() - startTime;
            if (elapsed < 1200) {
                await new Promise(r => setTimeout(r, 1200 - elapsed));
            }

            if (!response.ok) {
                throw new Error(`Server returned error status: ${response.status}`);
            }

            const result = await response.json();
            renderDashboard(result);
            updateStatusBadge(result.mode);

        } catch (error) {
            console.error("Analysis failed:", error);
            alert(`Error analyzing notes: ${error.message}. Running fallback simulated display...`);
            // Run fallback simulated display anyway
            renderDashboard({
                summary: [
                    "Failed to connect to API, but loaded local conceptual takeaway model.",
                    "mitosis divides cellular bodies into identical daughter blueprints.",
                    "Quantum qubits exist in multiple superposition paths simultaneously."
                ],
                actionItems: [
                    "Double check your server connections in server.py.",
                    "Verify your API Key in your local .env configuration.",
                    "Perform a manual test review of the checklist items."
                ],
                mode: 'simulated'
            });
        } finally {
            // Restore UI Input States
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            analyzeBtn.disabled = false;
            rawNotesInput.disabled = false;
        }
    });

    // 5. Render Output Dashboard (Summaries & Action Checklist)
    function renderDashboard(data) {
        // Toggle Empty states
        summaryEmpty.classList.add('hidden');
        checklistEmpty.classList.add('hidden');
        
        summaryContent.classList.remove('hidden');
        checklistContent.classList.remove('hidden');
        checklistProgressContainer.classList.remove('hidden');

        // Clear existing items
        takeawaysListUl.innerHTML = '';
        checklistItemsContainer.innerHTML = '';

        // A. Render Takeaways
        const summaryPoints = data.summary || [];
        if (summaryPoints.length === 0) {
            takeawaysListUl.innerHTML = '<li class="takeaway-item" style="animation-delay: 0.1s;"><span class="takeaway-bullet">💡</span><span class="takeaway-text">No summary takeaways returned. Try adding more detail.</span></li>';
        } else {
            summaryPoints.forEach((point, index) => {
                const li = document.createElement('li');
                li.className = 'takeaway-item';
                li.style.animationDelay = `${index * 0.1}s`;
                
                li.innerHTML = `
                    <span class="takeaway-bullet">✦</span>
                    <span class="takeaway-text">${escapeHtml(point)}</span>
                `;
                takeawaysListUl.appendChild(li);
            });
        }

        // B. Render Checklist
        const actionItems = data.actionItems || [];
        if (actionItems.length === 0) {
            checklistItemsContainer.innerHTML = '<p class="text-muted" style="font-size: 13px; padding: 20px; text-align: center;">No action items detected in these notes.</p>';
            updateProgress(0, 0);
        } else {
            actionItems.forEach((item, index) => {
                const cardId = `check-item-${index}`;
                const itemDiv = document.createElement('label');
                itemDiv.className = 'checklist-item';
                itemDiv.setAttribute('for', cardId);
                itemDiv.style.animationDelay = `${index * 0.1}s`;

                itemDiv.innerHTML = `
                    <input type="checkbox" id="${cardId}" class="checklist-checkbox-input">
                    <span class="checkbox-custom">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="4">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </span>
                    <span class="checklist-text">${escapeHtml(item)}</span>
                `;

                // Add state listener
                const checkbox = itemDiv.querySelector('input');
                checkbox.addEventListener('change', () => {
                    handleCheckboxChange();
                });

                checklistItemsContainer.appendChild(itemDiv);
            });
            
            // Set initial progress
            updateProgress(0, actionItems.length);
        }
    }

    // 6. Handle Checklist Changes & Progress Tracking
    function handleCheckboxChange() {
        const checkboxes = checklistItemsContainer.querySelectorAll('.checklist-checkbox-input');
        const total = checkboxes.length;
        let checkedCount = 0;

        checkboxes.forEach(cb => {
            if (cb.checked) {
                checkedCount++;
            }
        });

        updateProgress(checkedCount, total);

        // Play Confetti Celebration at 100% completion
        if (checkedCount === total && total > 0) {
            triggerConfetti();
        }
    }

    function updateProgress(checked, total) {
        if (total === 0) {
            progressText.textContent = '0% Complete';
            progressBarFill.style.width = '0%';
            return;
        }

        const percentage = Math.round((checked / total) * 100);
        progressText.textContent = `${percentage}% Complete (${checked}/${total})`;
        progressBarFill.style.width = `${percentage}%`;
    }

    // HTML Escaper for safety
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    // 7. Confetti Effect Canvas Renderer (Self-contained, offline-compatible)
    function triggerConfetti() {
        const canvas = document.getElementById('confetti-canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const colors = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];
        const particles = [];

        // Generate confetti pieces
        for (let i = 0; i < 120; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height - canvas.height,
                r: Math.random() * 5 + 3,
                d: Math.random() * canvas.height,
                color: colors[Math.floor(Math.random() * colors.length)],
                tilt: Math.random() * 10 - 5,
                tiltAngleIncremental: Math.random() * 0.05 + 0.02,
                tiltAngle: 0
            });
        }

        let animationFrameId;
        const startTime = Date.now();

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let active = false;

            particles.forEach((p, idx) => {
                p.tiltAngle += p.tiltAngleIncremental;
                p.y += (Math.cos(p.d) + 3 + p.r / 2) / 2;
                p.x += Math.sin(p.tiltAngle);
                p.tilt = Math.sin(p.tiltAngle - idx / 3) * 10;

                if (p.y < canvas.height) {
                    active = true;
                }

                ctx.beginPath();
                ctx.lineWidth = p.r;
                ctx.strokeStyle = p.color;
                ctx.moveTo(p.x + p.tilt + p.r / 2, p.y);
                ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 2);
                ctx.stroke();
            });

            // Stop animations after 4 seconds to save memory
            if (active && Date.now() - startTime < 4000) {
                animationFrameId = requestAnimationFrame(draw);
            } else {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                cancelAnimationFrame(animationFrameId);
            }
        }

        // Recalculate canvas size on window resize
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });

        draw();
    }

    // App Boot Init
    initApp();
});
