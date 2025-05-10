
# Feedback Report Generator

A Django-based microservice for generating and serving student feedback reports in **PDF** and **HTML** formats asynchronously using **Celery**, **Redis**, and **Docker Compose**.  
Package management is handled using **Poetry** for reproducible environments.

---

##  Project Structure

```

.
├── assignment/                # Django app containing views, models, tasks, serializers
├── feedback\_report/           # Django project configuration
├── docker-compose.yml         # Docker Compose config
├── Dockerfile                 # Dockerfile for Django app
├── redis/                     # Redis service for Celery
├── media/                     # Directory to store generated PDF reports
├── poetry.lock
├── pyproject.toml
├── README.md
└── requirements.txt

````

---

##  Getting Started

###  Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Poetry](https://python-poetry.org/docs/)

---

##  Setup & Run Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ShaibaliniKapuri/Feedback_report_generator.git
cd Feedback_report_generator
````

---

### 2. Create `.env` (if applicable)

If your application expects any environment variables, create a `.env` file in the root directory (not mandatory for this demo implementation unless extended).

---

### 3. Install Dependencies (for local non-docker testing)

```bash
poetry install
```

Activate the environment:

```bash
poetry shell
```

Run migrations:

```bash
python manage.py migrate
```

---

### 4️⃣ Run with Docker Compose (Recommended)

Build and run the full stack:

```bash
docker-compose up --build
```

This will start:

* Django web server
* Redis server (for Celery)
* Celery worker
* Flower (for monitoring tasks at `http://localhost:5555`)

---

##  Available API Endpoints

---

### 📄 1. Generate HTML Report

* **URL:** `POST /assignment/html`

* **Description:**
  Accepts event data as JSON, enqueues a Celery task to process the events asynchronously:

  * Events are sorted by the `unit` field.
  * A question alias (`Q1`, `Q2`, etc.) is assigned based on the sorted order.
  * Generates an HTML report showing the order of units answered.
  * Stores the generated HTML content in PostgreSQL using an efficient schema for large text data.

* **Input Example (JSON):**

  ```json
  [

  {

    "namespace": "ns_example",

    "student_id": "00a9a76518624b02b0ed57263606fc26",

    "events": [

      {

        "type": "saved_code",

        "created_time": "2024-07-21 03:04:55.939000+00:00",

        "unit": 17

      },

    ]

  }

  ]
  ```

* **Output Example:**

  ```json
  {
    "task_id": "abc12345"
  }
  ```

---

### 📄 2. Get HTML Report by Task ID

* **URL:** `GET /assignment/html/<task_id>`

* **Description:**

  * Checks the status of the HTML generation task using Celery's result backend.
  * Returns:

    * `running` / `completed` / `failed`
  * If completed, retrieves and returns the stored HTML content from the database.

* **Output Example (Completed):**

  ```html
  <h2>Student ID: 00a9a76518624b02b0ed57263606fc26</h2>
  <p>Event Order: Q1 -> Q1 -> Q3 -> Q1 -> Q2</p>
  ```

---

### 📄 3. Generate PDF Report

* **URL:** `POST /assignment/pdf`

* **Description:**
  Accepts the same event data JSON payload as the HTML endpoint, enqueues a Celery task to:

  * Process event data similarly (ordering and aliasing).
  * Generate a PDF report with the same event order.
  * Store the generated PDF in file storage or PostgreSQL, based on efficient storage design for large binary files.

* **Input Example (JSON):**

  ```json
  [

  {

    "namespace": "ns_example",

    "student_id": "00a9a76518624b02b0ed57263606fc26",

    "events": [

      {

        "type": "saved_code",

        "created_time": "2024-07-21 03:04:55.939000+00:00",

        "unit": 17

      },

    ]

  }

  ]
  ```

* **Output Example:**

  ```json
  {
    "task_id": "xyz67890"
  }
  ```

---

### 📄 4. Get PDF Report by Task ID

* **URL:** `GET /assignment/pdf/<task_id>`

* **Description:**

  * Checks the status of the PDF generation task.
  * Returns:

    * `running` / `completed` / `failed`
  * If completed, retrieves and serves the PDF file as a downloadable attachment.

* **Response (Completed):**

  * **Content-Type:** `application/pdf`
  * **Attachment:** PDF file download prompt in browser.

---

## 📑 Task Monitoring

* Flower dashboard for live Celery task status at:
  [http://localhost:5555](http://localhost:5555)

---

##  Assumptions & Design Decisions

* **PDF files** are generated asynchronously and stored in the `media/pdf_reports/` directory.
* **HTML reports** are stored as text content in the database.
* Task states are managed using **Celery** and **Redis**.
* **Docker Compose** orchestrates the multi-container environment for portability.
* Used **Poetry** for modern dependency management.
* Added robust API error handling and status reporting for asynchronous operations.
* Flower used for Celery task queue monitoring.

---

##  How to Stop the App

```bash
docker-compose down
```

---

##  Git Ignore Recommendations

Recommended `.gitignore` entries:

```
__pycache__/
*.pyc
*.pyo
*.pyd
env/
.venv/
media/
*.sqlite3
*.log
poetry.lock
.idea/
.vscode/
.env
__pycache__/
*.DS_Store
```

---

##  Author

Shaibalini Kapuri
GitHub: [@ShaibaliniKapuri](https://github.com/ShaibaliniKapuri)

---

