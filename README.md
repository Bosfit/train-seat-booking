# Train Seat Booking App: Reserve your train seats with ease

Train Seat Booking is a simple web application built with Python, Django, HTML, CSS, and JavaScript. It helps users browse available train trips, choose their seats, and complete bookings in a clear step-by-step flow.

---

## Contents

- [Project Goals](#project-goals)
- [Target User](#target-user)
- [User Stories](#user-stories)
- [MoSCoW Priorities](#moscow-priorities)
- [Simple Agile Board](#simple-agile-board)

---

## Project Goals

- Build a beginner-friendly train booking website with clear navigation and simple forms.
- Allow users to register, log in, and manage their own bookings safely.
- Support a complete booking flow from selecting a trip to making a test payment.
- Provide clear success and error messages so users always know what is happening.
- Keep the design responsive so the site works on mobile, tablet, and desktop.

---

## Target User

- People who want a quick and easy way to reserve train seats online.
- Users who prefer a simple booking process without confusing steps.
- Learners and assessors (for portfolio review) who need to see clear CRUD and payment features.

---

## User Stories

- As a visitor, I want to view available train trips so that I can decide what to book.
- As a user, I want to create an account so that I can save and manage my bookings.
- As a logged-in user, I want to create a booking so that I can reserve seats on a trip.
- As a logged-in user, I want to view my bookings so that I can check my trip details.
- As a logged-in user, I want to edit or cancel my own booking so that I can fix mistakes.
- As a logged-in user, I want to pay for an unpaid booking so that I can confirm my reservation.
- As a logged-in user, I want paid-only access to my ticket page so that unpaid bookings stay restricted.

---

## MoSCoW Priorities

### Must Have

- User registration, login, and logout.
- Train trip and booking models.
- Booking CRUD (create, read, update, delete) with ownership checks.
- Stripe test checkout for unpaid bookings.
- Paid status update after successful checkout.

### Should Have

- Helpful validation and user feedback messages.
- Paid-only ticket view.
- Mobile-friendly layout and navigation.

### Could Have

- Extra booking filters (e.g. by date or destination).
- Better profile page for account details.
- More UI polish and animations.

### Won't Have (for this release)

- Live train API integration.
- Real production payments (test mode only).
- Seat map visualisation with real-time seat locking.

---

## Simple Agile Board

### To Do

- Build base templates (`base.html`, navbar, messages).
- Add booking forms and booking list/detail pages.
- Add Stripe checkout flow and success/cancel pages.
- Add paid-only ticket page.
- Complete testing and deployment checks.

### Doing

- Set up project structure and app routing (`accounts`, `bookings`, `payments`).

### Done

- Create Django project.
- Create 3 apps: `accounts`, `bookings`, `payments`.
- Connect app URLs in project URL config.
