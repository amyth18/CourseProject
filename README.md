# Our Main Functional Goal(s)
In spite of the advent of many communication tools e.g. social media, slack etc., emails still continues to occupy an important position in one's communiation tool chest. The main goal of this project code names "Maximus", was to perform topic modelling on a user's Inbox (Gmail) and assign topics to each email. We belive this would help users in dealing with a deluge of emails they recieve every day/month by summarizing the main topics dicovered in their Inbox (e.s.p the unread emails) and help them focus on the most important emails that they are most interested.

# Related Documents
* Project Proposal [Project Proposal.pdf](https://github.com/amyth18/CourseProject/blob/main/CS410%20Project%20Proposal.pdf)
* Progress Report [CS410 Project Progress Report.pdf](https://github.com/amyth18/CourseProject/blob/main/CS410%20Project%20Progress%20Report.pdf)

# Team Members

# What did we accomplish?
We were able to build a basic WebApp (dockerized python based Flask application) that downloads emails from a user's Gmail Inbox 
and discovers the latent topics in the email corpus. We used the LDA implementation from Gensim package for topic modelling. 
We were also able to discover topic coverage for each email in the Inbox and were able to asociate topic label(s) to each email. 
We built dashboard (using ReactJS) to display the topics and number of emails associated with each topic.

[TBD insert image of dashboard]

# Installation and User Guide
There are 2 ways to install and use the application.

### Local Install (personal instance)
1. The application can be installed locally on your laptop/deskop (or a VM in the cloud). 
2. To install the application you will need Docker installed on your machine. If you dont already have docker installed, please visit [this site](https://docs.docker.com/get-docker/) to install docker for your OS.
3.  Clone this git repository
4.  cd into ```source/``` folder and run the command ```docker-compose up```. This should bring up the application.
5.  The application can be accessed at url ```http://localhost:8080```

### Or, Use our Cloud Instance
1. If you do not want to run locally or have run into issues, you can choose to access the application hosted at ```http://tbd:8080```
2. In this mode you directly start from step#5 above.

### Getting Started with Topic Discovery
1. Now for the fun part. To discover latent topics in your Gmail Inbox (only Gmail for now) you will have to authorize the app to read emails from your Inbox. Don't panic! we are not going to read all your email :-). Instead, We ask you add a label called ```cs410``` for emails that you are OK with app accessing it e.g. spam mail, promotions etc. We ONLY read emails tagged ```cs410``` from your inbox, if you have not tagged anything we read zero emails.
2. This is not much of an issue when running the app locally on our computer (data is in our computer, just like your any other desktop email client) as much as it is when using cloud instance.
3. If you want to play it absolutely safe (understandably so), you can use the "test" gmail account we have setup (id: amythcloud@gmail.com, password:?) with some pre-seeded emails.
4. Hitting the url first time will automatically direct you to Google to get your authorization for accessing your inbox. [handle issue with test account, give access to amythcloud?]
5. Once authorization is successful, you can hit the ```Sync Emails``` at the top right corner and hit ```Sync``` on the popped dialog and wait for spinner to stop. In case of error(s) a red badge appears on the button, click on the button to open the same dialog again to know the cause. The sync may take time depending on emails and network speed. The blue badge shows total cound of downloaded message.
7. Once ```Sync Email``` button show green tick mark, hit the ```Analyze``` button to discover topics. Again wait still the spinner stops and a green tick mark appears on the ```Analyze Emails``` button.
8. Once you see a green tick mark on the ```Analyze Emails``` button, refresh the page to see all the topics discovered in our Inbox :-).

# Software Design and Implementation Details

# Challenges

# Future Work
