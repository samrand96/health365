# Requirements Guideline

## Task Overview

We have prepared a specific task designed to assess your skills in software development, particularly with Python, FastAPI, SocketIO, and Tortoise ORM. If you are not familiar with FastAPI or Tortoise ORM, please do not worry; the goal of
this exercise is to see how you adapt to new technologies and implement them in a project.

----------------
## Setup

Create a new GitHub repository for this task.

----------------
## Requirements

- Token-based Authentication: Implement token-based authentication for both FastAPI and SocketIO. 
- Users should be able to register and log in using the FastAPI routes, receiving
JWT tokens upon successful authentication. 
- Secure the SocketIO connection using these tokens to ensure only authenticated users can access real-time features. 
- Advanced User Interaction and Notifications: Create a multi-role system with user roles like Secretary, Doctor, and Laboratory. Implement relationships between
users with different roles using Tortoise ORM. 
`Users: id, username, role`
- Relationships: Create a system where doctors can send patient information to other doctors. A doctor should be able to select a patient, input information, and send it to another doctor.

### Instructions:
- Design and implement user roles (Secretary, Doctor, Laboratory) using Tortoise ORM.
- Allow doctors to send patient information to other doctors. Each patient record should include patient details and medical information.
- Implement a notification system to alert doctors when they receive patient information from other doctors.
- Ensure secure access and data privacy for patient information. 

----------------
## Code Quality:

Please ensure your code is clean, well-organized, and documented. We value readability and maintainability. 

----------------
## Submission:

Once completed, please push your code to your GitHub repository and send us the link.

------------------
## Resources

- FastAPI Documentation: 
https://fastapi.tiangolo.com

- Tortoise ORM Documentation: 
https://tortoise.github.io
