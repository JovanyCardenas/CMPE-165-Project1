# Expense Tracker

**SJSU CMPE 165 — Software Engineering Process Management**
**Project 1: Software Product from Idea to Execution**

The **Expense Tracker** is a personal finance web application designed to help users record, organize, and better understand their income and spending.

The application provides a centralized location where users can track financial transactions, organize expenses into categories, monitor budgets, and view summaries of their financial activity.

This project is being developed for **CMPE 165 — Software Engineering Process Management** as part of Project 1. In addition to building a working software prototype, the project focuses on applying software project-management concepts including project selection, financial analysis, stakeholder analysis, leadership, risk management, decision analysis, and project evaluation.

---

## Project Status

**Current Phase:** Active Development

The project is currently being developed as a working prototype.

The primary development focus is creating a small, reliable application that demonstrates the core expense-tracking workflow while remaining achievable within the project's two-week development period.

---

## Problem

People make purchases across many different categories throughout the month, but it can be difficult to understand where their money is going without consistently tracking their financial activity.

Expenses may be spread across:

* Food and dining
* Transportation
* Housing
* Entertainment
* Shopping
* Utilities
* Education
* Subscriptions
* Other everyday purchases

Without an organized system, users may have difficulty determining:

* How much they are spending
* Which categories account for most of their expenses
* Whether they are staying within their budget
* How their income compares with their expenses
* Where they may be able to reduce unnecessary spending

The Expense Tracker is intended to simplify this process.

---

## Project Objective

The objective of the Expense Tracker is to provide users with a simple and accessible way to:

* Record income and expenses
* Organize transactions into categories
* Monitor monthly spending
* Create and track budgets
* View financial summaries
* Identify spending patterns

The application is intentionally focused on essential functionality rather than advanced financial services.

---

# Core Features

## Transaction Management

Users can record financial transactions including both income and expenses.

Transaction information may include:

* Transaction name or description
* Amount
* Transaction type
* Category
* Date
* Notes

Users can also update or remove transactions when necessary.

---

## Expense Categories

Transactions can be organized into categories to make spending easier to understand.

Example categories include:

* Food
* Transportation
* Housing
* Utilities
* Entertainment
* Shopping
* Education
* Health
* Subscriptions
* Other

Categories allow the application to calculate and display spending by type.

---

## Budget Tracking

Users can create budgets to help control their spending.

Budgets may be created for specific categories or for a general monthly spending limit.

The application can compare actual spending against the user's configured budget and show:

* Amount budgeted
* Amount spent
* Amount remaining
* Percentage of budget used

---

## Financial Dashboard

The dashboard provides a quick overview of the user's financial activity.

Information displayed may include:

* Total income
* Total expenses
* Current balance
* Monthly spending
* Remaining budget
* Recent transactions
* Spending by category

Charts and summary cards may be used to make financial information easier to understand.

---

## Transaction History and Filtering

Users can view previously recorded transactions.

Transactions may be filtered or searched using information such as:

* Transaction type
* Category
* Date
* Description

This allows users to review specific parts of their financial history without searching manually through every transaction.

---

# Planned / Future Features

The initial prototype focuses on the application's core expense-tracking functionality.

If development continues, additional features could include:

* Recurring transactions
* Savings goals
* Account tracking
* Receipt uploads
* CSV import/export
* Advanced financial reports
* Spending trend analysis
* Email notifications
* Budget warnings
* Debt tracking
* Shared household expenses
* Bank account integrations
* Mobile notifications

These features are considered future enhancements and are not required for the initial prototype.

---

# High-Level Data Concept

```text
User
│
├── Transactions
│   ├── Income
│   └── Expenses
│
├── Categories
│   ├── Food
│   ├── Transportation
│   ├── Housing
│   ├── Entertainment
│   └── Other Categories
│
├── Budgets
│   ├── Budget Amount
│   ├── Category
│   └── Spending Progress
│
└── Financial Dashboard
    ├── Total Income
    ├── Total Expenses
    ├── Balance
    ├── Budget Status
    └── Spending Analysis
```

The main design principle is:

> **Financial information should be simple to enter, easy to organize, and easy to understand.**

---

# Technology Stack

The project is currently being developed using:

* Python
* Django
* HTML
* Tailwind CSS
* JavaScript
* SQLite
* Git
* GitHub

Additional technologies used by the project infrastructure may include:

* Docker
* GitHub Actions
* PostgreSQL
* Render
* Gunicorn
* WhiteNoise

SQLite is used for local development. PostgreSQL may be used if the application is deployed to a production environment.

---

# Project Structure

The application uses the Django web framework.

A simplified project structure may look similar to:

```text
expense-tracker/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── expenses/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── core/
│
├── templates/
│
├── static/
│
├── manage.py
├── requirements.txt
├── README.md
└── .env.example
```

The exact structure may change as development continues.

---

# Team Members

* [Team Member Name]
* [Team Member Name]
* [Team Member Name]

Replace this section with the names of the CMPE 165 project team members.

---

# Development Workflow

The project uses Git and GitHub for version control.

A typical workflow is:

1. Pull the latest changes.
2. Create or switch to a development branch.
3. Implement a feature or fix.
4. Test the changes locally.
5. Commit the changes.
6. Push the branch to GitHub.
7. Open a pull request when appropriate.
8. Review and merge the changes.

Example:

```bash
git checkout main
git pull origin main

git checkout -b feature/transaction-management

# Make changes

git add .
git commit -m "Add transaction management"
git push -u origin feature/transaction-management
```

---

# Running the Project Locally

## 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

Replace `<repository-url>` and `<repository-folder>` with the project's actual GitHub information.

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file using `.env.example` as a reference if environment variables are required.

---

## 5. Run Database Migrations

```bash
python manage.py migrate
```

---

## 6. Create an Administrator Account

Optional:

```bash
python manage.py createsuperuser
```

---

## 7. Start the Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# Running with Docker

If Docker is being used, build and start the project with:

```bash
docker compose up --build
```

Run migrations:

```bash
docker compose exec web python manage.py migrate
```

Create an administrator:

```bash
docker compose exec web python manage.py createsuperuser
```

Stop the containers:

```bash
docker compose down
```

---

# AI-Assisted Development

Generative AI tools are being used as development assistants during this project.

## AI Tools Used

AI tools used during development may include:

* ChatGPT
* GitHub Copilot or other AI coding assistants, if used by team members

---

## How AI Assisted Development

AI tools have been used to assist with tasks such as:

* Brainstorming application architecture
* Reviewing project requirements
* Generating initial code examples
* Troubleshooting Django errors
* Improving HTML and Tailwind CSS layouts
* Suggesting model and database structures
* Reviewing code
* Improving documentation
* Identifying possible edge cases and testing scenarios

AI-generated suggestions are reviewed by team members before being incorporated into the project.

---

## AI-Generated Code Requiring Modification

During development, the team will document at least one example where AI-generated code did not work correctly or required human modification.

Example to update before submission:

> An AI-generated implementation initially produced code that did not correctly match the existing Django project structure. The team reviewed the generated code, identified the incompatibility, and modified the implementation so that it integrated correctly with the application's models, URLs, templates, and existing project configuration.

This section will be updated with a specific example from the actual development process before final submission.

---

## Human Team Decisions

Although AI tools assist with development, project decisions are made by the team.

Important human decisions include:

* Selecting the Expense Tracker as the project
* Determining the application's minimum viable product
* Deciding which features are necessary for the prototype
* Prioritizing functionality based on the project deadline
* Evaluating whether AI-generated suggestions are appropriate
* Determining the final design and user experience
* Deciding when features should be simplified, changed, or removed

The team remains responsible for understanding, testing, and maintaining the software produced during the project.

---

# Existing Project Foundation

The Expense Tracker was initialized using an existing Django project foundation previously developed by a team member.

Reusable infrastructure such as portions of the Django configuration, user-account functionality, shared templates, development configuration, and deployment setup may originate from that existing foundation.

The Expense Tracker's financial functionality, user interface modifications, project requirements, and project-specific features are being adapted and developed for the CMPE 165 project.

This distinction helps document which infrastructure already existed and which functionality was developed specifically for this project.

---

# Testing

The project should be tested for the application's primary workflows, including:

* Creating a transaction
* Editing a transaction
* Deleting a transaction
* Creating categories
* Creating budgets
* Calculating totals
* Displaying dashboard information
* User authentication
* Preventing one user from accessing another user's financial information

Testing may include both automated Django tests and manual testing of the user interface.

---

# Privacy and Security

Because the application manages personal financial information, privacy is an important project consideration.

The prototype should ensure that:

* Users must authentic
