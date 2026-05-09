# Firebase Authentication Setup Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Download Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click the **gear icon** (⚙️) next to "Project Overview" → **Project settings**
3. Go to the **"Service accounts"** tab
4. Click **"Generate new private key"**
5. Save the JSON file to your project folder
6. Rename it to `firebase-service-account.json`

## Step 3: Configure Environment Variables

Edit the `.env` file in your project root:

```env
SECRET_KEY=your-secret-key-here
FIREBASE_WEB_API_KEY=AIzaSyAIScD7fHKBIquvA3MXTKbznpiPeVp9qtI
FIREBASE_CREDENTIALS=./firebase-service-account.json
SQLALCHEMY_DATABASE_URI=sqlite:///instance/app.db
```

## Step 4: Initialize Database

Since we added a new column (`firebase_uid`) to the User model, you need to recreate the database:

```bash
# Delete old database (WARNING: This deletes all data!)
Remove-Item instance/app.db

# Create new tables
python -c "from app import create_app; app=create_app(); app.app_context().push(); from app.extensions import db; db.create_all()"
```

## Step 5: Run the Application

```bash
python run.py
```

## Step 6: Test Authentication

1. Open http://localhost:5000/auth/register
2. Create a new account
3. Check Firebase Console → Authentication → Users (you should see the new user)
4. Log out and log back in

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"
→ Make sure you're running commands from the project root folder (where `run.py` is)

### Error: "Firebase credentials not found"
→ Check that `firebase-service-account.json` exists in your project folder
→ Verify the path in `.env` is correct

### Error: "Invalid API key"
→ Double-check your `FIREBASE_WEB_API_KEY` in `.env`
→ Make sure you copied the Web API Key, not the service account key

### Error: "EMAIL_EXISTS"
→ The email is already registered in Firebase
→ Use a different email or reset the password
