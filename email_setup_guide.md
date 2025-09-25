# Gmail SMTP Setup Guide for TeenBuzz

## Step 1: Enable 2-Factor Authentication on Gmail

1. Go to your Gmail account: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click "2-Step Verification"
4. Follow the prompts to enable 2FA

## Step 2: Generate App Password

1. Go back to "Security" settings
2. Under "Signing in to Google", click "App passwords"
3. Select "Mail" as the app
4. Select "Other" as the device and type "TeenBuzz App"
5. Click "Generate"
6. Copy the 16-character password (it will look like: abcd efgh ijkl mnop)

## Step 3: Configure Environment Variables

Create a `.env` file in your TeenBuzz directory with:

```
EMAIL_PASSWORD=your-16-character-app-password-here
```

## Step 4: Test Email Connection

Run the test script to verify everything works:

```bash
python test_email.py
```

## Important Notes

- **Never use your regular Gmail password** - always use the App Password
- **Keep the App Password secure** - don't commit it to version control
- **The App Password is 16 characters** with spaces (remove spaces when using)
- **If you change your Gmail password**, you'll need to generate a new App Password

## Troubleshooting

### "Authentication failed" error:
- Make sure 2FA is enabled on your Gmail account
- Verify you're using the App Password, not your regular password
- Check that the App Password doesn't have spaces

### "Connection refused" error:
- Check your internet connection
- Verify Gmail SMTP settings (smtp.gmail.com, port 587)
- Make sure your firewall isn't blocking the connection

### "Less secure app access" error:
- This shouldn't happen with App Passwords
- If it does, make sure you're using the App Password correctly

