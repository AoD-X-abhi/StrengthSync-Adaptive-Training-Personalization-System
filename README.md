<div align="center">

# StrengthSyn

### The Smart Progressive Overload Coach That Actually Listens to You

StrengthSyn is an intelligent, adaptive workout engine designed for serious lifters who want **consistent, long-term strength progress** — without the guesswork.

Unlike basic workout loggers, StrengthSyn **analyzes your performance in real time** using:

- **RPE (Rate of Perceived Exertion)**
- **Reps Completed**
- **Wellness Indicators** (sleep, stress, soreness, readiness)

…and instantly adjusts your next set, training volume, and progression.

**No more stagnant routines. No more random jumps in weight.**  
StrengthSyn learns your strength curve and **progresses you exactly when you're ready**.

Built with a minimalist UI, fast navigation, and distraction-free workflow that’s perfect for use inside the gym.

<br>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?logo=chart-dot-js&logoColor=white)
![Responsive](https://img.shields.io/badge/Mobile_First-10B981?logo=responsive-design&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-10B981)

<br><br>

</div>

### 🔐 Login & Onboarding

StrengthSyn launches straight into a clean and distraction-free login screen designed for speed.  
Just enter a username and password once — your account is created instantly with no emails, no OTPs, and no friction.

The minimalist layout makes it perfect for quick gym access, even with sweaty hands or low network connectivity.

<div align="center">
<img src="screenshots/login.jpg" width="100%" alt="StrengthSyn Login Screen"/>
</div>

### 📊 Dashboard Overview

Your dashboard gives you a complete visual summary of your training:

- **Training Streak Ring** — tracks your consistency and motivates you to stay on track  
- **Weekly Volume & Intensity Charts** powered by Chart.js  
- **Last 7 Sessions Overview** including reps, weight, and total load  
- **Wellness Score** that influences your daily training targets  
- **Fast-start Workout Button** for immediate session launch

Everything updates automatically based on your logged sets.

<div align="center">
<img src="screenshots/dashboard.jpg" width="100%" alt="StrengthSyn Dashboard with Stats & Streak"/>
</div>

### 🏋️ Live Workout Session

During every session, StrengthSyn becomes your personal strength coach.

- Enter **reps + RPE** after each set  
- System instantly adjusts **next set’s weight or reps**  
- Smart messages guide your effort:  
  - “Great set!”  
  - “You’ve got more in the tank.”  
  - “Reduce load — fatigue detected.”  
- Automatically builds your session log  
- Zero clutter — fully optimized for one-handed phone use

Every set you complete teaches the model more about your strength curve.

<div align="center">
<img src="screenshots/workout.jpg" width="100%" alt="Live Workout Session with Real-Time RPE Feedback"/>
</div>


## Tech Stack

| Layer         | Technology           |
|-------------|----------------------|
| Backend       | Python + Flask       |
| Frontend      | HTML + Tailwind CSS + Vanilla JS |
| Database      | MySQL                |
| Charts        | Chart.js             |
| Auth & Hashing| Werkzeug Security    |

</div>

## Requirements

```bash
pip install flask flask-cors pandas scikit-learn mysql-connector-python gunicorn joblib lightgbm cloudpickle


git clone https://github.com/AoD-X-abhi/StrengthSync-Adaptive-Training-Personalization-System.git
```