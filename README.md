# Shopkeepers

*Developed by Ibrahim Kimotho*

## It's a helper app for vendors who already have a physical shop - to expand their horizon beyond the limits

_____
**Architecture**
The app in made with KivyMD/Kivy and stores access token in sqlite3 within the users app.

Its backend *Flask API* is served on a linux server with ufw firewalling, nginx reverse proxy and talking to a mysql database

**The Back-end API**
Create an account to be furnished with an access token that you'll need for all other endpoints.
Supply the AUTHORIZATION header with every request, "AUTHORIZATION": BEARER <acces-token>

*The end-points:*
- /craete_ac - create a new user
- /products - retrieve all products
- /upload - for photo uploads
- /login - validate registerd users
- /refresh - renew expired access token
- /craete_item upload new stock item
