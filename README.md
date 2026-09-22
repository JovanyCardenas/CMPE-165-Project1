# Expense Tracker

> **SJSU CMPE 165 — Software Engineering Process Management**  
> **Project 1: Software Product from Idea to Execution**

Expense Tracker is a Django-based personal finance web application that helps users record income and expenses, organize transactions, create monthly category budgets, and understand their financial activity through a dashboard and reports.

The project was built as a working prototype for CMPE 165 with a focus on delivering a small but complete software product within a limited development window. In addition to the application itself, the project demonstrates software project-management concepts such as scope selection, stakeholder needs, financial analysis, risk, decision making, testing, and project evaluation.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem](#problem)
- [Project Objective](#project-objective)
- [Implemented Features](#implemented-features)
- [Demo Data and Management Commands](#demo-data-and-management-commands)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Running the Project Locally](#running-the-project-locally)
- [Running with Docker](#running-with-docker)
- [Testing](#testing)
- [AI-Assisted Development](#ai-assisted-development)
- [Existing Project Foundation](#existing-project-foundation)
- [Privacy and Security](#privacy-and-security)
- [Future Enhancements](#future-enhancements)
- [Team Members](#team-members)

---

# Project Overview

Expense Tracker provides a centralized place for a user to:

- Record income and expenses
- Organize transactions into categories
- Search and filter financial history
- Create monthly category budgets
- Compare budgeted amounts with actual spending
- View current financial totals on a dashboard
- Review monthly reports and spending breakdowns
- Manage personal categories
- Keep financial data isolated between user accounts

The prototype intentionally focuses on practical expense-tracking workflows rather than attempting to provide banking, investment, or other advanced financial services.

---

# Problem

People make purchases across many categories throughout the month, but it can be difficult to understand where their money is going without consistently recording and organizing their financial activity.

Expenses may include:

- Food and dining
- Housing
- Transportation
- Utilities
- Shopping
- Entertainment
- Subscriptions
- Education
- Health
- Other everyday purchases

Without an organized system, users may have difficulty answering questions such as:

- How much did I spend this month?
- How does my income compare with my expenses?
- Which categories account for most of my spending?
- Am I staying within the budgets I created?
- How much money remains in my monthly budget?
- What were my largest expenses?

Expense Tracker is designed to make those questions easier to answer.

---

# Project Objective

The objective of the project is to build a simple, usable, and testable financial-tracking prototype that allows users to manage their own financial records while keeping the project scope achievable.

The minimum viable product centers on four meaningful areas:

1. **Transaction management**
2. **Category and budget management**
3. **Financial dashboard calculations**
4. **Monthly reports and spending insights**

---

# Implemented Features

## Transaction Management

Authenticated users can create, view, edit, and delete transactions.

Each transaction can contain:

- Description
- Amount
- Transaction type: income or expense
- Category
- Date
- Notes

All transaction queries are scoped to the currently authenticated user so one user cannot access another user's financial records.

---

## Transaction Search and Filtering

The transaction history can be filtered by:

- Search text
- Transaction type
- Category
- Month

The page also calculates totals for the currently filtered income and expenses.

---

## Expense Categories

Users can manage their own categories.

The application includes common category types such as:

- Food
- Housing
- Transportation
- Utilities
- Shopping
- Entertainment
- Subscriptions
- Health
- Education
- Other

Users can also create, edit, and remove their own categories.

Category deletion is handled safely:

- Transactions can remain in the system with no category assigned.
- Categories that are still used by budgets are protected from deletion.

---

## Budget Tracking

Users can create a monthly budget for a category.

For each budget, the application calculates:

- Budget amount
- Amount spent
- Amount remaining
- Percentage of budget used

Duplicate budgets for the same user, category, and month are prevented both by application validation and a database constraint.

---

## Financial Dashboard

The dashboard provides a quick overview of the user's finances.

Current dashboard information includes:

- Overall balance
- Current-month income
- Current-month expenses
- Current-month budget total
- Remaining budget
- Budget usage percentage
- Spending by category
- Recent transactions

The dashboard calculations use only the current user's records.

---

## Reports and Insights

The Reports page provides month-based financial summaries.

Users can select a month and review:

- Total income
- Total expenses
- Net cash flow
- Savings rate
- Largest expense
- Number of transactions
- Expense totals by category

Category data is also prepared for visual chart display.

---

## User Accounts and Profiles

The project includes authentication and account functionality such as:

- User registration
- Login and logout
- Profile page
- Edit profile
- Password change

Financial data is associated with the authenticated user.

---

## Staff and Administrative Tools

The project retains reusable Django administration infrastructure.

Staff functionality includes:

- Django Admin access
- Administrative views for categories, transactions, and budgets
- Feature-toggle infrastructure
- Staff/admin utility pages
- Search and filtering in Django Admin

The project also contains feature flags for current and future functionality so selected features can be enabled or disabled without removing their code.

---

# Demo Data and Management Commands

The project includes Django management commands to make development, demonstration, testing, and data inspection easier.

## Seed Demo Data

Create a demo user with categories, budgets, and realistic financial activity:

```bash
python manage.py seed_demo_data
```

Reset and regenerate the demo financial data:

```bash
python manage.py seed_demo_data --reset
```

Default local demo credentials:

```text
Username: demo
Password: Demo12345!
```

> The demo credentials are intended only for local development and classroom demonstration. They should not be used as production credentials.

---

## Generate Historical Sample Transactions

Generate several months of deterministic sample transaction history:

```bash
python manage.py generate_sample_transactions demo --months 6
```

Reset previously generated sample history before recreating it:

```bash
python manage.py generate_sample_transactions demo --months 6 --reset
```

This command is useful for demonstrating month filtering and financial reports without manually entering dozens of records.

---

## Clear Demo Data

Remove generated demo financial data while preserving the demo user:

```bash
python manage.py clear_demo_data
```

Delete the complete demo account and its associated data:

```bash
python manage.py clear_demo_data --delete-user
```

---

## Expense Summary

Display a user's current-month summary from the command line:

```bash
python manage.py expense_summary demo
```

Display all-time totals:

```bash
python manage.py expense_summary demo --all-time
```

---

## Data Integrity Check

Run Expense Tracker-specific integrity checks:

```bash
python manage.py check_expense_tracker
```

The command checks conditions such as:

- Non-positive transaction amounts
- Non-positive budget amounts
- Duplicate monthly budgets
- Transaction/category ownership mismatches
- Budget/category ownership mismatches

---

## Export Expense Data

Export a user's data to CSV:

```bash
python manage.py export_expense_data demo
```

Export as JSON:

```bash
python manage.py export_expense_data demo --format json
```

Export a specific month:

```bash
python manage.py export_expense_data demo --month 2026-09
```

A custom output directory can also be supplied:

```bash
python manage.py export_expense_data demo --output tmp/expense_exports
```

Generated exports should remain out of version control because they may contain financial information.

Recommended `.gitignore` entry:

```gitignore
exports/
```

---

# Technology Stack

| Area | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Local Database | SQLite |
| Version Control | Git, GitHub |
| Testing | Django TestCase / Django test runner |
| Optional Deployment Infrastructure | PostgreSQL, Render, Gunicorn, WhiteNoise |
| Containerization | Docker |

SQLite is used for local development. PostgreSQL can be used in a deployed environment.

---

# Project Structure

A simplified project structure is shown below:

```text
CMPE-165-Project1/
│
├── accounts/
│   ├── forms.py
│   ├── urls.py
│   └── views.py
│
├── core/
│   ├── context_processors.py
│   ├── middleware.py
│   ├── models.py
│   └── views.py
│
├── expenses/
│   ├── management/
│   │   └── commands/
│   │       ├── check_expense_tracker.py
│   │       ├── clear_demo_data.py
│   │       ├── expense_summary.py
│   │       ├── export_expense_data.py
│   │       ├── generate_sample_transactions.py
│   │       └── seed_demo_data.py
│   │
│   ├── tests/
│   │   ├── test_budgets.py
│   │   ├── test_categories.py
│   │   ├── test_dashboard.py
│   │   ├── test_models.py
│   │   └── test_transactions.py
│   │
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
│
├── templates/
│   ├── accounts/
│   ├── expenses/
│   └── partials/
│
├── static/
├── manage.py
├── requirements.txt
├── README.md
└── .env.example
```

The exact structure may vary slightly as the project is finalized.

---

# Running the Project Locally

## 1. Clone the Repository

```bash
git clone <repository-url>
cd CMPE-165-Project1
```

Replace `<repository-url>` with the actual GitHub repository URL.

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

If the project uses environment variables, create a `.env` file using `.env.example` as a reference.

Do not commit secrets or production credentials to GitHub.

---

## 5. Apply Database Migrations

```bash
python manage.py migrate
```

---

## 6. Optional: Create an Administrator

```bash
python manage.py createsuperuser
```

---

## 7. Optional: Load Demo Data

```bash
python manage.py seed_demo_data --reset
python manage.py generate_sample_transactions demo --months 6 --reset
```

---

## 8. Start the Development Server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

---

# Running with Docker

If Docker is configured for the project:

```bash
docker compose up --build
```

Apply migrations:

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

# Testing

The project uses Django's automated test framework for model, view, calculation, security, and ownership behavior.

Run the entire Django test suite:

```bash
python manage.py test
```

Run only the Expense Tracker tests:

```bash
python manage.py test expenses
```

Run an individual test module:

```bash
python manage.py test expenses.tests.test_transactions
```

The automated tests cover areas such as:

- Model creation and constraints
- Transaction CRUD operations
- Category CRUD operations
- Budget CRUD operations
- Duplicate-budget protection
- Budget spending calculations
- Authentication requirements
- User-data isolation
- Dashboard financial calculations
- Category spending calculations
- Recent transaction behavior

In addition to automated testing, the application should be manually checked through the complete user workflow before submission.

Recommended final verification:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

---

# AI-Assisted Development

Generative AI was used as a development assistant during the project. AI output was treated as draft material and reviewed, tested, and modified before being incorporated into the application.

## AI Tools Used

- **ChatGPT** — brainstorming, implementation assistance, debugging, code review, testing ideas, UI refinement, and documentation

---

## How AI Assisted the Project

AI assistance was used for tasks including:

- Reviewing the project requirements and narrowing the prototype scope
- Brainstorming Django application architecture
- Drafting portions of forms, views, templates, and tests
- Troubleshooting Django configuration and template errors
- Reviewing user-data isolation and ownership checks
- Improving Tailwind CSS layouts
- Suggesting test cases and edge cases
- Building development-oriented management commands
- Reviewing and improving project documentation

AI-generated suggestions were not accepted automatically. Changes were reviewed against the existing project structure and tested before being kept.

---

## Example of AI-Generated Code That Required Modification

A significant example occurred while developing the automated test suite for the budget system.

AI was used to help generate Django tests for budget creation, editing, deletion, user isolation, and spending calculations. When the initial tests were executed, seven tests produced errors.

Several of the AI-generated tests incorrectly assumed that the budget list view returned a template context variable named `budgets`. After reviewing the existing view, the team determined that the application actually returns `budget_data`, which contains each budget together with calculated values such as the amount spent, amount remaining, and percentage of the budget used.

Instead of changing the working application to match the AI-generated assumptions, the tests were revised to match the actual design of the application.

The same test run also revealed a separate, legitimate application problem: attempting to create a duplicate budget for the same category and month could reach the database uniqueness constraint and raise an `IntegrityError`. Unlike the incorrect test assumptions, this represented a real edge case in the application. The budget creation and editing logic was updated to detect duplicates before saving and display a normal validation error to the user.

After these changes, the Expense Tracker test suite successfully passed all tests.

This experience demonstrated that AI-generated tests and code still required human review. Test failures had to be investigated individually to determine whether the problem was in the application or in the AI-generated test itself, rather than modifying code simply to make the tests pass.

---

## Important Human Decisions

The team remained responsible for product and engineering decisions.

Important decisions made by the developers included:

- Selecting Expense Tracker as the software product
- Defining the minimum viable product around transactions, categories, budgets, dashboard calculations, and reports
- Reusing useful Django infrastructure from an existing project instead of rebuilding authentication and shared infrastructure from scratch
- Replacing other application-specific functionality from the reused foundation
- Keeping advanced ideas such as bank integration, receipt processing, recurring transactions, and AI recommendations outside the initial prototype scope
- Choosing explicit user ownership checks so financial records remain private between accounts
- Deciding which AI-generated suggestions fit the existing codebase
- Testing generated code and changing it when it did not behave correctly

AI supported development, but final implementation choices, testing, scope decisions, and responsibility for the software remained with the human developers.

---

# Existing Project Foundation

Expense Tracker was initialized from an existing Django project foundation previously developed by a team member.

Reusable infrastructure included portions of:

- Django configuration
- Authentication and account handling
- Shared base templates and navigation structure
- Staff/admin infrastructure
- Feature-toggle infrastructure
- Development and deployment configuration

The foundation originally supported a different application concept. For the CMPE 165 project, application-specific functionality was replaced or adapted for Expense Tracker.

Expense Tracker-specific work includes the financial data models, transaction workflow, categories, budgets, financial calculations, dashboard, reports, tests, management commands, and user-interface changes.

Documenting this distinction makes clear which reusable infrastructure existed before the project and which functionality was created or adapted specifically for CMPE 165.

---

# Privacy and Security

Because the application stores personal financial information, user isolation is an important design requirement.

The prototype includes the following protections:

- Authentication is required for financial pages.
- Transactions are filtered by the authenticated user.
- Categories are filtered by the authenticated user.
- Budgets are filtered by the authenticated user.
- Edit and delete operations verify ownership.
- One user cannot edit or delete another user's financial records through normal application routes.
- Automated tests verify several cross-user access restrictions.
- Exported financial data should not be committed to version control.
- Secrets and production credentials should not be stored directly in the repository.

This is an academic prototype and should not be treated as a production banking or financial-services system.

---

# Future Enhancements

The current version focuses on the required prototype scope. Possible future work includes:

- Recurring transactions
- Savings goals
- Receipt uploads
- CSV import through the web interface
- User-facing data export
- Spending trend analysis across multiple months
- Budget warnings and notifications
- Debt tracking
- Shared household expenses
- Bank account integration
- Mobile/PWA notifications
- Additional visual reports
- AI-assisted financial insights

These features are intentionally outside the initial minimum viable product unless separately implemented.

---

# Team Members

Update this section with the final CMPE 165 team roster before submission.

- Jovany Cardenas Vargas
- Gagandeep Singh

---

# Course

**San José State University**  
**CMPE 165 — Software Engineering Process Management**  
**Project 1: Software Product from Idea to Execution**

---

## Disclaimer

Expense Tracker is an academic software prototype created for coursework. It is not a bank, accounting platform, financial advisor, or production financial service.
