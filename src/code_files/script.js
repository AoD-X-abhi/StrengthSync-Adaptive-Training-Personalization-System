const API_BASE_URL = '';

document.addEventListener('DOMContentLoaded', () => {
    const page = window.location.pathname.split("/").pop() || "index.html";
    const username = localStorage.getItem('workoutAppUsername');

    // Redirect to login if not logged in (except on index.html)
    if (page !== 'index.html' && page !== '' && !username) {
        window.location.href = 'index.html';
        return;
    }

    // === LOGIN PAGE ===
    if (page === 'index.html' || page === '') {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value;

                if (!username || !password) {
                    alert('Please enter both username and password');
                    return;
                }

                try {
                    const response = await fetch(`${API_BASE_URL}/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || 'Login failed');
                    }

                    localStorage.setItem('workoutAppUsername', username);

                    if (data.has_baseline) {
                        window.location.href = 'dashboard.html';
                    } else {
                        alert('Welcome! Let’s set your starting strength levels.');
                        window.location.href = 'baseline.html';
                    }

                } catch (err) {
                    alert('Login failed: ' + err.message);
                }
            });
        }
    }

    // === DASHBOARD PAGE ===
    if (page === 'dashboard.html') {
        // Username already auto-filled in HTML via localStorage → no need to set again

        const viewStatsBtn = document.getElementById('view-stats-btn');
        if (viewStatsBtn) {
            viewStatsBtn.addEventListener('click', fetchUserStats);
        }
        // Session History button now uses onclick → no JS listener needed
    }

    // === BASELINE PAGE ===
    if (page === 'baseline.html') {
        const baselineForm = document.getElementById('baseline-form');
        if (baselineForm) {
            baselineForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const baselineData = {
                    "Barbell Squats": { 
                        weight: document.getElementById('squat-weight').value, 
                        reps: document.getElementById('squat-reps').value 
                    },
                    "Bench Press": { 
                        weight: document.getElementById('bench-weight').value, 
                        reps: document.getElementById('bench-reps').value 
                    },
                    "Barbell Rows": { 
                        weight: document.getElementById('row-weight').value, 
                        reps: document.getElementById('row-reps').value 
                    }
                };

                try {
                    const response = await fetch(`${API_BASE_URL}/save_baseline`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username: username, baseline: baselineData }),
                    });

                    if (!response.ok) {
                        const result = await response.json();
                        throw new Error(result.error || 'Failed to save baseline.');
                    }

                    alert("Baseline saved! Redirecting to your dashboard.");
                    window.location.href = 'dashboard.html';
                } catch (error) {
                    alert(`Error saving baseline: ${error.message}`);
                }
            });
        }
    }

    // === DAILY CHECK-IN PAGE ===
    if (page === 'daily.html') {
        const dailyForm = document.getElementById('daily-form');
        if (dailyForm) {
            dailyForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const wellnessData = {
                    username: username,
                    sleep_quality: parseInt(document.getElementById('sleep').value),
                    readiness: parseInt(document.getElementById('readiness').value),
                    stress: parseInt(document.getElementById('stress').value),
                    soreness: parseInt(document.getElementById('soreness').value)
                };

                try {
                    const response = await fetch(`${API_BASE_URL}/get_workout`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(wellnessData),
                    });

                    if (!response.ok) {
                        const data = await response.json();
                        throw new Error(data.error || 'Failed to get workout');
                    }

                    const data = await response.json();
                    localStorage.setItem('todaysWorkout', JSON.stringify(data));
                    window.location.href = 'workout.html';
                } catch (error) {
                    alert(`Error starting workout: ${error.message}`);
                }
            });
        }
    }

    // === WORKOUT SESSION PAGE ===
    if (page === 'workout.html') {
        const workoutDisplay = document.getElementById('workout-display');
        if (!workoutDisplay) return;

        let fullSession = JSON.parse(localStorage.getItem('todaysWorkout'));
        let workoutPlan = fullSession?.workout_plan || [];
        let currentExerciseIndex = 0;
        let currentSetNumber = 1;

        if (!fullSession || workoutPlan.length === 0) {
            document.getElementById('exercise-name').innerText = "No Workout Loaded";
            document.getElementById('set-info').innerText = "Please return to the daily check-in page.";
            document.getElementById('log-set-form').style.display = 'none';
            return;
        }

        let currentExerciseState = workoutPlan[currentExerciseIndex];

        const updateDisplay = () => {
            if (!currentExerciseState) return;

            document.getElementById('exercise-name').innerText = currentExerciseState.exercise_name;

            let messageHTML = `
                <div class="text-2xl font-bold text-cyan-300 mb-2">
                    Set ${currentSetNumber} of 4
                </div>
                <div class="text-xl text-gray-200">
                    Perform exactly <strong class="text-white">${currentExerciseState.recommended_reps} reps</strong> 
                    with <strong class="text-white">${currentExerciseState.recommended_weight} kg</strong>
                </div>
            `;

            if (currentExerciseState.message) {
                messageHTML += `
                    <div class="mt-5 p-5 bg-cyan-900/60 border border-cyan-600 rounded-xl text-cyan-200 font-medium text-lg text-center shadow-lg">
                        ${currentExerciseState.message}
                    </div>
                `;
            }

            document.getElementById('set-info').innerHTML = messageHTML;

            if (typeof updateProgress === 'function') {
                updateProgress(currentSetNumber);
            }
        };

        const logSetToTable = (set, weight, reps, rpe) => {
            const row = document.getElementById('log-body').insertRow();
            row.innerHTML = `
                <td class="px-4 py-2 border-t border-gray-700">${set}</td>
                <td class="px-4 py-2 border-t border-gray-700">${weight} kg</td>
                <td class="px-4 py-2 border-t border-gray-700">${reps}</td>
                <td class="px-4 py-2 border-t border-gray-700">${rpe}</td>
            `;
        };

        const clearLogTable = () => {
            document.getElementById('log-body').innerHTML = "";
        };

        const logSetForm = document.getElementById('log-set-form');
        if (logSetForm) {
            logSetForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const repsDone = parseInt(document.getElementById('reps-done').value);
                const rpeLogged = parseInt(document.getElementById('rpe-logged').value);

                logSetToTable(currentSetNumber, currentExerciseState.recommended_weight, repsDone, rpeLogged);

                const performanceData = {
                    username: username,
                    session_id: fullSession.session_id,
                    exercise_name: currentExerciseState.exercise_name,
                    set_number: currentSetNumber,
                    reps_done: repsDone,
                    rpe_logged: rpeLogged,
                    weight_lifted: currentExerciseState.recommended_weight
                };

                try {
                    const response = await fetch(`${API_BASE_URL}/get_next_set`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(performanceData),
                    });

                    if (!response.ok) {
                        const data = await response.json();
                        throw new Error(data.error || 'Server error');
                    }

                    const data = await response.json();

                    if (currentSetNumber >= 4) {
                        currentExerciseIndex++;
                        if (currentExerciseIndex >= workoutPlan.length) {
                            document.getElementById('workout-display').innerHTML = `
                                <h1 class="text-5xl font-bold text-green-400">Workout Complete!</h1>
                                <p class="text-2xl text-gray-300 mt-6">Amazing work today!</p>
                            `;
                            logSetForm.style.display = 'none';
                            return;
                        } else {
                            currentSetNumber = 1;
                            currentExerciseState = workoutPlan[currentExerciseIndex];
                            currentExerciseState.message = "Starting next exercise!";
                            clearLogTable();
                        }
                    } else {
                        currentSetNumber++;
                        currentExerciseState.recommended_weight = data.next_weight;
                        currentExerciseState.message = data.message;
                    }

                    updateDisplay();
                    logSetForm.reset();
                } catch (error) {
                    alert(`Could not get next set: ${error.message}`);
                }
            });
        }

        updateDisplay();
    }
});

// === ONLY STATS FUNCTION REMAINS (for dashboard "My Stats" button) ===
async function fetchUserStats() {
    const username = localStorage.getItem('workoutAppUsername');
    const resultsDiv = document.getElementById('stats-results');

    if (!resultsDiv) return;

    resultsDiv.innerHTML = '<p class="text-gray-400">Loading stats...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/user_stats/${username}`);
        if (!response.ok) throw new Error('Failed to load stats');

        const data = await response.json();

        if (data.length === 0) {
            resultsDiv.innerHTML = '<p class="text-gray-400">Not enough data yet. Keep training!</p>';
            return;
        }

        let tableHTML = `
            <h3 class="text-2xl font-bold text-purple-300 mb-6">My Strength Stats</h3>
            <table class="min-w-full bg-gray-900 rounded-lg">
                <thead>
                    <tr>
                        <th class="px-6 py-4 text-left border-b-2 border-gray-700">Exercise</th>
                        <th class="px-6 py-4 text-left border-b-2 border-gray-700">Total Sets</th>
                        <th class="px-6 py-4 text-left border-b-2 border-gray-700">Avg RPE</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.forEach(stat => {
            const avgRPE = parseFloat(stat.average_rpe).toFixed(1);
            tableHTML += `
                <tr>
                    <td class="px-6 py-4 border-t border-gray-700">${stat.exercise_name}</td>
                    <td class="px-6 py-4 border-t border-gray-700">${stat.total_sets}</td>
                    <td class="px-6 py-4 border-t border-gray-700">${avgRPE}</td>
                </tr>
            `;
        });

        tableHTML += '</tbody></table>';
        resultsDiv.innerHTML = tableHTML;
    } catch (error) {
        resultsDiv.innerHTML = `<p class="text-red-400">Error loading stats: ${error.message}</p>`;
    }
}