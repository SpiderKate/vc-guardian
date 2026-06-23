# Privacy Policy for VC Guardian Bot

## 1. Data Collection
This bot collects only the minimum data required to function:

- Voice channel member count
- Voice activity state (whether the VC is empty or not)
- Streak start time (when VC activity begins)
- Longest streak duration
- Temporary warning flags (e.g. 1 or 2 users remaining)

This data is stored locally in a `state.json` file on the host machine.

---

## 2. Data We Do NOT Collect
This bot does NOT collect:

- Message content from users
- Private messages
- Email addresses
- Passwords or login credentials
- IP addresses
- Personal data outside Discord user IDs used for VC tracking

---

## 3. How Data Is Used
All stored data is used only for:

- Tracking voice channel activity streaks
- Providing VC statistics via slash commands
- Sending alerts when VC participant count changes

---

## 4. Data Storage
- Data is stored locally in a JSON file (`state.json`)
- No external database or third-party storage is used
- Data is not shared or sold

---

## 5. User Rights
Users may request:
- Reset of VC statistics
- Removal from tracking (if supported by server admin configuration)

Contact the server administrator or bot owner for requests.

---

## 6. Contact
For questions about this policy, contact the bot owner via Discord.