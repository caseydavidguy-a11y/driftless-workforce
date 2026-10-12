# Connecting the website forms (about 10 minutes, one time)

The forms save into a Google Sheet that only you can open. Every submission also lands in your email,
and resumes go to a private Google Drive folder. Nothing here costs money.

## 1. Make the sheet
1. Go to sheets.google.com while signed in as yourself and create a blank sheet.
2. Name it **Driftless website inbox**.

## 2. Add the code
1. In the sheet, open **Extensions > Apps Script**.
2. Delete what is in `Code.gs` and paste in everything from `Code.gs` (this folder).
3. Click **+** next to Files, choose **HTML**, name it `Inbox` (exactly), and paste in everything from `Inbox.html`.
4. Click **Save**.
5. In the function menu at the top, pick **setup** and click **Run**. Google will ask for permission
   (Sheets, Drive, and sending email as you). Approve it. Your four tabs appear in the sheet.

## 3. Turn on the form address (public, receives submissions)
1. Click **Deploy > New deployment**, gear icon > **Web app**.
2. Description: `Forms`. Execute as: **Me**. Who has access: **Anyone**.
3. Click **Deploy** and copy the **Web app URL**. Send it to Claude. It goes into the website.

## 4. Turn on your private inbox (the back door)
1. Click **Deploy > New deployment** again, **Web app**.
2. Description: `Inbox`. Execute as: **Me**. Who has access: **Only myself**.
3. Deploy, copy that URL and bookmark it. That is your inbox. Send it to Claude too and it
   becomes the **Staff sign-in** link at the bottom of the website. Anyone else who clicks it
   is asked to sign in to Google and is turned away.
4. Optional: in Apps Script, **Project Settings > Script properties**, add `INBOX_URL` = that address,
   so the email alerts link straight to it.

You can also open the inbox from the sheet itself: **Driftless > Open inbox**.

## What is protected, and how
- Only you can open the sheet, the resume folder and the inbox. They live in your Google account.
- The public form address can only add new rows. It cannot read anything back.
- Spam: a hidden trap field, a too-fast check and a limit of 30 submissions a minute.
- Text that looks like a spreadsheet formula is stored as plain text.
- Resumes: PDF or Word only, 5 MB at most.

## If you change the forms
Ask Claude. The website and this code are built from the same list of fields, so they stay in step.
After a change, paste the new `Code.gs` and use **Deploy > Manage deployments > Edit > New version**
on both deployments (the addresses stay the same).
