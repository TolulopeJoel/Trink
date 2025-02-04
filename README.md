# Trink - AI Budget Manager

Trink is an AI-powered budget manager that helps users track spending, set financial goals, and gain personalized insights to improve financial habits.

## Features
- **Bank Account Integration**: Securely link bank accounts for real-time tracking.
- **AI-Powered Categorization**: Automatically classify transactions.
- **Financial Insights**: Get smart recommendations based on spending patterns.
- **Goal Tracking**: Set savings goals and monitor progress.
- **Automated Budgeting**: Generate and adjust budgets based on spending behavior.


## Getting Started
### Prerequisites
- Python 3.9+
- PostgreSQL & MongoDB installed

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/trink.git
   cd trink
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Configure environment variables (e.g., database credentials, API keys).
5. Run database migrations:
   ```sh
   python manage.py migrate
   ```
6. Start the development server:
   ```sh
   python manage.py runserver
   ```

## Usage
- Upload bank statements and categorize transactions.
- Set and track financial goals.
- Get AI-driven financial insights.

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License.

---

_Stay in control of your finances with Trink!_
