# Asiimov

A free, intuitive, open source CS:GO item trading platform.

## Goals

- (done) You can authenticate with your steam account
- Site gets your items automatically on the press of a button
- You can create 'offers' using your items as a base
- A border colour indicates if the item is still in your inventory
- You can manually renew an offer page to check if the item is still in the inventory
- You can send trade offers (preferably with the items preselected or even completely automated)
- You have a profile with some badges to get your profile semi verified (email, trade link...)
- Everything is available for free
- Items should be displayed with: Item ID, Inspect Link, Pattern Index (...) NO PRICES! We don't want to anger Valve!
- Simple user design, minimalistic, less pages more features
- (optional) You can mark your inventory items as "for trade" or "holding on to this"

Additional features and goals will be tracked in this repositories issues.

## Pages

- Home Page (w/ live feed of created offers)
- `/offer/<offerID>` - Offer page (for each offer)
- `/offer/<offerID>/refresh` - Refreshes offer page
- `/profile/<steamID>` - Profile page for badges, confirmed trades (...)
- `/profile/<steamID>/inventory` - Inventory page
- `/profile/<steamID>/settings` - Personal settings
- `/search/<filter>` - Offer Search/ Filter
- `/create` - Create offer

## Setup Testing Environment

1. Clone repository
2. Set up [virtualenv](https://virtualenv.pypa.io/en/latest/)
3. Install dependencies with `pip install -r requirements.txt`
4. Migrate database scheme `python manage.py migrate`
5. Run the test server `python manage.py runserver`

## Branching

We use a pretty simple and intuitive branching structure:

- `master` - Contains deployable code where everything is tested and tagged to the latest version
- `dev` - Contains the latest version of seemingly stable code, pull requests will be collected and tested here
- `hotfix-X` - Is a branch where security or major issues are worked on, they will be merged into `master` and `dev`
- `feature-X` - Is a branch where a specific feature is worked on, will be merged into `dev`

If you fork this repository and want to help us you will most likely work in the `dev` branch and create a pull request from your `dev` to our `dev`.

## Contribution Guide

See the `CONTRIBUTING.md`
