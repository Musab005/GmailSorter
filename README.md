# Environment.yaml
In addition to running `conda env create -f environment.yaml`
do: `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`

# Motivation
1) Wanted to develop a machine learning model for a practical use case.
2) Wanted to work with Google Cloud
3) Wanted to work with REST APIs.

# Challenges
Some emails don't really belong to any label. Have to make a hard decision to make a more general label and include
different types of emails. Because to train the model need to have a large enough dataset. Worst case if confidentiality is < 95%
i will just keep it in primary inbox for manual sorting. So its a win win

# Project idea
Developing a machine learning project to sort incoming emails into appropriate folders in my gmail account.
I was tired of doing it manually and used to delay sorting new emails, and it ultimately accumulated to the backlog.

# Success metrics
Successfully sort incoming emails with >= 90% accuracy
Reduce effort of manual sorting

# Failure case
In the case where the probability of an email is <= 75 % for any folder, put it into the "Unsorted" folder.

# Sorted folders supported
- Phone
- Home internet
- Bank account
- credit account
- Job applications (Confirmation of jobs applied)
- OAs/Interview invitations
- Online deliveries
- Food deliveries
- Investments
- Car rental
- Apartment rental
- Hotel bookings
- flight bookings
- Insurance
- Unsorted (need manual sorting)

# Instructions for obtaining credentials
The file token.json stores the user's access and refresh tokens, and is
created automatically when the authorization flow completes for the first
time.

# Note
On terminal, do `git rm --cached <file_path>` to untrack the file.