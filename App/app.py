from flask import Flask, render_template, request, redirect, url_for, jsonify
from connection import get_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        balance = request.form['balance']

        conn = get_connection()
        cur = conn.cursor()

        # Create user
        cur.execute("""
            INSERT INTO Users (Name, Email, Bank_Balance)
            VALUES (%s, %s, %s)
            RETURNING User_ID
        """, (name, email, balance))
        user_id = cur.fetchone()[0]

        # Create savings account with balance 0
        cur.execute("""
            INSERT INTO Savings_Account (User_ID, Balance)
            VALUES (%s, %s)
        """, (user_id, 0.00))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('user_added', name=name, email=email, balance=balance))

    return render_template('signup.html')

@app.route('/user_added')
def user_added():
    name = request.args.get('name')
    email = request.args.get('email')
    balance = request.args.get('balance')
    return render_template('user_added.html', name=name, email=email, balance=balance)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE Name = %s", (name,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return redirect(url_for('user_dashboard', name=user[1]))
        else:
            return render_template('login.html', error="User not found!")

    return render_template('login.html')

@app.route('/user/<name>')
def user_dashboard(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM Users WHERE Name = %s", (name,))
    row = cur.fetchone()

    if row:
        user = {
            'User_ID': row[0],
            'Name': row[1],
            'Email': row[2],
            'Bank_Balance': row[3]
        }

        # Get Savings Account
        cur.execute("SELECT Account_ID FROM Savings_Account WHERE User_ID = %s", (user['User_ID'],))
        account_row = cur.fetchone()
        account_id = account_row[0] if account_row else None

        cur.close()
        conn.close()

        return render_template('user_details.html', user=user, account_id=account_id)

    cur.close()
    conn.close()
    return "User not found", 404

@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()

    # Total Users
    cur.execute("SELECT COUNT(*) FROM Users")
    total_users = cur.fetchone()[0]

    # Top 5 Savers
    cur.execute("""
       SELECT u.name as user_name, b.balance
       FROM Savings_account b
       JOIN users u ON u.user_id = b.user_id
       ORDER BY b.balance DESC
       LIMIT 5
    """)
    top_users = cur.fetchall()

    # Daily Transaction Trends (last 30 days)
    cur.execute("""
        SELECT 
            DATE_TRUNC('day', Timestamp)::date AS Day,
            SUM(CASE WHEN Type = 'Deposit' THEN Amount ELSE 0 END) AS Daily_Deposits,
            SUM(CASE WHEN Type = 'Withdrawal' THEN Amount ELSE 0 END) AS Daily_Withdrawals
        FROM Transaction
        WHERE Timestamp > NOW() - INTERVAL '30 days'
        GROUP BY Day
        ORDER BY Day
    """)
    trend_data = cur.fetchall()
    trend_dates = [row[0].strftime('%Y-%m-%d') for row in trend_data]
    deposits = [float(row[1]) for row in trend_data]
    withdrawals = [float(row[2]) for row in trend_data]

    # Inactive Accounts (no transaction in last 3 months)
    cur.execute("""
        SELECT sa.Account_ID, u.User_ID, u.Name
        FROM Savings_Account sa
        JOIN Users u ON sa.User_ID = u.User_ID
        LEFT JOIN Transaction t ON sa.Account_ID = t.Account_ID AND t.Timestamp > NOW() - INTERVAL '3 months'
        WHERE t.Transaction_ID IS NULL
    """)
    inactive_accounts = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'dashboard.html',
        total_users=total_users,
        top_users=top_users,
        trend_dates=trend_dates,
        deposits=deposits,
        withdrawals=withdrawals,
        inactive_accounts=inactive_accounts
    )

@app.route('/transactions/<int:user_id>/<int:account_id>', methods=['GET', 'POST'])
def user_transactions(user_id, account_id):
    conn = get_connection()
    cur = conn.cursor()
    error = None

    if request.method == 'POST':
        amount = float(request.form['amount'])
        txn_type = request.form['type']
        description = request.form['description']

        # Get current balance from the correct table
        cur.execute("SELECT Balance FROM Savings_Account WHERE Account_ID = %s", (account_id,))
        result = cur.fetchone()
        if result:
            balance = result[0]
        else:
            error = "Account not found"
            transactions = []
            return render_template('transactions.html', transactions=transactions, user_id=user_id, account_id=account_id, error=error)

        # Validate and insert transaction
        if txn_type == 'Withdrawal' and amount > balance:
            error = "Withdrawal exceeds current account balance!"
        else:
            cur.execute("""
                INSERT INTO Transaction (User_ID, Account_ID, Amount, Type, Description)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, account_id, amount, txn_type, description))

            # Update balance
            if txn_type == 'Deposit':
                cur.execute("UPDATE Savings_Account SET Balance = Balance + %s WHERE Account_ID = %s", (amount, account_id))
            else:
                cur.execute("UPDATE Savings_Account SET Balance = Balance - %s WHERE Account_ID = %s", (amount, account_id))

            conn.commit()

    # Always fetch latest transactions
    cur.execute("SELECT * FROM Transaction WHERE User_ID = %s ORDER BY Timestamp DESC", (user_id,))
    transactions = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('transactions.html', transactions=transactions, user_id=user_id, account_id=account_id, error=error)

@app.route('/savings_rules/<int:user_id>/<int:account_id>', methods=['GET', 'POST'])
def view_savings_rules(user_id, account_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        rule_type = request.form['rule_type']
        rule_condition = request.form['rule_condition']

        cur.execute("""
            INSERT INTO Savings_Rule (Account_ID, Rule_Type, Rule_Condition)
            VALUES (%s, %s, %s)
        """, (account_id, rule_type, rule_condition))
        conn.commit()

    cur.execute("SELECT * FROM Savings_Rule WHERE Account_ID = %s", (account_id,))
    rules = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('savings_rules.html', rules=rules, user_id=user_id, account_id=account_id)

@app.route('/toggle_rule/<int:rule_id>', methods=['POST'])
def toggle_rule(rule_id):
    new_state = request.json.get('active')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Savings_Rule SET Active = %s WHERE Rule_ID = %s", (new_state, rule_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True})

@app.route('/savings_goals/<int:user_id>/<int:account_id>', methods=['GET', 'POST'])
def view_savings_goals(user_id, account_id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        goal_name = request.form['goal_name']
        target_amount = request.form['target_amount']
        status = 'Active'

        cur.execute("""
            INSERT INTO Savings_Goal (User_ID, Goal_Name, Target_Amount, Status)
            VALUES (%s, %s, %s, %s)
        """, (user_id, goal_name, target_amount, status))
        conn.commit()

        return redirect(url_for('view_savings_goals', user_id=user_id, account_id=account_id))

    cur.execute("SELECT Goal_ID, Goal_Name, Target_Amount, Saved_Amount, Status FROM Savings_Goal WHERE User_ID = %s", (user_id,))
    goals = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('savings_goals.html', goals=goals, user_id=user_id, account_id=account_id)

if __name__ == '__main__':
    app.run(debug=True)