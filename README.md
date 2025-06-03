# Automated Savings System 

## Overview 
The Automated Savings System is an SQL-based financial web application designed to help users manage their personal finances more efficiently. The platform enables users to automate savings, track daily transactions, set personalized financial goals, and gain insights into their financial habits through analytics.

The platform uses PostgreSQL as the core database system, storing structured data such as user profiles,
transaction logs, savings goals, and rule configurations. The backend is developed using Python (Flask),
which processes user requests and handles all the logic, such as handling routes, processing input, and
applying savings rules. The frontend is built with HTML and CSS, providing a user interface for entering
user details, adding transactions and setting savings goals and rules.

## Features
- **User Signup & Login:** Simple registration with name, email, and bank balance
- **Track Transactions:** Log everyday transactions like groceries or bills.
- **Set Savings Goals:** Create goals like vacation, emergency fund, etc.
- **Create Savings Rules:** Automatic savings rules like Round-Up, Fixed, or Percentage-based saving.
- **Track Progress:** Visualize the progress of savings goals.
- **Analytics:** An analytics section that uses user data to track spending patterns, monitor savings
growth and predict future trends.

## System Architecture
#### Technologies Used:
- **Frontend:** HTML, CSS
- **Backend:** Python (Flask)
- **Database:** PostgreSQL

#### Architecture Overview:
- User ↔ Flask App ↔ PostgreSQL Database
  - User inputs are processed by the Flask backend and stored in the database.
  - Data is retrieved and displayed in the frontend dynamically
 
  ### Authors:
  - Eva Mukherjee
  - Maria Joseph
