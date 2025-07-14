# BoletinOficial by Crate

A simplified, self-hosted clone of Argentina's *Boletín Oficial* built with Flask. It features a dashboard where official-looking documents are listed by type and date, and an admin panel to manage them.

---

## 🏦 Tech Stack

- **Backend**: Flask + SQLAlchemy (SQLite)
- **Frontend**: TailwindCSS
- **Database**: SQLite
- **Auth**: Cookie-based token system

---

## 🧹 Features

- 📜 Public site displaying official documents:
  - Filtered by **date**
  - Grouped by **type**
- 🔐 Admin login with persistent cookie
- 🛠️ Admin panel to:
  - Create new documents
  - Delete existing documents
- 🗓️ Document timestamps are handled automatically
- 🍪 Cookie system to:
  - Store visit date
  - Authenticate admin without needing to log in on every action

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/cr4t3/BoletinOficial.git
cd BoletinOficial
```

### 2. Install dependencies

Use a virtual environment if you prefer:

```bash
pip install -r requirements.txt
```

### 3. Setup environment variables

Copy the example file and configure as needed:

```bash
cp .env.example .env
```

Set the values accordingly. You'll need at least:

- `ADMIN_PASSWORD`
- `SECRET_KEY`

### 4. Initialize the database

The database will auto-create the tables on first run.However, **document types** (e.g., *Avisos Oficiales*, *Leyes*, etc.) must be manually inserted using a tool like **DB Browser for SQLite** or similar.

### 5. Run the app (development)

```bash
python app.py
```

> Note: Using `flask run` can lose port binding or environment detection depending on your setup. Prefer `python app.py` for consistent behavior.

### 6. Run in production

Use something like **Gunicorn** with a reverse proxy:

```bash
gunicorn app:app
```

---

## 📌 Notes

- This project is intended for local or internet use, **as long as the MIT license is respected**.
- No user registration or public admin access is supported.
- Document types are fixed and **cannot be modified via the admin panel**.
- You can customize styles directly in the HTML templates using Tailwind classes.

---

## 📄 License

This project is licensed under the MIT License.Made with ❤️ by **Crate**.
