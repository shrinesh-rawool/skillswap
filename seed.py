"""Run once to populate demo data: python seed.py (use --force to reset existing DB)"""
import hashlib
import os
import sqlite3
import sys
from app import DB, init_db


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


users = [
    ("Alex Rivera", "alex@demo.com", "demo123", "MIT", "#6366f1", "Full-stack developer who loves teaching Python and React. Always happy to swap coding help for language lessons."),
    ("Priya Sharma", "priya@demo.com", "demo123", "Stanford", "#8b5cf6", "Music theory geek and aspiring data scientist. Can teach piano, guitar basics, and music production."),
    ("Jordan Lee", "jordan@demo.com", "demo123", "UC Berkeley", "#10b981", "Bilingual in English and Mandarin. Studying economics, happy to tutor math and business concepts."),
    ("Sam Okonkwo", "sam@demo.com", "demo123", "NYU", "#f59e0b", "Graphic designer and UI/UX enthusiast. Can teach Figma, Illustrator, and design thinking."),
    ("Maria Gonzalez", "maria@demo.com", "demo123", "UCLA", "#ec4899", "Spanish native speaker, learning Japanese. Can teach Spanish conversation and essay writing."),
]

skills = [
    (1, "Python for Beginners", "Teach the fundamentals of Python — variables, loops, functions, and basic OOP. Perfect for complete beginners.", "Programming", "teach", "Intermediate", "Help with math or music theory"),
    (2, "Guitar Basics (Acoustic)", "Learn chords, strumming patterns, and how to read tabs. I can get you playing simple songs within a few sessions.", "Music", "teach", "Intermediate", "CSS / web development"),
    (3, "Mandarin Conversation", "Practice spoken Mandarin for everyday situations — greetings, shopping, travel. HSK 4 level.", "Languages", "teach", "Advanced", "English writing coaching"),
    (4, "Figma & UI Design", "Teach wireframing, prototyping, and building a polished UI in Figma. Portfolio projects included.", "Design", "teach", "Advanced", "Any programming help"),
    (5, "Spanish for Travelers", "Functional conversational Spanish covering travel, dining, and getting around. Native speaker.", "Languages", "teach", "Advanced", "Japanese practice partner"),
    (1, "Data Structures & Algorithms", "DSA prep for coding interviews — arrays, linked lists, trees, sorting. With practice problems.", "Programming", "teach", "Advanced", "Open to anything"),
    (2, "Music Theory Fundamentals", "Scales, chords, time signatures, and ear training. Great for anyone learning an instrument.", "Music", "teach", "Advanced", "Math tutoring"),
    (3, "Calculus Help Wanted", "Looking for someone to explain derivatives, integrals, and limits. Struggling with college calculus.", "Math", "learn", "Beginner", "Mandarin lessons in return"),
    (4, "Photography Basics Wanted", "Want to learn composition, lighting, and manual camera settings. Can swap design lessons.", "Arts & Crafts", "learn", "Beginner", "Figma / UI design lessons"),
    (5, "Japanese Conversation Practice", "Want a practice partner for conversational Japanese — I'm N4 level. Native Spanish in return.", "Languages", "learn", "Intermediate", "Spanish lessons"),
]


def seed(force=False):
    init_db()
    db = sqlite3.connect(DB)
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0 and not force:
        print("Database already populated. Skipping seed (pass --force to overwrite).")
        db.close()
        return

    db.executescript(
        """
        DELETE FROM messages;
        DELETE FROM reviews;
        DELETE FROM requests;
        DELETE FROM skills;
        DELETE FROM users;
        DELETE FROM sqlite_sequence;
        """
    )

    for name, email, pw, univ, color, bio in users:
        db.execute(
            "INSERT INTO users(name,email,password,university,avatar_color,bio) VALUES(?,?,?,?,?,?)",
            (name, email, hash_pw(pw), univ, color, bio),
        )
    for uid, title, desc, cat, stype, level, wants in skills:
        db.execute(
            "INSERT INTO skills(user_id,title,description,category,skill_type,level,wants_in_return) VALUES(?,?,?,?,?,?,?)",
            (uid, title, desc, cat, stype, level, wants),
        )

    # Requests
    db.execute(
        "INSERT INTO requests(from_user,to_user,skill_id,message,status) VALUES(?,?,?,?,?)",
        (3, 1, 1, "Hi Alex! I'd love to learn Python. I can offer Mandarin lessons in return.", "accepted"),
    )
    db.execute(
        "INSERT INTO requests(from_user,to_user,skill_id,message,status) VALUES(?,?,?,?,?)",
        (4, 2, 2, "I've always wanted to learn guitar. Can we trade for Figma lessons?", "accepted"),
    )
    db.execute(
        "INSERT INTO requests(from_user,to_user,skill_id,message,status) VALUES(?,?,?,?,?)",
        (5, 3, 3, "Hola! Soy Maria. I'd love Mandarin lessons and can teach Spanish.", "pending"),
    )

    # Reviews
    db.execute(
        "INSERT INTO reviews(reviewer_id,reviewee_id,rating,comment) VALUES(?,?,?,?)",
        (3, 1, 5, "Alex is a fantastic teacher! Very patient and explains things clearly. Learned so much in just two sessions."),
    )
    db.execute(
        "INSERT INTO reviews(reviewer_id,reviewee_id,rating,comment) VALUES(?,?,?,?)",
        (4, 2, 5, "Priya is amazing! She made guitar feel approachable. Great at adapting to different learning styles."),
    )

    # Messages
    db.execute("INSERT INTO messages(from_user,to_user,body) VALUES(?,?,?)", (3, 1, "Hey Alex! When are you free for our first Python session?"))
    db.execute("INSERT INTO messages(from_user,to_user,body) VALUES(?,?,?)", (1, 3, "Hi Jordan! How about Saturday at 2pm? We can use Google Meet."))
    db.execute("INSERT INTO messages(from_user,to_user,body) VALUES(?,?,?)", (3, 1, "Perfect! I'll send you the link. Looking forward to it!"))

    db.commit()
    db.close()
    print("Demo data seeded. Login: alex@demo.com / demo123")


if __name__ == "__main__":
    seed(force="--force" in sys.argv)