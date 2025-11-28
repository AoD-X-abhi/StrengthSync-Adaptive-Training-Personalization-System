DROP DATABASE IF EXISTS USER_WORKOUTS;
CREATE DATABASE USER_WORKOUTS;
USE USER_WORKOUTS;

CREATE TABLE users (
    username VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE WorkoutSessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
CREATE TABLE Workouts (
    workout_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    exercise_name VARCHAR(255) NOT NULL,
    base_weight DECIMAL(10, 2) NOT NULL,
    base_reps INT NOT NULL,
    UNIQUE KEY uq_user_exercise (username, exercise_name),
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
CREATE TABLE DailyWellness (
    wellness_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    log_date DATE NOT NULL,
    sleep_quality INT,
    readiness INT,
    stress INT,
    soreness INT,
    UNIQUE KEY uq_user_date (username, log_date),
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
CREATE TABLE PerformedSets (
    set_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    username VARCHAR(255) NOT NULL,
    exercise_name VARCHAR(255) NOT NULL,
    set_number INT NOT NULL,
    performed_reps INT,
    performed_weight DECIMAL(10, 2),
    performed_rpe INT,
    FOREIGN KEY (session_id) REFERENCES WorkoutSessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
CREATE INDEX idx_username_sessions ON WorkoutSessions(username);
CREATE INDEX idx_username_sets ON PerformedSets(username);
CREATE INDEX idx_username_wellness ON DailyWellness(username);
CREATE INDEX idx_exercise_name ON PerformedSets(exercise_name);
CREATE INDEX idx_session_date ON WorkoutSessions(session_date);
