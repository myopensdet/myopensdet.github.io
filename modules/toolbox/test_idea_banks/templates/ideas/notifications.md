<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Notifications: test ideas

Email, SMS, push and in-app messages. Use a test inbox or a fake email server, never real customers.

## Works as it should

- Each event sends its notification: order placed, shipped, password changed
- The right person gets it, with their name, the right links and the right language
- Links in the message open the right page, also on a phone
- Turning a notification type off in settings stops it; on starts it again

## Refuses bad input

- A user with no email or phone number: no error, and the event still completes
- An email address that bounces: it's recorded, and not tried forever

## Edges and limits

- Many events at once: grouped, or one message each, as the rule says
- The same event twice: the message is sent once
- Quiet hours and time zones: a message planned for 9:00 arrives at 9:00 for the user
- Very long names or content: the message still looks right
- A user who unsubscribed gets only what they must (like password resets)

## Security

- No password, full card number or secret in any message
- A message never goes to another customer (check with two test users)
- Unsubscribe links work without logging in, but only for that user

## People, devices and failures

- The email service is down: messages wait and are sent later, the app keeps working
- Emails look right in common email apps, and with images turned off
- Push notifications on a locked phone, and after the app was closed
