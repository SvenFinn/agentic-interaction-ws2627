# Exercise 2: Wizard of Oz and the Delegation Boundary

## Delegation Boundary

| Action                                            | Decision | Justification                                                                                                    |
| ------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------- |
| 1. Read the appointments of a day                 | alone    | Reading appointments does not modify any information or affect other parties.                                    |
| 2. Look up the weather                            | alone    | Looking up weather information does not modify any data or affect others.                                        |
| 3. Search train connections                       | alone    | Searching for train connections is a read-only operation without any commitments.                                |
| 4. Read notes                                     | alone    | Reading existing notes does not modify their contents.                                                           |
| 5. Create a personal calendar block               | approval | The user should decide whether a particular time should be blocked in their calendar.                            |
| 6. Reschedule an appointment with other attendees | approval | Rescheduling affects other attendees, and the user may have additional context that the agent lacks.             |
| 7. Book a train ticket                            | approval | Booking involves a financial commitment, so the user should make the final decision.                             |
| 8. Send a message to third parties                | approval | Sending a message communicates on behalf of the user and may have consequences that the agent cannot anticipate. |
| 9. Create a note                                  | approval | Creating a note modifies the user's information, and the user should control what is stored.                     |
| 10. Delete a note                                 | approval | Deleting a note might result in the loss of important information, so the user should approve it beforehand.     |

## Rule

The agent may independently perform read-only actions that do not change any data, but must request approval before modifying information, making commitments, spending money, or interacting with third parties.

## Observations

- Asking for approval before performing actions slows the process down, so it is important to find a balance between autonomy and user control. If the agent has to ask for approval for every read-only action, it may become inefficient and frustrating for the user.
- For actions such as "clean up my notes", the agent should ask for approval, as the task is very broad and may have unintended consequences. The user should be able to specify what they want to be cleaned up and how. The contents of the notes may also not contain the entire context of the user's intentions, so the user should have the final say in what is deleted or modified.
