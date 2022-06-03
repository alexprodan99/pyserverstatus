# pyserverstatus
* You can start a local debugging smtp server by running the following command:
```
python -m smtpd -n -c DebuggingServer localhost:587
```
* In case that you want to use google smtp, you have to set up your google account credentials into a .env file.
```
SMTP_USER=<SMTP_USER>
SMTP_PASSWORD=<SMTP_PASSWORD>
```
* Email receivers must be specified into the ```receivers.json``` file.
